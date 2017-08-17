# coding: utf-8
"""Helper functions for `fs.smbfs`.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from ..path import relpath


__all__ = ['split_path']


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
