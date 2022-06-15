# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).


## [Unreleased]

[Unreleased]: https://github.com/althonos/fs.smbfs/compare/v1.0.5...HEAD


## [v1.0.5] - 2022-06-15

[v1.0.5]: https://github.com/althonos/fs.smbfs/compare/v1.0.4...v1.0.5

### Added
- Explicit support for `v1.2.8` of PySMB.


## [v1.0.4] - 2022-04-29

[v1.0.4]: https://github.com/althonos/fs.smbfs/compare/v1.0.3...v1.0.4

### Fixed
- `SMBFS.geturl` producing invalid URLs when the `SMBFS` object was created without explicitly setting a port ([#35](https://github.com/althonos/fs.smbfs/issues/35)).

### Added
- `preserve_time` keyword argument to `SMBFS.move`.


## [v1.0.3] - 2021-08-24

[v1.0.3]: https://github.com/althonos/fs.smbfs/compare/v1.0.2...v1.0.3

### Fixed
- `SMBFS._meta['invalid_path_chars']` containing valid characters ([#32](https://github.com/althonos/fs.smbfs/issues/32)).


## [v1.0.2] - 2021-05-30

[v1.0.2]: https://github.com/althonos/fs.smbfs/compare/v1.0.1...v1.0.2

### Added
- Explicit support for `v1.2.7` of PySMB.


## [v1.0.1] - 2021-04-12

[v1.0.1]: https://github.com/althonos/fs.smbfs/compare/v1.0.0...v1.0.1

### Fixed
- SMB share names are now matched case-insensitively ([#28](https://github.com/althonos/fs.smbfs/pull/28)).
- When created with `direct_tcp=True`, `SMBFS` will not attempt to use NetBIOS anymore to find a missing IP/hostname ([#25](https://github.com/althonos/fs.smbfs/pull/25)). Closes [#24](https://github.com/althonos/fs.smbfs/issues/24). 


## [v1.0.0] - 2021-01-31

[v1.0.0]: https://github.com/althonos/fs.smbfs/compare/v0.7.4...v1.0.0

### Added
- Explicit support for Python 3.9.
- This changelog file.
- `SMBFS.upload` (resp. `download`) implementation using the `SMBConnection.storeFile` (resp. `retrieveFile`) method.
- `SMBFS.geturl` implementation for the `download` purpose.
- `SMBFile.mode` property to expose the mode the file was created with.
- `SMBFile.readinto` method using a zero-copy implementation.

### Changed
- `SMBFS.openbin` will open a new connection for every new file.
- `SMBFS.readbytes` (resp. `writebytes`) now uses `SMBFS.download` (resp. `upload`).
- Mark the project as *Stable* in `setup.cfg` classifiers.
- Switched from Travis-CI and AppVeyor to GitHub Actions for continuous integration.
- Rewrote `README.rst` in Markdown format.


## [v0.7.4] - 2020-12-10

[v0.7.4]: https://github.com/althonos/fs.smbfs/compare/v0.7.3...v0.7.4

### Added
- Explicit support for `v1.2.6` of PySMB.


## [v0.7.3] - 2020-11-10

[v0.7.3]: https://github.com/althonos/fs.smbfs/compare/v0.7.2...v0.7.3

### Added
- Explicit support for `v1.2.5` of PySMB.


## [v0.7.2] - 2020-10-06

[v0.7.2]: https://github.com/althonos/fs.smbfs/compare/v0.7.1...v0.7.2

### Added
- Explicit support for `v1.2.4` of PySMB.


## [v0.7.1] - 2020-10-06

[v0.7.1]: https://github.com/althonos/fs.smbfs/compare/v0.7.0...v0.7.1

### Added
- Explicit support for `v1.2.3` of PySMB.


## [v0.7.0] - 2020-09-17

[v0.7.0]: https://github.com/althonos/fs.smbfs/compare/v0.6.4...v0.7.0

### Added
- `domain` argument to specify the Windows network domain in `SMBFS.__init__` (@Vegemash [#17](https://github.com/althonos/fs.smbfs/pull/17)).


## [v0.6.4] - 2020-09-05

[v0.6.4]: https://github.com/althonos/fs.smbfs/compare/v0.6.3...v0.6.4

### Fixed
- Make `SMBFS.close` method check for `_smb` attribute before calling `self._smb.close`.


## [v0.6.3] - 2020-05-20

[v0.6.3]: https://github.com/althonos/fs.smbfs/compare/v0.6.2...v0.6.3

### Added
- Explicit support for `v1.2.0` of PySMB.

### Removed
- Support for `v1.1.19` of PySMB.


## [v0.6.2] - 2020-05-13

[v0.6.2]: https://github.com/althonos/fs.smbfs/compare/v0.6.1...v0.6.2

### Added
- Note to `README.rst` that the `host` parameter to `SMBFS` should *not* a [FQDN](https://en.wikipedia.org/wiki/Fully_qualified_domain_name) (@mivade [#13](https://github.com/althonos/fs.smbfs/pull/13)).

### Fixed
- `SMBFS.__make_access_from_sd` incorrectly assuming that the *everyone* [ACE](https://docs.microsoft.com/en-us/windows/win32/secauthz/access-control-entries) exists (@telamonian [#11](https://github.com/althonos/fs.smbfs/pull/11))


## [v0.6.1] - 2020-04-14

[v0.6.1]: https://github.com/althonos/fs.smbfs/compare/v0.6.0...v0.6.1

### Added
- Explicit support for Python 3.8.

### Changed
- Delegate choice of default SMB port to PySMB (@telamonian [#10](https://github.com/althonos/fs.smbfs/pull/10))


## [v0.6.0] - 2020-04-14

[v0.6.0]: https://github.com/althonos/fs.smbfs/compare/v0.5.2...v0.6.0

### Added
- `hostname` argument support in SMB FS URLs (@telamonian [#7](https://github.com/althonos/fs.smbfs/pull/7)).

### Removed
- Python 3.4 support.


## [v0.5.2] - 2019-02-22

[v0.5.2]: https://github.com/althonos/fs.smbfs/compare/v0.5.1...v0.5.2

### Added
- Explicit support of the `v1.1.27` of PySMB.


## [v0.5.1] - 2019-02-11

[v0.5.1]: https://github.com/althonos/fs.smbfs/compare/v0.5.0...v0.5.1

### Added
- Explicit support of the `v2.3.0` of `fs`.


## [v0.5.0] - 2019-01-06

[v0.5.0]: https://github.com/althonos/fs.smbfs/compare/v0.4.0...v0.5.0

### Added
- Python 3.7 support.

### Changed
- Bumped minimum required `fs` version to `v2.2.0`.
- Mark PySMB `v1.1.26` as unsupported in `setup.cfg`.

### Removed
- Python 3.3 support.


## [v0.4.0] - 2018-08-13

[v0.4.0]: https://github.com/althonos/fs.smbfs/compare/v0.3.3...v0.4.0

### Added
- Option to pass a `(hostname, IP)` tuple as the `host` argument to `SMBFS.__init__`.

### Changed
- Bumped minimum required `fs` version to `v2.1.0`.


## [v0.3.3] - 2018-02-24

[v0.3.3]: https://github.com/althonos/fs.smbfs/compare/v0.3.2...v0.3.3

### Fixed
- `SMBOpener` not managing the `create` argument as expected.


## [v0.3.2] -2017-12-13

[v0.3.2]: https://github.com/althonos/fs.smbfs/compare/v0.3.1...v0.3.2

### Fixed
- `SMBFS.scandir` crashing when requesting access info from a SMB1 server.


## [v0.3.1] - 2017-12-13

[v0.3.1]: https://github.com/althonos/fs.smbfs/compare/v0.3.0...v0.3.1

### Fixed
- `SMBFS.getinfo` crashing when requesting access info from a SMB1 server.


## [v0.3.0] - 2017-10-23

[v0.3.0]: https://github.com/althonos/fs.smbfs/compare/v0.2.4...v0.3.0

### Added
- Support for FS URL parameters in `SMBOpener`.

### Fixed
- `direct_tcp` parameter being ignored in `SMBFS.__init__`.
- `SMBFS` always using guest account instead of provided username/password.
- `COPYING` file not being added to wheel distributions.
- Wrong info namespace being checked in `SMBFS.scandir`.
- Uncatched socket error on connection failure in `SMBFS.__init__`.


## [v0.2.4] - 2017-10-19

[v0.2.4]: https://github.com/althonos/fs.smbfs/compare/v0.2.3...v0.2.4

### Fixed
- `SMBConnection` not being closed by `SMBFS.close`.

### Changed
- Pinned minimum required `six` version to `v1.10` in `setup.cfg`.


## [v0.2.3] - 2017-09-18

[v0.2.3]: https://github.com/althonos/fs.smbfs/compare/v0.2.2...v0.2.3

### Changed
- Bumped `pysmb` version to `v1.1.22`.

### Removed
- Temporary `pysmb` bugfix for [miketeo/pysmb#90](https://github.com/miketeo/pysmb/issues/90.


## [v0.2.2] - 2017-09-13

[v0.2.2]: https://github.com/althonos/fs.smbfs/compare/v0.2.1...v0.2.2

### Fixed
- `SMBFile.truncate` changing the position in the file.
- Unicode paths not working properly ([miketeo/pysmb#90](https://github.com/miketeo/pysmb/issues/90)).


## [v0.2.1] - 2017-09-10

[v0.2.1]: https://github.com/althonos/fs.smbfs/compare/v0.2.0...v0.2.1

### Removed
- Invalid `SMBFile.__length_hint__` special method.
- Debug `print` call left in `SMBFS.openbin`.


## [v0.2.0] - 2017-08-29

[v0.2.0]: https://github.com/althonos/fs.smbfs/compare/v0.1.0...v0.2.0

### Added
- `SMBFS.move` implementation using the `SMBConnection.rename` method from PySMB.
- Missing module docstrings to `fs.smbfs` and `fs.opener.smbfs` modules.
- `__version__` attribute to `fs.opener.smbfs` module.

### Changed
- Use `fs.smbfs.utils.is_ip` to check if the host given to `SMBFS` is an IP address.

### Fixed
- `SMBFS.openbin` not raising `fs.errors.PermissionDenied` on SMB access errors.
- Broken `SMBFS` usage example in `README.rst`.


## [v0.1.0] - 2017-08-12

[v0.1.0]: https://github.com/althonos/fs.smbfs/compare/07b002c...v0.1.0

Initial commit.
