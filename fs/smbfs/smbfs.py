# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import socket
import itertools

import nmb.NetBIOS
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


__all__ = ['SMBFS']


class SMBFS(FS):

    _meta = {
        'case_insensitive': True,
        'invalid_path_chars': '\0"\[]:+|<>=;?,*',
        'network': True,
        'read_only': False,
        'thread_safe': False, # FIXME: make that True
        'unicode_paths': True,
        'virtual': False,
    }

    RX_IP = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    NETBIOS = nmb.NetBIOS.NetBIOS()

    @classmethod
    def _make_info_from_shared_file(cls, shared_file, sd=None, namespaces=None):
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
                        if shared_file.isDirectory else ResourceType.file,
            }

        if 'smb' in namespaces:
            info['smb'] = {
                name: bool(shared_file.file_attributes & attr)
                    for name, attr in {
                        'archive': smb.smb_constants.ATTR_ARCHIVE,
                        'hidden': smb.smb_constants.ATTR_HIDDEN,
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
        access = {'gid': sd.group, 'uid': sd.owner}

        # Extract Access Control Entries corresponding to
        # * `everyone` (used for UNIX `others` mode)
        # * `owner` (used for UNIX `user` mode, falls back to `everyone`)
        # * `group` (used for UNIX `group` mode, falls back to `everyone`)
        other_ace = next(ace for ace in sd.dacl.aces
            if str(ace.sid).startswith(smb.security_descriptors.SID_EVERYONE))
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
        modes = {
            'u': owner_ace.mask,
            'g': group_ace.mask,
            'o': other_ace.mask,
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
        namespaces = namespaces or set()
        info = {'basic': {'name': '', 'is_dir': True}}
        if 'details' in namespaces:
            info['details'] = {'type': ResourceType.directory, 'size': 0}
        return Info(info)

    def __init__(self, host, username='guest', passwd='', timeout=15, port=445):
        super(SMBFS, self).__init__()

        if self.RX_IP.match(host):
            self._server_ip = ip = host
            response = self.NETBIOS.queryIPForName(host, timeout=timeout)
            if not response:
                raise errors.CreateFailed(
                    "could not get a name for IP: '{}'".format(host))
            self._server_name = response[0]

        else:
            self._server_name = host
            response = self.NETBIOS.queryName(host, '', timeout=timeout)
            if not response:
                raise errors.CreateFailed(
                    "could not get an IP for name: '{}'".format(host))
            self._server_ip = ip = response[0]

        self._timeout = timeout
        self._server_port = port
        self._client_name = socket.gethostname()
        self._username = username
        self._password = passwd

        self._smb = smb.SMBConnection.SMBConnection(
            self._username, self._password,
            self._client_name, self._server_name,
        )

        if not self._smb.connect(ip, port, timeout=timeout):
            raise errors.CreateFailed("could not connect to '{}'".format(host))

        self._shares = {
            share.name for share in self._smb.listShares()
                if share.type == share.DISK_TREE
        }

    def makedir(self, path, permissions=None, recreate=False):
        _path = self.validatepath(path)

        if _path in '/':
            if not recreate:
                raise errors.DirectoryExists(path)

        else:
            share, smb_path = utils.split_path(_path)

            # Check we are not creating a share
            if not smb_path and share not in self._shares:
                raise errors.Unsupported('cannot create share {}'.format(share))
            elif not smb_path and not recreate:
                raise errors.DirectoryExists(path)

            # Check parent path exists and is a directory
            if not self.getinfo(dirname(_path)).is_dir:
                raise errors.DirectoryExpected(dirname(_path))

            # Check new directory does not exist
            try:
                info = self.getinfo(_path)
            except errors.ResourceNotFound:
                self._smb.createDirectory(share, smb_path, self._timeout)
            else:
                if not (info.is_dir and recreate):
                    raise errors.DirectoryExists(path)

        return self.opendir(_path)

    def openbin(self, path, mode='r', buffering=-1, **options):
        _path = self.validatepath(path)
        _mode = Mode(mode)

        _mode.validate_bin()

        if self.exists(_path):
            if not self.isfile(path):
                raise errors.FileExpected(path)
            elif _mode.exclusive:
                raise errors.FileExists(path)
        elif not _mode.create:
            raise errors.ResourceNotFound(path)
        else:
            if self.gettype(dirname(_path)) is not ResourceType.directory:
                raise errors.FileExpected(path)

        share, smb_path = utils.split_path(_path)
        return SMBFile(self, share, smb_path, _mode)


    def listdir(self, path):
        return [f.name for f in self.scandir(path)]

    def scandir(self, path, namespaces=None, page=None):
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        iter_info = self._scanshares(namespaces) if _path in '/' \
               else self._scandir(path, namespaces)
        if page is not None:
            start, end = page
            iter_info = itertools.islice(iter_info, start, end)
        return iter_info


    def _scanshares(self, namespaces=None):
        sd = None
        if _path in '/':
            for device in self._smb.listShares():
                if device.type == device.DISK_TREE:
                    if 'access' in namespaces:
                        sd = self._smb.getSecurity(device.name, '/')
                    info = self._make_info_from_shared_file(
                        self._smb.getAttributes(device.name, '/'),
                        sd, namespaces)
                    info.raw['basic']['name'] = device.name
                    yield info

    def _scandir(self, path, namespaces=None):
        sd = None
        if self.isfile(path):
            raise errors.DirectoryExpected(path)
        elif not self.isdir(path):
            raise errors.ResourceNotFound(path)
        share, smb_path = utils.split_path(self.validatepath(path))
        for shared_file in self._smb.listPath(share, smb_path):
            if shared_file.filename not in '..':
                if 'types' in namespaces:
                    sd = self._smb.getSecurity(
                        share, join(smb_path, shared_file.filename))
                yield self._make_info_from_shared_file(
                    shared_file, sd, namespaces)

    def remove(self, path):
        _path = self.validatepath(path)

        if self.gettype(_path) is not ResourceType.file:
            raise errors.FileExpected(path)

        share, smb_path = utils.split_path(_path)
        self._smb.deleteFiles(share, smb_path)

    def removedir(self, path):
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

        self._smb.deleteDirectory(share, smb_path)

    def getinfo(self, path, namespaces=None):
        _path = self.validatepath(path)
        namespaces = namespaces or ()
        sd = None

        share, smb_path = utils.split_path(_path)

        if not share:
            return self._make_root_info(namespaces)
        elif share not in self._shares:
            raise errors.ResourceNotFound(path)

        try:
            shared_file = self._smb.getAttributes(share, smb_path)
        except smb.smb_structs.OperationFailure:
            raise errors.ResourceNotFound(path)

        if 'access' in namespaces:
            sd = self._smb.getSecurity(share, smb_path)

        info = self._make_info_from_shared_file(shared_file, sd, namespaces)
        if not smb_path:
            info.raw['basic']['name'] = share

        return info

    def setinfo(self, path, info):
        _path = self.validatepath(path)

        if not self.exists(_path):
            raise errors.ResourceNotFound(path)

        # NB: pysmb doesn't seem to support setting attributes.
