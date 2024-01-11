# coding: utf-8
"""`SMBFS` opener definition.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import configparser

import six

from fs.opener.base import Opener
from fs.subfs import ClosingSubFS
from fs.errors import CreateFailed

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017-2021 Martin Larralde"
__author__ = "MiaRec <support@miarec.com>"
__version__ = __version__ = (
    __import__("pkg_resources")
    .resource_string("miarec_smbfs", "_version.txt")
    .strip()
    .decode("ascii")
)


class SMBOpener(Opener):
    """`SMBFS` opener.
    """

    protocols = ['msmb', 'mcifs']

    @staticmethod
    def open_fs(fs_url, parse_result, writeable, create, cwd):  # noqa: D102
        from .smbfs import SMBFS
        smb_host, _, dir_path = parse_result.resource.partition('/')
        smb_host, _, smb_port = smb_host.partition(':')
        smb_port = int(smb_port) if smb_port.isdigit() else None


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
            direct_tcp=params.getboolean('smbfs', 'direct-tcp', fallback=False),
            domain=params.get('smbfs', 'domain', fallback=''),
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
