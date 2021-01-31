# coding: utf-8
from __future__ import unicode_literals
from __future__ import absolute_import

import fs
import os


# Add the local code directory to the `fs` module path
fs.__path__.insert(0, os.path.realpath(
    os.path.join(__file__, os.pardir, os.pardir, 'fs')))
fs.opener.__path__.insert(0, os.path.realpath(
    os.path.join(__file__, os.pardir, os.pardir, 'fs', 'opener')))


# Add additional openers to the entry points
import fs.opener
from fs.opener.smbfs import SMBOpener
fs.opener.registry.install(SMBOpener)
