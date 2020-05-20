# coding: utf-8
"""Pyfilesystem2 over SMB using pysmb.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from .smbfs import SMBFS

__all__ = ['SMBFS']

__license__ = "MIT"
__copyright__ = "Copyright (c) 2017-2020 Martin Larralde"
__author__ = "Martin Larralde <martin.larralde@embl.de>"
__version__ = 'dev'

# Dynamically get the version of the installed module
try:
    import pkg_resources
    __version__ = pkg_resources.get_distribution(__name__).version
except Exception: # pragma: no cover
    pkg_resources = None
finally:
    del pkg_resources
