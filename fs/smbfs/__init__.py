# coding: utf-8
"""Pyfilesystem2 over SMB using pysmb.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .smbfs import SMBFS

__all__ = ['SMBFS']

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017-2021 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@embl.de>"
__version__ = (
    __import__("pkg_resources")
    .resource_string(__name__, "_version.txt")
    .strip()
    .decode("ascii")
)
