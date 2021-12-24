# `fs.smbfs` [![star me](https://img.shields.io/github/stars/althonos/fs.smbfs.svg?style=social&maxAge=3600&label=Star)](https://github.com/althonos/fs.smbfs/stargazers)

[![Source](https://img.shields.io/badge/source-GitHub-303030.svg?logo=git&maxAge=36000&style=flat-square)](https://github.com/althonos/fs.smbfs)
[![PyPI](https://img.shields.io/pypi/v/fs.smbfs.svg?logo=pypi&style=flat-square&maxAge=3600)](https://pypi.python.org/pypi/fs.smbfs)
[![Actions](https://img.shields.io/github/workflow/status/althonos/fs.smbfs/Test/master?logo=github&style=flat-square&maxAge=300)](https://github.com/althonos/fs.smbfs/actions)
[![Codecov](https://img.shields.io/codecov/c/github/althonos/fs.smbfs/master.svg?logo=codecov&style=flat-square&maxAge=300)](https://codecov.io/gh/althonos/fs.smbfs)
[![Codacy](https://img.shields.io/codacy/grade/82d40d17b4734692a9e70c5af5cc2a5b/master.svg?logo=codacy&style=flat-square&maxAge=300)](https://www.codacy.com/app/althonos/fs.smbfs/dashboard)
[![License](https://img.shields.io/pypi/l/fs.smbfs.svg?style=flat-square&maxAge=300)](https://choosealicense.com/licenses/mit/)
[![Versions](https://img.shields.io/pypi/pyversions/fs.smbfs.svg?logo=python&style=flat-square&maxAge=300)](https://pypi.org/project/fs.smbfs)
[![Format](https://img.shields.io/pypi/format/fs.smbfs.svg?style=flat-square&maxAge=300)](https://pypi.python.org/pypi/fs.smbfs)
[![GitHub issues](https://img.shields.io/github/issues/althonos/fs.smbfs.svg?style=flat-square&maxAge=600)](https://github.com/althonos/fs.smbfs/issues)
[![Downloads](https://img.shields.io/badge/dynamic/json?style=flat-square&color=303f9f&maxAge=86400&label=downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2Ffs.smbfs)](https://pepy.tech/project/fs.smbfs)
[![Changelog](https://img.shields.io/badge/keep%20a-changelog-8A0707.svg?maxAge=2678400&style=flat-square)](https://github.com/althonos/fs.smbfs/blob/master/CHANGELOG.md)


## Requirements

| **PyFilesystem2** | [![PyPI fs](https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/fs) | [![Source fs](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square)](https://github.com/PyFilesystem/pyfilesystem2) | [![License fs](https://img.shields.io/pypi/l/fs.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
|:-|:-|:-|:-|
| **six** | [![PyPI six](https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/six) | [![Source six]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/benjaminp/six) | [![License six](https://img.shields.io/pypi/l/six.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
| **PySMB** | [![PyPI pysmb](https://img.shields.io/pypi/v/pysmb.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/pysmb) | [![Source pysmb]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/miketeo/pysmb) | [![License pysmb](https://img.shields.io/pypi/l/pysmb.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/zlib/) |

## Installation

Install directly from PyPI, using [pip](https://pip.pypa.io/) :

```console
$ pip install fs.smbfs
```

## Usage

### Opener

Use `fs.open_fs` to open a filesystem with an SMB [FS
URL](https://pyfilesystem2.readthedocs.io/en/latest/openers.html):

```python
import fs
smb_fs = fs.open_fs('smb://username:password@SAMBAHOSTNAME:port/share')
```

The opener can use either an IPv4 address or a NetBIOS hostname, using the
[NetBIOS name service](https://en.wikipedia.org/wiki/NetBIOS#Name_service) to
find the other token. Otherwise, if NetBIOS is not available, a new SMB
connection can be established by using the IPv4 address and giving the
hostname with the `hostname` URL parameter.

The following parameters can be passed as URL parameters: `timeout`,
`name-port`, `direct-tcp`, `hostname`, and `domain`.


### Constructor

```python
import fs.smbfs
smb_fs = fs.smbfs.SMBFS(
    host, username="guest", passwd="", timeout=15,
    port=139, name_port=137, direct_tcp=False, domain=""
)
```

with each argument explained below:

- `host`: either the host name (*not* the [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name))
  of the SMB server, its IP address, or both in a tuple.
  *If either the IP address or the host name is not given, NETBIOS is queried to get the missing data.*
- `user`: the username to connect with, defaults to `"guest"` for anonymous
  connection.
- `passwd`: an optional password to connect with, defaults to `""` for
  anonymous connection.
- `timeout`: the timeout, in seconds, for NetBIOS and TCP requests.
- `port`: the port the SMB server is listening on.
- `name_port`: the port the NetBIOS naming service is listening on.
- `direct_tcp`: set to *True* if the server is accessible directly
  through TCP, leave as *False* for maximum compatibility.
- `domain`: the network domain to connect with, i.e. the workgroup on
  Windows. Usually safe to leave as empty string, the default.

Once created, the `SMBFS` filesystem behaves like any other filesystem
(see the [Pyfilesystem2 documentation](https://pyfilesystem2.readthedocs.io)),
except if it was open in the root directory of the server, in which case the
root directory of the `SMBFS` instance will be read-only (since SMB clients
cannot create new shares).

## Feedback

Found a bug ? Have an enhancement request ? Head over to the [GitHub
issue tracker](https://github.com/althonos/fs.smbfs/issues) of the
project if you need to report or ask something. If you are filling in on
a bug, please include as much information as you can about the issue,
and try to recreate the same bug in a simple, easily reproducible
situation.


## Credits

`fs.smbfs` is developed and maintained by:
- [Martin Larralde](https://github.com/althonos)

The following people contributed to `fs.sshfs`:
- [Mike DePalatis](https://github.com/mivade)
- [Isaac Jackson](https://github.com/Vegemash)
- [Max Klein](https://github.com/telamonian)
- [Francesco Frassinelli](https://github.com/frafra)
- [Josiah Witheford](https://github.com/josiahwitheford)

This project obviously owes a lot to the PyFilesystem2 project and
[all its contributors](https://github.com/PyFilesystem/pyfilesystem2/blob/master/CONTRIBUTORS.md).


## See also

-   [fs](https://github.com/Pyfilesystem/pyfilesystem2), the core
    Pyfilesystem2 library
-   [fs.archive](https://github.com/althonos/fs.archive), enhanced
    archive filesystems for Pyfilesystem2
-   [fs.sshfs](https://github.com/althonos/fs.sshfs), Pyfilesystem2 over
    SSH using paramiko
