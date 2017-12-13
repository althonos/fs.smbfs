# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import sys
import time
import shutil
import unittest
import tempfile

import smb.base

import fs.test
import fs.errors
from fs.enums import ResourceType

from . import utils


@unittest.skipUnless(utils.DOCKER, "docker service unreachable.")
class TestSMBFS(fs.test.FSTestCases, unittest.TestCase):

    def make_fs(self):
        smbfs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data')
        smbfs.removetree('/')
        return smbfs

    def test_connection_error(self):
        with utils.mock.patch('fs.smbfs.smbfs.SMBFS.NETBIOS') as n:
            n.queryIPForName = utils.mock.MagicMock(return_value = ("TE"))
            self.assertRaises(
                fs.errors.CreateFailed,
                fs.open_fs, 'smb://8.8.8.8?timeout=1'
            )

    def test_write_denied(self):
        self.fs = fs.open_fs('smb://127.0.0.1/data')
        self.assertRaises(
            fs.errors.PermissionDenied,
            self.fs.openbin, '/test.txt', 'w'
        )

    def test_openbin_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(
            fs.errors.ResourceNotFound,
            self.fs.openbin, '/abc'
        )
        self.assertRaises(
            fs.errors.PermissionDenied,
            self.fs.openbin, '/abc', 'w'
        )

    def test_makedir_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(
            fs.errors.PermissionDenied,
            self.fs.makedir, '/abc'
        )

    def test_removedir_root(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
        self.assertRaises(
            fs.errors.PermissionDenied,
            self.fs.removedir, '/data'
        )

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

    def test_makedir(self):
        super(TestSMBFS, self).test_makedir()
        self.fs.touch('abc')
        self.assertRaises(
            fs.errors.DirectoryExpected,
            self.fs.makedir, '/abc/def'
        )
        self.assertRaises(
            fs.errors.ResourceNotFound,
            self.fs.makedir, '/spam/bar'
        )
        self.assertRaises(
            fs.errors.DirectoryExists,
            self.fs.delegate_fs().makedir, '/'
        )

    def test_move(self):
        super(TestSMBFS, self).test_move()
        self.fs.touch('a')
        self.fs.touch('b')
        self.assertRaises(
            fs.errors.DirectoryExpected,
            self.fs.move, 'a', 'b/a'
        )
        self.assertRaises(
            fs.errors.DestinationExists,
            self.fs.delegate_fs().move, 'data/a', 'data/b'
        )

    def test_openbin(self):
        super(TestSMBFS, self).test_openbin()
        self.fs.makedir('spam')
        self.assertRaises(
            fs.errors.FileExpected,
            self.fs.openbin, 'spam'
        )
        self.fs.touch('abc.txt')
        self.assertRaises(
            fs.errors.DirectoryExpected,
            self.fs.openbin, 'abc.txt/def.txt', 'w'
        )

    def test_removedir(self):
        super(TestSMBFS, self).test_removedir()
        self.assertRaises(
            fs.errors.RemoveRootError,
            self.fs.delegate_fs().removedir, '/'
        )

    def test_scanshares(self):
        share = next(self.fs.delegate_fs().scandir('/', ['basic', 'access']))
        self.assertEqual(share.name, 'data')
        self.assertEqual(share.get('access', 'uid'), "S-1-5-21-872258815-2917653212-864907935-1000")

    def test_getinfo_root(self):
        self.assertEqual(self.fs.delegate_fs().gettype('/'), ResourceType.directory)
        self.assertEqual(self.fs.delegate_fs().getsize('/'), 0)

    def test_getinfo_access_smb1(self):
        self.fs.settext('test.txt', 'This is a test')
        _smb = self.fs.delegate_fs()._smb
        with utils.mock.patch.object(_smb, '_getSecurity', new=_smb._getSecurity_SMB1):
            try:
                info = self.fs.getinfo('test.txt', namespaces=['access'])
            except smb.base.NotReadyError:
                self.fail("getinfo(..., ['access']) raised an error")

    def test_getinfo_smb(self):
        self.fs.settext('test.txt', 'This is a test')
        info = self.fs.getinfo('test.txt', namespaces=['basic', 'smb'])
        self.assertFalse(info.get('smb', 'hidden'))
        self.assertFalse(info.get('smb', 'system'))
