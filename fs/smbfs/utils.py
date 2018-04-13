# coding: utf-8
"""Helper functions for `fs.smbfs`.
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import six

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

    Note:
        ``is_ip("localhost")`` will return `True` !

    Example:
        >>> from fs.smbfs.utils import is_ip
        >>> is_ip('192.168.0.1')
        True
        >>> is_ip('github.com')
        False
    """
    return _RX_IP.match(token) is not None


def get_hostname_and_ip(host, netbios, timeout=15, name_port=137):
    """Get the IP and hostnames from the given token.

    Example:
        >>> from fs.smbfs.utils import get_hostname_and_ip as ghip
        >>> from nmb.NetBIOS import NetBIOS
        >>> nb = NetBIOS()
        >>> ghip("SAMBAALPINE")
        ("SAMBAALPINE", "127.0.0.1")
        >>> ghip("localhost")
        ("SAMBAALPINE", "localhost")
        >>> ghip(("localhost", "SAMBAALPINE"))
        ("SAMBAALPINE", "localhost")
    """


    try:
        name, ip = host
    except ValueError:
        name, ip = host, None

    # Swap values if needed
    if (name is not None and is_ip(name)) or (ip is not None and not is_ip(ip)):
        name, ip = ip, name

    # If given an IP: find the SMB host name
    if name is None and ip is not None:
        response = netbios.queryIPForName(ip, timeout=timeout, port=name_port)
        if not response:
            raise RuntimeError("could not get name for IP: '{}'".format(ip))
        name = response[0]

    # If given an hostname: find the IP
    elif ip is None and name is not None:
        response = netbios.queryName(name, '', timeout=timeout, port=name_port)
        if not response:
            raise RuntimeError("could not get IP for host: '{}'".format(name))
        ip = response[0]

    # Make sure we have both values
    elif ip is None and name is None:
       raise ValueError("Could not get host/IP pair for: '{}'".format(host))

    if six.PY2:
        if isinstance(name, six.text_type):
            name = name.encode('utf-8')
        if isinstance(ip, six.text_type):
            ip = ip.encode('utf-8')

    return name, ip
