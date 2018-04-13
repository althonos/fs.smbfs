# coding: utf-8
"""Helper functions for `fs.smbfs`.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re

from ..path import relpath


__all__ = ['split_path', 'is_ip']

#: The compiled regex used by `is_ip`.
_RX_IP = re.compile(r'localhost|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')


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
    return _RX_IP.match(token) is not None


def get_hostname_and_ip(host, netbios, timeout=15, name_port=137):
    try:
        hostname, ip = host
    except ValueError:
        hostname, ip = host, None

    if is_ip(hostname):
        hostname, ip = ip, hostname

    # If given an IP: find the SMB host name
    if hostname is None:
        response = netbios.queryIPForName(ip, timeout=timeout, port=name_port)
        if not response:
            raise RuntimeError("could not get name for IP: '{}'".format(ip))
        hostname = response[0]

    # If given an hostname: find the IP
    elif ip is None:
        response = netbios.queryName(hostname, '', timeout=timeout, port=name_port)
        if not response:
            raise RuntimeError("could not get IP for host: '{}'".format(hostname))
        ip = response[0]

    #if not is_ip(ip) or ip is None or hostname is None:
    #    raise ValueError("Could not get host/IP pair for: '{}'".format(host))

    print(hostname, ip)
    return hostname, ip
