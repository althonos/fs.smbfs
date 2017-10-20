# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest
import fs

from . import utils


@unittest.skipUnless(utils.DOCKER, "docker service unreachable.")
class TestSMBOpener(unittest.TestCase):

    @unittest.skipUnless(utils.FSVERSION > (2, 0, 7), 'not supported')
    def test_url_parameters(self):
        self.fs = fs.open_fs('smb://rio:letsdance@SAMBAALPINE/data?timeout=5')
        self.assertEqual(self.fs.delegate_fs()._timeout, 5)

    def test_host(self):
        self.fs = fs.open_fs('smb://rio:letsdance@SAMBAALPINE/data')

    def test_ip(self):
        self.fs = fs.open_fs('smb://rio:letsdance@127.0.0.1/data')
