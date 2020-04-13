# coding: utf-8
"""`SMBFS` opener definition.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import configparser

import six

from .base import Opener
from .registry import registry
from ..subfs import ClosingSubFS
from ..errors import CreateFailed

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017-2019 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@ens-cachan.fr>"
__version__ = 'dev'


# Dynamically get the version of the main module
try:
    import pkg_resources
    _name = __name__.replace('.opener', '')
    __version__ = pkg_resources.get_distribution(_name).version
except Exception: # pragma: no cover
    pkg_resources = None
finally:
    del pkg_resources


class SMBOpener(Opener):
    """`SMBFS` opener.
    """

    protocols = ['smb', 'cifs']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):  # noqa: D102
        from ..smbfs import SMBFS
        smb_host, _, dir_path = parse_result.resource.partition('/')
        smb_host, _, smb_port = smb_host.partition(':')
        smb_port = int(smb_port) if smb_port.isdigit() else 445


        params = configparser.ConfigParser()
        params.read_dict({'smbfs':getattr(parse_result, 'params', {})})

        smb_hostname = params.get('smbfs', 'hostname', fallback=None)

        smb_fs = SMBFS(
            (smb_host, smb_hostname),
            username=parse_result.username or 'guest',
            passwd=parse_result.password or '',
            port=smb_port,
            timeout=params.getint('smbfs', 'timeout', fallback=15),
            name_port=params.getint('smbfs', 'name-port', fallback=137),
            direct_tcp=params.getboolean('smbfs', 'direct-tcp', fallback=False)
        )

        try:
            if dir_path:
                if create:
                    smb_fs.makedirs(dir_path, recreate=True)
                return smb_fs.opendir(dir_path, factory=ClosingSubFS)
            else:
                return smb_fs
        except Exception as err:
            six.raise_from(CreateFailed, err)


registry.install(SMBOpener)
