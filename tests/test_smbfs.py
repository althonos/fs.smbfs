# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import stat
import time
import shutil
import unittest
import tempfile

import docker

import fs.test
import fs.errors
from fs.subfs import ClosingSubFS
from fs.permissions import Permissions

from . import utils


@unittest.skipUnless(utils.CI or utils.DOCKER, "docker service unreachable.")
class _TestSMBFS(fs.test.FSTestCases):

    @classmethod
    def setUpClass(cls):
        cls.docker_client = docker.from_env(version='auto')
        cls.temp_dir = tempfile.mkdtemp()
        cls.startSambaServer()

    @classmethod
    def tearDownClass(cls):
        cls.stopSambaServer()
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        super(_TestSMBFS, self).setUp()
        self.fs.removetree("/")

    @classmethod
    def startSambaServer(cls):
        cls.samba_container = cls.docker_client.containers.run(
            "pwntr/samba-alpine",
            detach=True, network_mode='host', tty=True,
            volumes={cls.temp_dir: {'bind': '/shared', 'mode': 'rw'}}
        )
        time.sleep(5)

    @classmethod
    def stopSambaServer(cls):
        cls.samba_container.kill()
        cls.samba_container.remove()

    @staticmethod
    def destroy_fs(fs):
        fs.close()
        del fs


class TestSMBFS_fromHostname(_TestSMBFS, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@SAMBAALPINE/data')


class TestSMBFS_fromIP(_TestSMBFS, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@127.0.0.1/data')
