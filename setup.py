#!/usr/bin/env python

import setuptools

install_requires = [
    'configparser~=3.2; python_version<"3"',
    'fs~=2.2',
    'pysmb~=1.2',
    'six~=1.10',
]

dev_requires = [
    'codecov',
    'coverage',
    'green',
    'docutils',
    'Pygments',
]

test_requires = [
    'docker~=3.6',
    'mock~=2.0; python_version<"3.4"',
    'semantic_version~=2.6'
]

setuptools.setup(
    install_requires=install_requires,
    extras_require={
        'dev': dev_requires + test_requires
    },
)
