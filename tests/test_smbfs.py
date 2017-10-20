# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import time
import shutil
import unittest
import tempfile

import fs.test
from fs.errors import PermissionDenied, ResourceNotFound

from . import utils


@unittest.skipUnless(utils.DOCKER, "docker service unreachable.")
class TestSMBFS(fs.test.FSTestCases, unittest.TestCase):

    def make_fs(self):
        smbfs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data')
        smbfs.removetree('/')
        return smbfs

    def test_write_denied(self):
        self.fs = fs.open_fs('smb://127.0.0.1/data')
        self.assertRaises(PermissionDenied, self.fs.openbin, '/test.txt', 'w')

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

        self.fs.remove('foo.txt')
