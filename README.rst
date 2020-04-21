``fs.smbfs`` |star me|
======================

.. |star me| image:: https://img.shields.io/github/stars/althonos/fs.smbfs.svg?style=social&maxAge=3600&label=Star
   :target: https://github.com/althonos/fs.smbfs/stargazers

|Source| |PyPI| |Travis| |Codecov| |Codacy| |Format| |License|

.. |Codacy| image:: https://img.shields.io/codacy/grade/82d40d17b4734692a9e70c5af5cc2a5b/master.svg?style=flat-square&maxAge=300
   :target: https://www.codacy.com/app/althonos/fs.smbfs/dashboard

.. |Travis| image:: https://img.shields.io/travis/althonos/fs.smbfs/master.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.smbfs/branches

.. |Codecov| image:: https://img.shields.io/codecov/c/github/althonos/fs.smbfs/master.svg?style=flat-square&maxAge=300
   :target: https://codecov.io/gh/althonos/fs.smbfs

.. |PyPI| image:: https://img.shields.io/pypi/v/fs.smbfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.smbfs

.. |Format| image:: https://img.shields.io/pypi/format/fs.smbfs.svg?style=flat-square&maxAge=300
   :target: https://pypi.python.org/pypi/fs.smbfs

.. |Versions| image:: https://img.shields.io/pypi/pyversions/fs.smbfs.svg?style=flat-square&maxAge=300
   :target: https://travis-ci.org/althonos/fs.smbfs

.. |License| image:: https://img.shields.io/pypi/l/fs.smbfs.svg?style=flat-square&maxAge=300
   :target: https://choosealicense.com/licenses/mit/

.. |Source| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/althonos/fs.smbfs


Requirements
------------

+-------------------+-----------------+-------------------+--------------------+
| **pyfilesystem2** | |PyPI fs|       | |Source fs|       | |License fs|       |
+-------------------+-----------------+-------------------+--------------------+
| **six**           | |PyPI six|      | |Source six|      | |License six|      |
+-------------------+-----------------+-------------------+--------------------+
| **pysmb**         | |PyPI pysmb|    | |Source pysmb|    | |License pysmb|    |
+-------------------+-----------------+-------------------+--------------------+


.. |License six| image:: https://img.shields.io/pypi/l/six.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source six| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/benjaminp/six

.. |PyPI six| image:: https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/six

.. |License fs| image:: https://img.shields.io/pypi/l/fs.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/mit/

.. |Source fs| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/PyFilesystem/pyfilesystem2

.. |PyPI fs| image:: https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/fs

.. |License pysmb| image:: https://img.shields.io/pypi/l/pysmb.svg?maxAge=300&style=flat-square
   :target: https://choosealicense.com/licenses/zlib/

.. |Source pysmb| image:: https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=300&style=flat-square
   :target: https://github.com/miketeo/pysmb

.. |PyPI pysmb| image:: https://img.shields.io/pypi/v/pysmb.svg?maxAge=300&style=flat-square
   :target: https://pypi.python.org/pypi/pysmb


Installation
------------

Install directly from PyPI, using `pip <https://pip.pypa.io/>`_ ::

    pip install fs.smbfs


Usage
-----

Opener
''''''

Use ``fs.open_fs`` to open a filesystem with an SMB
`FS URL <https://pyfilesystem2.readthedocs.io/en/latest/openers.html>`_:

.. code:: python

   import fs
   smb_fs = fs.open_fs('smb://username:password@SAMBAHOSTNAME:port/share')

The opener can use either an IPv4 address or a NetBIOS hostname, using the
`NetBIOS name service <https://en.wikipedia.org/wiki/NetBIOS#Name_service>`_
to find the other token. Otherwise, if NetBIOS is not available, a new SMB
connection can be established by using the IPv4 address and giving the 
hostname with the ``hostname`` URL parameter.

The following parameters can be passed as URL parameters: ``timeout``,
``name-port``, ``direct-tcp``, ``hostname``.


Constructor
'''''''''''

.. code:: python

    import fs.smbfs
    smb_fs = fs.smbfs.SMBFS(
        host, username='guest', passwd='', timeout=15,
        port=139, name_port=137, direct_tcp=False
    )

with each argument explained below:

``host``
  either the host name (*not* the FQDN) of the SMB server, its IP address, or
  both in a `tuple`. *if either the IP address or the host name is not given,
  NETBIOS is queried to get the missing data.*
``user``
  the username to connect with, defaults to `'guest'` for anonymous connection.
``passwd``
  an optional password, defaults to `''` for anonymous connection.
``timeout``
  the timeout, in seconds, for NetBIOS and TCP requests.
``port``
  the port the SMB server is listening on.
``naming_port``
  the port the NetBIOS naming service is listening on
``direct_tcp``
  set to `True` if the server is accessible directly through TCP, leave to
  `False` for maximum compatibility


Once created, the ``SMBFS`` filesystem behaves like any other filesystem
(see the `Pyfilesystem2 documentation <https://pyfilesystem2.readthedocs.io>`_),
except if it was open in the root directory of the server, in which case the
root directory of the ``SMBFS`` instance will be read-only (since SMB clients
cannot create new shares).


Feedback
--------

Found a bug ? Have an enhancement request ? Head over to the
`GitHub issue tracker <https://github.com/althonos/fs.smbfs/issues>`_ of the
project if you need to report or ask something. If you are filling in on a bug,
please include as much information as you can about the issue, and try to
recreate the same bug in a simple, easily reproductible situation.


See also
--------

* `fs <https://github.com/Pyfilesystem/pyfilesystem2>`_, the core Pyfilesystem2 library
* `fs.archive <https://github.com/althonos/fs.archive>`_, enhanced archive filesystems
  for Pyfilesystem2
* `fs.sshfs <https://github.com/althonos/fs.sshfs>`_, Pyfilesystem2 over SSH
  using paramiko
