fs.smbfs
========

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

Use ``fs.open_fs`` to open a filesystem with an SMB
`FS URL <https://pyfilesystem2.readthedocs.io/en/latest/openers.html>`_:

.. code:: python

   import fs
   smb_fs = fs.open_fs('smb://username:password@SAMBAHOSTNAME:port/share')

The opener can use either an IPv4 address or a NetBIOS hostname, using the
`NetBIOS name service <https://en.wikipedia.org/wiki/NetBIOS#Name_service>`_
to find the other token.

Otherwise, use the ``SMBFS`` constructor:

.. code:: python

    import fs.smbfs
    smb_fs = fs.smbfs.SMBFS(
      host,       # name or IP of the SMB server host
      username,   # username to connect with,
                  # defaults to 'guest' for anonymous connection
      passwd,     # password to connect with,
                  # defaults to '' for anonymous connection
      timeout,    # timeout for NetBIOS and TCP requests
      port,       # Port the SMB server is listening on
      name_port,  # Port the NetBIOS naming service is listening on
      direct_tcp, # True if the Server is directly accessible through TCP,
                  # leave to False for maximum compatibility
    )

Once created, the ``SMBFS`` filesystem behaves like any other filesystem
(see the `Pyfilesystem2 documentation <https://pyfilesystem2.readthedocs.io>`_),
except if it was open in the root directory of the server, in which case the
root directory of the ``SMBFS`` instance will be read-only (since SMB clients
cannot create new shares).


See also
--------

* `fs <https://github.com/Pyfilesystem/pyfilesystem2>`_, the core Pyfilesystem2 library
* `fs.archive <https://github.com/althonos/fs.archive>`_, enhanced archive filesystems
  for Pyfilesystem2
* `fs.proxy <https://github.com/althonos/fs.proxy>`_, miscellaneous proxy filesystems
  for Pyfilesystem2
* `fs.sshfs <https://github.com/althonos/fs.sshfs>`_, Pyfilesystem2 over SSH
  using paramiko
