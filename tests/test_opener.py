# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import six
import fs.errors
import fs.path

from . import utils


@unittest.skipUnless(utils.DOCKER, "docker service unreachable.")
class TestSMBOpener(unittest.TestCase):

    @unittest.skipUnless(utils.FSVERSION > (2, 0, 7), 'not supported')
    def test_timeout_parameter(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data?timeout=5')
        self.assertEqual(self.fs.delegate_fs()._timeout, 5)

    @utils.py2expectedFailure
    def test_bad_host(self):
        self.assertRaises(
            fs.errors.CreateFailed,
            fs.open_fs,
            'smb://NONSENSE/?timeout=2',
        )

    def test_bad_ip(self):
        self.assertRaises(
            fs.errors.CreateFailed,
            fs.open_fs,
            'smb://84.190.160.12/?timeout=2',
        )

    @utils.py2expectedFailure
    def test_host(self):
        self.fs = fs.open_fs('smb://rio:letsdance@SAMBAALPINE/')

    def test_ip(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')

    def test_create(self):

        directory = "data/test/directory"
        base = "smb://rio:letsdance@127.0.0.1"
        url = "{}/{}".format(base, directory)

        # Make sure unexisting directory raises `CreateFailed`
        with self.assertRaises(fs.errors.CreateFailed):
            smb_fs = fs.open_fs(url)

        # Open with `create` and try touching a file
        with fs.open_fs(url, create=True) as smb_fs:
            smb_fs.touch("foo")

        # Open the base filesystem and check the subdirectory exists
        with fs.open_fs(base) as smb_fs:
            self.assertTrue(smb_fs.isdir(directory))
            self.assertTrue(smb_fs.isfile(fs.path.join(directory, "foo")))

        # Open without `create` and check the file exists
        with fs.open_fs(url) as smb_fs:
            self.assertTrue(smb_fs.isfile("foo"))

        # Open with create and check this does fail
        with fs.open_fs(url, create=True) as smb_fs:
            self.assertTrue(smb_fs.isfile("foo"))
