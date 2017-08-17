# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import re
import sys
import stat
import time
import shutil
import unittest
import tempfile

import docker

import fs.test
import fs.smbfs
from fs.subfs import ClosingSubFS
from fs.errors import PermissionDenied, ResourceNotFound
from fs.permissions import Permissions

from . import utils


@unittest.skipUnless(utils.CI or utils.DOCKER, "docker service unreachable.")
class _TestSMBFS(fs.test.FSTestCases):

    @classmethod
    def serverHasStarted(cls):
        s = b"daemon 'smbd' finished starting up and ready to serve connections"
        cls.samba_container.update()
        return s in cls.samba_container.logs()

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
            "pwntr/samba-alpine", detach=True, tty=True,
            ports={'139/tcp': 139, '137/udp': 137, '445/tcp': 445},
            tmpfs={'/shared': 'size=3G,uid=1000'},
        )
        time.sleep(15)

    @classmethod
    def stopSambaServer(cls):
        cls.samba_container.kill()
        cls.samba_container.remove()

    @staticmethod
    def destroy_fs(fs):
        fs.close()
        del fs


@utils.tag_on(sys.version_info < (3,), unittest.expectedFailure)
class TestSMBFS_fromHostname(_TestSMBFS, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@SAMBAALPINE/data')



class TestSMBFS_fromIP(_TestSMBFS, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@127.0.0.1/data')

    def test_openbin_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(ResourceNotFound, self.fs.openbin, '/abc')
        self.assertRaises(PermissionDenied, self.fs.openbin, '/abc', 'w')

    def test_makedir_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(PermissionDenied, self.fs.makedir, '/abc')

    def test_removedir_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(PermissionDenied, self.fs.removedir, '/data')

    def test_seek(self):
        self.fs.settext('foo.txt', 'Hello, World !')

        with self.fs.openbin('foo.txt') as handle:
            self.assertRaises(ValueError, handle.seek, -2, 0)
            self.assertRaises(ValueError, handle.seek, 2, 2)
            self.assertRaises(ValueError, handle.seek, -2, 12)

            self.assertEqual(handle.seek(2, 1), 2)
            self.assertEqual(handle.seek(-1, 1), 1)
            self.assertEqual(handle.seek(-2, 1), 0)
