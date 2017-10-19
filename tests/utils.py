# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import os

import fs
import docker

try:
    docker.from_env(version='auto').info()
except Exception:
    DOCKER = False
else:
    DOCKER = True

try:
    from unittest import mock   # pylint: disable=unused-import
except ImportError:
    import mock                 # pylint: disable=unused-import

CI = os.getenv('CI', '').lower() == 'true'

def tag_on(condition, wrapper):
    return wrapper if condition else (lambda func: func)

fs_version = tuple(map(int, fs.__version__.split('.')))
