# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import io

from .. import errors
from ..path import join
from ..enums import Seek


__all__ = ['SMBFile']


class SMBFile(io.RawIOBase):
    """A file on an SMB server.
    """

    def __init__(self, smb_fs, share, smb_path, mode):
        """Create an `SMBFile` instance.

        Arguments:
            smb_fs (SMBFS): the SMB filesystem this file is accessed from.
            share (str): the name of the share this file is located on.
            smb_path (str): the path to the resource on the share.
            mode (fs.mode.Mode): the mode the file is opened with.
        """
        self._fs = smb_fs
        self._mode = mode
        self._smb = smb_fs._smb   # TODO: clone the connection instead of using it multiple times
        self._share = share
        self._smb_path = smb_path
        self._position = self.__length_hint__() if mode.appending else 0

        if mode.truncate:
            self.truncate(0)
        elif mode.writing:
            self.write(b'')

    def __length_hint__(self):
        try:
            return self._fs.getsize(join(self._share, self._smb_path))
        except errors.ResourceNotFound:
            return 0

    def readable(self):
        return self._mode.reading

    def read(self, size=-1):
        if not self._mode.reading:
            raise IOError('File not open for reading')
        handle = io.BytesIO()
        _, bytes_read = self._smb.retrieveFileFromOffset(
            service_name=self._share, path=self._smb_path, file_obj=handle,
            offset=self._position, max_length=size, timeout=self._fs._timeout,
        )
        self._position += bytes_read
        return handle.getvalue()

    def seekable(self):
        return True

    def tell(self):
        return self._position

    def seek(self, offset, whence=Seek.set):

        if whence == Seek.set:
            if offset < 0:
                raise ValueError("Negative seek position {}".format(offset))
            self._position = offset

        elif whence == Seek.current:
            self._position = max(self._position + offset, 0)

        elif whence == Seek.end:
            if offset > 0:
                raise ValueError("Positive seek position {}".format(offset))
            self._position = max(0, self.__length_hint__() + offset)

        else:
            raise ValueError(
                "Invalid whence ({}, should be {}, {} or {})".format(
                    whence, Seek.set, Seek.current, Seek.end
                )
            )

        return self._position

    def writable(self):
        return self._mode.writing

    def write(self, data):
        if not self._mode.writing:
            raise IOError('File not open for writing')
        new_position = self._smb.storeFileFromOffset(
            service_name=self._share, path=self._smb_path,
            file_obj=io.BytesIO(data), offset=self._position, truncate=False,
            timeout=self._fs._timeout
        )
        written_bytes = new_position - self._position
        self._position = new_position
        return written_bytes

    def truncate(self, pos=None):
        pos = pos or self._position
        length = self.__length_hint__()

        self.seek(0)

        if not pos:
            handle = io.BytesIO()
        elif pos > length:
            handle = io.BytesIO(self.read() + b'\0'*(pos - length))
        else:
            handle = io.BytesIO(self.read(pos))

        # FIXME: instead of reading everything up to `pos`,
        #        create an IO wrapper that looks like its
        #        EOF is at `pos`
        self._position = self._smb.storeFileFromOffset(
            service_name=self._share, path=self._smb_path,
            file_obj=handle, offset=0, truncate=True,
            timeout=self._fs._timeout
        )
        return self._position
