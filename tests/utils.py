# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import atexit
import os
import time
import unittest

import docker
import fs
import six

try:
    docker_client = docker.from_env(version='auto')
    docker_client.info()
except Exception:
    DOCKER = False
else:
    DOCKER = True

try:
    from unittest import mock   # pylint: disable=unused-import
except ImportError:
    import mock                 # pylint: disable=unused-import

CI = os.getenv('CI', '').lower() == 'true'
FSVERSION = tuple(map(int, fs.__version__.split('.')))

if DOCKER:
    docker_client = docker.from_env(version='auto')
    smb_container = docker_client.containers.run(
        "pwntr/samba-alpine", detach=True, tty=True,
        ports={'139/tcp': 139, '137/udp': 137, '445/tcp': 445},
        tmpfs={'/shared': 'size=3G,uid=1000'},
    )
    atexit.register(smb_container.remove)
    atexit.register(smb_container.kill)
    time.sleep(15)

if six.PY2:
    def py2expectedFailure(func):
        return unittest.expectedFailure(func)
else:
    def py2expectedFailure(func):
        return func
