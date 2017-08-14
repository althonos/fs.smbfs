# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

from ..path import relpath


__all__ = ['split_path']


def split_path(path):
    if path in '/':
        return '', ''
    path = relpath(path)
    if '/' not in path:
        return path, ''
    return path.split('/', 1)
