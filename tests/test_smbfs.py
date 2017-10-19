# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import time
import shutil
import unittest
import tempfile

import docker

import fs.test
import fs.smbfs
from fs.errors import PermissionDenied, ResourceNotFound

from . import utils


@unittest.skipUnless(utils.CI or utils.DOCKER, "docker service unreachable.")
class _TestSMBFS(object):

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
        self.fs = self.make_fs()
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
class TestSMBOpenerWithHost(_TestSMBFS, fs.test.FSTestCases, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@SAMBAALPINE/data?timeout=5')

    @unittest.skipUnless(utils.fs_version > (2, 0, 7),
                         'FS URLs params not supported.')
    def test_url_parameters(self):
        self.assertEqual(self.fs.delegate_fs()._timeout, 5)


class TestSMBOpenerWithIP(_TestSMBFS, fs.test.FSTestCases, unittest.TestCase):

    @staticmethod
    def make_fs():
        return fs.open_fs('smb://rio:letsdance@127.0.0.1/data?timeout=5')

    @unittest.skipUnless(utils.fs_version > (2, 0, 7),
                         'FS URLs params not supported.')
    def test_url_parameters(self):
        self.assertEqual(self.fs.delegate_fs()._timeout, 5)


class TestSMBFS(_TestSMBFS, unittest.TestCase):

    def setUp(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')

    def test_write_denied(self):
        self.fs = fs.open_fs('smb://127.0.0.1/data')
        self.assertRaises(PermissionDenied, self.fs.openbin, '/test.txt', 'w')

    def test_openbin_root(self):
        self.assertRaises(ResourceNotFound, self.fs.openbin, '/abc')
        self.assertRaises(PermissionDenied, self.fs.openbin, '/abc', 'w')

    def test_makedir_root(self):
        self.assertRaises(PermissionDenied, self.fs.makedir, '/abc')

    def test_removedir_root(self):
        self.assertRaises(PermissionDenied, self.fs.removedir, '/data')

    def test_seek(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data')
        self.fs.settext('foo.txt', 'Hello, World !')

        with self.fs.openbin('foo.txt') as handle:
            self.assertRaises(ValueError, handle.seek, -2, 0)
            self.assertRaises(ValueError, handle.seek, 2, 2)
            self.assertRaises(ValueError, handle.seek, -2, 12)

            self.assertEqual(handle.seek(2, 1), 2)
            self.assertEqual(handle.seek(-1, 1), 1)
            self.assertEqual(handle.seek(-2, 1), 0)

        self.fs.remove('foo.txt')
