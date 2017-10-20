# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

import six
import fs.errors

from . import utils


@unittest.skipUnless(utils.DOCKER, "docker service unreachable.")
class TestSMBOpener(unittest.TestCase):

    @unittest.skipUnless(utils.FSVERSION > (2, 0, 7), 'not supported')
    def test_timeout_parameter(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data?timeout=5')
        self.assertEqual(self.fs.delegate_fs()._timeout, 5)

    def test_bad_host(self):
        self.assertRaises(
            fs.errors.CreateFailed,
            fs.open_fs,
            'smb://NONSENSE/?timeout=2',
        )
    if six.PY2:
        test_bad_host = unittest.expectedFailure(test_bad_host)


    def test_bad_ip(self):
        self.assertRaises(
            fs.errors.CreateFailed,
            fs.open_fs,
            'smb://84.190.160.12/?timeout=2',
        )

    def test_host(self):
        self.fs = fs.open_fs('smb://rio:letsdance@SAMBAALPINE/')
    if six.PY2:
        test_host = unittest.expectedFailure(test_host)

    def test_ip(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/')
