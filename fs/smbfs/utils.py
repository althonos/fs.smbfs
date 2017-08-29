# coding: utf-8
"""Helper functions for `fs.smbfs`.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re

from ..path import relpath


__all__ = ['split_path', 'is_ip']

#: The compiled regex used by `is_ip`.
_RX_IP = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


def split_path(path):
    """Split a SMBFS path into a share name and a path component.

    Example:
        >>> from fs.smbfs.utils import split_path
        >>> split_path('/share/path/to/resource')
        ('share', 'path/to/resource')
        >>> split_path('/share')
        ('share', '')
    """
    if path in '/':
        return '', ''
    path = relpath(path)
    if '/' not in path:
        return path, ''
    return path.split('/', 1)


def is_ip(token):
    """Return True if ``token`` is an IP adress, using a regex.

    Example:
        >>> from fs.smbfs.utils import is_ip
        >>> is_ip('192.168.0.1')
        True
        >>> is_ip('github.com')
        False
    """
    return _RX_IP.match(token)
