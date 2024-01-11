# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import unittest

from miarec_smbfs.file import _Cursor


class TestCursor(unittest.TestCase):

    def test_write(self):
        buffer = bytearray(8)
        cursor = _Cursor(buffer)
        self.assertEqual(cursor.write(b"abcd"), 4)
        self.assertEqual(buffer, b"abcd\0\0\0\0")
        self.assertEqual(cursor.write(b"efgh"), 4)
        self.assertEqual(buffer, b"abcdefgh")
        self.assertRaises(IOError, cursor.write, b"ijkl")
        self.assertEqual(cursor.write(b""), 0)
