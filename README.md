# `miarec_smbfs` SMB filesystem for PyFilesystem2

This is a fork of [fs.smbfs](https://github.com/althonos/fs.smbfs)

The code was modified by MiaRec team to fullfill our needs.

[![Actions](https://img.shields.io/github/actions/workflow/status/miarec/miarec_smbfs/test.yml?branch=master&logo=github&style=flat-square&maxAge=300)](https://github.com/miarec/miarec_smbfs/actions)
[![License](https://img.shields.io/pypi/l/fs.smbfs.svg?style=flat-square&maxAge=300)](https://choosealicense.com/licenses/mit/)

## Notable differences between miarec_s3fs and fs-s3fs

1. Requires Python 3.7+. A support of older version of Python was removed.

2. The opener protocol prefix is `msmb://` (instead of the original `smb://`)


## Requirements

| **PyFilesystem2** | [![PyPI fs](https://img.shields.io/pypi/v/fs.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/fs) | [![Source fs](https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square)](https://github.com/PyFilesystem/pyfilesystem2) | [![License fs](https://img.shields.io/pypi/l/fs.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
|:-|:-|:-|:-|
| **six** | [![PyPI six](https://img.shields.io/pypi/v/six.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/six) | [![Source six]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/benjaminp/six) | [![License six](https://img.shields.io/pypi/l/six.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/mit/) |
| **PySMB** | [![PyPI pysmb](https://img.shields.io/pypi/v/pysmb.svg?maxAge=300&style=flat-square)](https://pypi.python.org/pypi/pysmb) | [![Source pysmb]( https://img.shields.io/badge/source-GitHub-303030.svg?maxAge=36000&style=flat-square )]( https://github.com/miketeo/pysmb) | [![License pysmb](https://img.shields.io/pypi/l/pysmb.svg?maxAge=36000&style=flat-square)](https://choosealicense.com/licenses/zlib/) |

`miarec_smbfs` supports Python versions 3.7+ 

## Installation

Install directly from PyPI, using [pip](https://pip.pypa.io/) :

```console
$ pip install miarec_smbfs
```

## Usage

### Opener

Use `fs.open_fs` to open a filesystem with an SMB [FS
URL](https://pyfilesystem2.readthedocs.io/en/latest/openers.html):

```python
import fs
smb_fs = fs.open_fs('msmb://username:password@SAMBAHOSTNAME:port/share')
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
import miarec_smbfs
smb_fs = miarec_smbfs.SMBFS(
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

## Testing

Automated unit tests are run on [GitHub Actions](https://github.com/miarec/miarec_smbfs/actions)

To run the tests locally, do the following.

Install Docker on local machine.

Create activate python virtual environment:

    python -m vevn venv
    source venv\bin\activate

Install the project and test dependencies:

    pip install -e ".[test]"

Run tests:

    pytest

## Credits

`miarec_smbfs` is developed and maintained by [MiaRec](https://www.miarec.com)

The original code (`fs.smbfs`) was developed by:
- [Martin Larralde](https://github.com/althonos)

