# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

from .base import Opener
from ..subfs import ClosingSubFS

#__license__ = "LGPL-2.1+"
#__copyright__ = "Copyright (c) 2017 Martin Larralde"
#__author__ = "Martin Larralde <martin.larralde@ens-cachan.fr>"
#__version__ = 'dev'


# Dynamically get the version of the main module
# try:
#     _name = __name__.replace('.opener', '')
#     import pkg_resources
#     __version__ = pkg_resources.get_distribution(_name).version
# except Exception:
#     pkg_resources = None
# finally:
#     del pkg_resources


class SMBOpener(Opener):
    protocols = ['smb', 'samba', 'cifs']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):
        from ..smbfs import SMBFS
        smb_host, _, dir_path = parse_result.resource.partition('/')
        smb_host, _, smb_port = smb_host.partition(':')
        smb_port = int(smb_port) if smb_port.isdigit() else 445
        smb_fs = SMBFS(
            smb_host,
            username=parse_result.username or 'guest',
            passwd=parse_result.password or '',
            port=smb_port,
        )

        if dir_path: # pragma: no cover
            return smb_fs.opendir(dir_path, factory=ClosingSubFS)
        else:
            return smb_fs
