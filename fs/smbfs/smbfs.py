# coding: utf-8
"""Implementation of `SMBFS`.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import io
import itertools
import socket

import nmb.NetBIOS
import six
import smb.SMBConnection
import smb.smb_constants
import smb.security_descriptors

from .. import errors
from ..base import FS
from ..info import Info
from ..mode import Mode
from ..path import join, dirname
from ..enums import ResourceType
from ..permissions import Permissions

from . import utils
from .file import SMBFile

if six.PY2:
    casefold = unicode.lower
else:
    casefold = str.casefold


__all__ = ['SMBFS']


class SMBFS(FS):
    """A filesystem over SMB.

    Arguments:
        host (str or tuple): the IP or NetBIOS hostname of the server,
            or an (IP, hostname) tuple.
        username (str): the username to connect with. Use `None` to
            connect anonymously. **[default: None]**
        passwd (str): the password to connect with. Set to `None` to connect
            anonymously. **[default: None]**
        timeout (int): the timeout of network operations, in seconds. Used for
            both NetBIOS and SMB communications. **[default: 15]**
        port (int): the port the SMB server is listening to. Often ``139`` for
            SMB over NetBIOS, sometimes ``445`` for an SMB server over direct
            TCP. **[default: 139]**
        name_port (int): the port the NetBIOS naming service is listening on.
            **[default: 137]**
        direct_tcp (int): set to True to attempt to connect directly to the
            server using TCP instead of NetBIOS. **[default: False]**
        domain (str): the network domain to connect with, the workgroup on
            windows. Usually safe to leave as empty string **[default: '']**

    Raises:
        `fs.errors.CreateFailed`: if the filesystem could not be created.

    Example:
        >>> import fs
        >>> smb_fs = fs.open_fs('smb://SOMESERVER/share')

    """

    _meta = {
        'case_insensitive': True,
        'invalid_path_chars': '\0"\[]:+|<>=;?,*',
        'network': True,
        'read_only': False,
        'thread_safe': True,
        'unicode_paths': True,
        'virtual': False,
    }

    #: The client used to communicate with the NetBIOS naming service.
    NETBIOS = nmb.NetBIOS.NetBIOS()

    @classmethod
    def _make_info_from_shared_file(cls, shared_file, sd=None, namespaces=None):
        """Translate a `smb.base.SharedFile` object to a raw info `dict`.

        Note:
            The supported namespaces are:
            * ``access`` (using an approximative *Windows access* to
              *UNIX permissions* translation)
            * ``basic``
            * ``details``
            * ``smb`` (using the SMB file attributes)

        """
        namespaces = namespaces or ()

        info = {'basic': {
            'name': shared_file.filename,
            'is_dir': shared_file.isDirectory,
        }}

        if 'details' in namespaces:
            info['details'] = {
                'accessed': shared_file.last_access_time,
                'created': shared_file.create_time,
                'metadata_changed': shared_file.last_attr_change_time,
                'modified': shared_file.last_write_time,
                'size': shared_file.file_size,
                'type': ResourceType.directory \
                        if shared_file.isDirectory \
                        else ResourceType.file,
            }

        if 'smb' in namespaces:
            info['smb'] = {
                name: bool(shared_file.file_attributes & attr)
                    for name, attr in {
                        'archive': smb.smb_constants.ATTR_ARCHIVE,
                        'compressed': smb.smb_constants.ATTR_COMPRESSED,
                        'directory': smb.smb_constants.ATTR_DIRECTORY,
                        'encrypted': smb.smb_constants.ATTR_ENCRYPTED,
                        'hidden': smb.smb_constants.ATTR_HIDDEN,
                        'normal': smb.smb_constants.ATTR_NORMAL,
                        'not_content_indexed': \
                            smb.smb_constants.ATTR_NOT_CONTENT_INDEXED,
                        'offline': smb.smb_constants.ATTR_NOT_CONTENT_INDEXED,
                        'read_only': smb.smb_constants.ATTR_READONLY,
                        'reparse_point': smb.smb_constants.ATTR_REPARSE_POINT,
                        'sparse': smb.smb_constants.ATTR_SPARSE,
                        'system': smb.smb_constants.ATTR_SYSTEM,
                        'temporary': smb.smb_constants.ATTR_TEMPORARY,
                    }.items()
            }

        if 'access' in namespaces and sd is not None:
            info['access'] = cls._make_access_from_sd(sd)

        return Info(info)

    @classmethod
    def _make_access_from_sd(cls, sd):
        """Translate a `SecurityDescriptor` object to a raw access `dict`.

        Arguments:
            sd (smb.security_descriptors.SecurityDescriptor): the security
                descriptors obtained through SMB.

        Note:
            Since Windows (and as such, SMB) do not handle the permissions the
            way UNIX does, the permissions here are translated as such:
                * ``user`` mode is taken from the *read* / *write* / *execute*
                  access descriptors of the user owning the resource.
                * ``group`` mode is taken from the *read* / *write* / *execute*
                  access descriptors of the group owning the resource.
                * ``other`` mode uses the permissions of the **Everyone** group,
                  which means sometimes an user could be denied access to a
                  file Windows technically allows to open (since there is no
                  such thing as *other* groups in Windows).
        """
        access = {'gid': str(sd.group), 'uid': str(sd.owner)}

        # Extract Access Control Entries corresponding to
        # * `everyone` (used for UNIX `others` mode)
        # * `owner` (used for UNIX `user` mode, falls back to `everyone`)
        # * `group` (used for UNIX `group` mode, falls back to `everyone`)
        other_ace = next((ace for ace in sd.dacl.aces
            if str(ace.sid).startswith(smb.security_descriptors.SID_EVERYONE)), None)
        owner_ace = next((ace for ace in sd.dacl.aces
            if str(ace.sid).startswith(str(sd.owner))), other_ace)
        group_ace = next((ace for ace in sd.dacl.aces
            if str(ace.sid).startswith(str(sd.group))), other_ace)

        # Defines the masks used to check for the attributes
        attributes = {
            'r': smb.smb_constants.FILE_READ_DATA \
               & smb.smb_constants.FILE_READ_ATTRIBUTES,
            'w': smb.smb_constants.FILE_WRITE_DATA \
               & smb.smb_constants.FILE_WRITE_ATTRIBUTES,
            'x': smb.smb_constants.FILE_EXECUTE,
        }

        # Defines the mask used for each mode
        other_mask = other_ace.mask if other_ace is not None else 0x0
        modes = {
            'u': (owner_ace.mask if owner_ace is not None else 0x0) | other_mask,
            'g': (group_ace.mask if group_ace is not None else 0x0) | other_mask,
            'o': other_mask,
        }

        # Create the permissions from a permission list
        access['permissions'] = Permissions([
            '{}_{}'.format(mode_name, attr_name)
                for mode_name, mode_mask in modes.items()
                    for attr_name, attr_mask in attributes.items()
                        if attr_mask & mode_mask
        ])

        return access

    @classmethod
    def _make_root_info(cls, namespaces=None):
        """Create an `fs.info.Info` instance for the root directory.

        Arguments:
            namespaces (collections.Container): the namespaces to return
                info about. Only ``basic`` and a subset of ``details`` are
                supported.
        """
        namespaces = namespaces or set()
        info = {'basic': {'name': '', 'is_dir': True}}
        if 'details' in namespaces:
            info['details'] = {'type': ResourceType.directory, 'size': 0}
        return Info(info)

    def __init__(self, host, username='guest', passwd='', timeout=15,
                 port=None, name_port=137, direct_tcp=False, domain=''):  # noqa: D102
        super(SMBFS, self).__init__()

        try:
            self._server_name, self._server_ip = utils.get_hostname_and_ip(
                host, None if direct_tcp else self.NETBIOS,
                timeout=timeout,
                name_port=name_port
            )
        except Exception as exc:
            six.raise_from(
                errors.CreateFailed("could not get IP/host pair from '{}'".format(host)),
                exc
            )

        self._timeout = timeout
        self._server_port = port
        self._client_name = socket.gethostname()
        self._username = username
        self._password = passwd
        self._direct_tcp = direct_tcp
        self._domain = domain
        self._connect_kw = dict(timeout=self._timeout)
        if self._server_port is not None:
            self._connect_kw['port'] = self._server_port

        try:
            self._smb = self._new_connection()
        except (IOError, OSError) as exc:
            six.raise_from(
                errors.CreateFailed("could not connect to '{}'".format(host)),
                exc
            )

        self._shares = {
            casefold(share.name)
            for share in self._smb.listShares()
            if share.type == share.DISK_TREE
        }

    def _new_connection(self):
        con = smb.SMBConnection.SMBConnection(
            self._username,
            self._password,
            self._client_name,
            self._server_name,
            is_direct_tcp=self._direct_tcp,
            domain=self._domain,
        )
        con.connect(self._server_ip, **self._connect_kw)
        return con

    if six.PY2:

        def close(self):  # noqa: D102
            if not self.isclosed():
                if hasattr(self, "_smb"):
                    self._smb.close()
            super(SMBFS, self).close()

    else:

        def close(self): # noqa: D102
            if not self.isclosed():
                if hasattr(self, "_smb"):
                    self._smb.close()
            super().close()

    def makedir(self, path, permissions=None, recreate=False):  # noqa: D102
        _path = self.validatepath(path)

        if _path in '/':
            if not recreate:
                raise errors.DirectoryExists(path)

        else:
            share, smb_path = utils.split_path(_path)

            # Check we are not creating a share
            if not smb_path and share not in self._shares:
                raise errors.PermissionDenied(
                    'cannot create share {}'.format(share))
            elif not smb_path and not recreate:
                raise errors.DirectoryExists(path)

            # Check parent path exists and is a directory
            if not self.getinfo(dirname(_path)).is_dir:
                raise errors.DirectoryExpected(dirname(path))

            # Check new directory does not exist
            try:
                info = self.getinfo(_path)
            except errors.ResourceNotFound:
                with self.lock():
                    self._smb.createDirectory(share, smb_path, self._timeout)
            else:
                if not (info.is_dir and recreate):
                    raise errors.DirectoryExists(path)

        return self.opendir(_path)

    def openbin(self, path, mode='r', buffering=-1, **options):  # noqa: D102
        _path = self.validatepath(path)
        _mode = Mode(mode)
        _mode.validate_bin()

        # TODO: check for permissions before opening the file

        with self.lock():
            # check the file is not a folder if it exists
            if self.exists(_path):
                if not self.isfile(path):
                    raise errors.FileExpected(path)
                elif _mode.exclusive:
                    raise errors.FileExists(path)
            elif not _mode.create:
                raise errors.ResourceNotFound(path)
            else:
                if not self.getinfo(dirname(_path)).is_dir:
                    raise errors.DirectoryExpected(dirname(path))
            # open / create a new SMBFile
            share, smb_path = utils.split_path(_path)
            if not smb_path:
                raise errors.PermissionDenied("cannot open file in '/'")
            return SMBFile(self, share, smb_path, _mode)

    def listdir(self, path):  # noqa: D102
        return [f.name for f in self.scandir(path)]

    def move(self, src_path, dst_path, overwrite=False):  # noqa: D102
        _src_path = self.validatepath(src_path)
        _dst_path = self.validatepath(dst_path)

        _src_share, _src_smb_path = utils.split_path(_src_path)
        _dst_share, _dst_smb_path = utils.split_path(_dst_path)

        # Check the source exists and is a file
        with self.lock():
            if not self.getinfo(src_path).is_file:
                raise errors.FileExpected(src_path)

        # Cannot rename across shares
        if _src_share != _dst_share: # pragma: no cover
            return super(SMBFS, self).move(src_path, dst_path, overwrite=overwrite)

        # Check the parent of dst_path exists and is not a file
        if not self.getinfo(dirname(dst_path)).is_dir:
            raise errors.DirectoryExpected(dirname(dst_path))
        # Check the destination does not exist
        if self.exists(dst_path):
            if overwrite:
                self.remove(dst_path)
            else:
                raise errors.DestinationExists(dst_path)
        # Rename with PySMB
        with self.lock():
            self._smb.rename(
                _src_share,
                _src_smb_path,
                _dst_smb_path,
                timeout=self._timeout
            )

    def scandir(self, path, namespaces=None, page=None):  # noqa: D102
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        if _path in '/':
            iter_info = self._scanshares(namespaces)
        else:
            iter_info = self._scandir(path, namespaces)
        if page is not None:
            start, end = page
            iter_info = itertools.islice(iter_info, start, end)
        return iter_info

    def _get_security(self, share, path):
        try:
            with self.lock():
                return self._smb.getSecurity(share, path)
        except smb.base.NotReadyError:
            return None

    def _scanshares(self, namespaces=None):
        """Iterate over the shares in the root directory.

        Arguments:
            namespaces (collections.Container): the namespaces to fetch for
                yielded `fs.info.Info`. Supports the namespaces supported by
                `SMBFS._make_info_from_shared_file`. Defaults to ``basic``
                only.
        """
        sd = None
        with self.lock():
            devices = self._smb.listShares()
        for device in devices:
            if device.type == device.DISK_TREE:
                if 'access' in namespaces:
                    sd = self._get_security(device.name, '/')
                with self.lock():
                    attr = self._smb.getAttributes(device.name, '/')
                info = self._make_info_from_shared_file(attr, sd, namespaces)
                info.raw['basic']['name'] = device.name
                yield info

    def _scandir(self, path, namespaces=None):
        """Iterate over the resources in a directory.

        Arguments:
            path (str): the path to the directory.
            namespaces (collections.Container): the namespaces to fetch for
                yielded `fs.info.Info`. Supports the namespaces supported by
                `SMBFS._make_info_from_shared_file`. Defaults to ``basic``
                only.
        """
        sd = None
        if self.isfile(path):
            raise errors.DirectoryExpected(path)
        elif not self.isdir(path):
            raise errors.ResourceNotFound(path)
        share, smb_path = utils.split_path(self.validatepath(path))
        with self.lock():
            shared_files = self._smb.listPath(share, smb_path)
        for shared_file in shared_files:
            if shared_file.filename not in '..':
                if 'access' in namespaces:
                    sd = self._get_security(
                        share,
                        join(smb_path, shared_file.filename)
                    )
                yield self._make_info_from_shared_file(
                    shared_file, sd, namespaces)

    def remove(self, path):  # noqa: D102
        _path = self.validatepath(path)
        if not self.getinfo(_path).is_file:
            raise errors.FileExpected(path)
        share, smb_path = utils.split_path(_path)
        with self.lock():
            self._smb.deleteFiles(share, smb_path)

    def removedir(self, path):  # noqa: D102
        _path = self.validatepath(path)

        if _path in '/':
            raise errors.RemoveRootError(path)

        if not self.getinfo(path).is_dir:
            raise errors.DirectoryExpected(path)

        if next(self.scandir(path), None) is not None:
            raise errors.DirectoryNotEmpty(path)

        share, smb_path = utils.split_path(_path)
        if not smb_path:
            raise errors.PermissionDenied(
                msg="cannot remove share '{}'".format(share))

        with self.lock():
            self._smb.deleteDirectory(share, smb_path)

    def geturl(self, path, purpose='download'):  # noqa: D102
        _path = self.validatepath(path)
        if purpose != 'download':
            raise errors.NoURL(path, purpose)
        return "smb://{}@{}:{}{}".format(
            self._username, self._server_name, self._server_port, _path)

    def getinfo(self, path, namespaces=None):  # noqa: D102
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        sd = None

        share, smb_path = utils.split_path(_path)

        if not share:
            return self._make_root_info(namespaces)
        # Shares are case insensitive, however the lookup in python is not.
        # This causes issues when looking for shares that exist, albeit with
        # different casing.
        elif casefold(share) not in self._shares:
            raise errors.ResourceNotFound(path)

        try:
            with self.lock():
                shared_file = self._smb.getAttributes(share, smb_path)
        except smb.smb_structs.OperationFailure:
            raise errors.ResourceNotFound(path)

        if 'access' in namespaces:
            sd = self._get_security(share, smb_path)

        info = self._make_info_from_shared_file(shared_file, sd, namespaces)
        if not smb_path:
            info.raw['basic']['name'] = share

        return info

    def setinfo(self, path, info):  # noqa: D102
        # TODO ? pysmb doesn't seem to support setting attributes.
        _path = self.validatepath(path)
        if not self.exists(_path):
            raise errors.ResourceNotFound(path)

    def download(self, path, file, chunk_size=None, **options):
        """Copy a file from the filesystem to a file-like object.

        This method uses the `smb.SMBConnection.SMBConnection.retrieveFile`
        method without creating a new connection, which should be more
        efficient than opening and reading from a file with `openbin`.

        Arguments:
            path (str): A path on the filesystem.
            file (file-like): A file-like object open for writing in
                binary mode.
            chunk_size (int, optional): Ignored, kept for compatibility
                with the `fs.base.FS.upload` signature.

        Note that the file object ``file`` will *not* be closed by this
        method. Take care to close it after this method completes
        (ideally with a context manager).

        Example:
            >>> with open('starwars.mov', 'wb') as write_file:
            ...     my_fs.download('/movies/starwars.mov', write_file)

        """
        _path = self.validatepath(path)

        if not self.getinfo(path).is_file:
            raise errors.FileExpected(path)

        share, smb_path = utils.split_path(_path)
        with self.lock():
            self._smb.retrieveFile(share, smb_path, file, timeout=self._timeout)

    def upload(self, path, file, chunk_size=None, **options):
        """Set a file to the contents of a binary file object.

        This method uses the `smb.SMBConnection.SMBConnection.storeFile`
        method without creating a new connection, which should be more
        efficient than opening and writing to a file with `openbin`.

        Arguments:
          path (str): A path on the filesystem.
          file (io.IOBase): A file object open for reading in
              binary mode.
          chunk_size (int, optional): Ignored, kept for compatibility
              with the `fs.base.FS.download` signature.

        Raises:
          fs.errors.ResourceNotFound: If a parent directory of
              ``path`` does not exist.

        Note that the file object ``file`` will *not* be closed by this
        method. Take care to close it after this method completes
        (ideally with a context manager).

        Example:
          >>> with open('~/movies/starwars.mov', 'rb') as read_file:
          ...     my_fs.upload('starwars.mov', read_file)

        """
        _path = self.validatepath(path)

        if self.isdir(_path):
            raise errors.FileExpected(path)
        elif not self.isdir(dirname(_path)):
            raise errors.ResourceNotFound(dirname(path))

        share, smb_path = utils.split_path(_path)
        if not smb_path:
            raise errors.PermissionDenied("cannot open file in '/'")

        with self.lock():
            self._smb.storeFile(share, smb_path, file, timeout=self._timeout)

    def readbytes(self, path):  # noqa: D102
        buffer = io.BytesIO()
        self.download(path, buffer)
        return buffer.getvalue()

    def writebytes(self, path, contents):  # noqa: D102
        buffer = io.BytesIO(contents)
        self.upload(path, buffer)

    def hassyspath(self, path):  # noqa: D102
        return False
