# Changelog

All notable changes to this project will be documented in this file based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

- See upcoming changes in [News directory](https://github.com/makukha/importloc/tree/main/NEWS.d)

<!-- towncrier release notes start -->

## [v0.3.1](https://github.com/makukha/importloc/releases/tag/v0.3.1) — 2025-02-06

***Fixed***

- `get_subclasses` returning the parent class itself ([#30](https://github.com/makukha/importloc/issues/30))
- `atomic_import` did not cover object retrieval ([#31](https://github.com/makukha/importloc/issues/31))
- `atomic import` did not store previous state correctly ([#31](https://github.com/makukha/importloc/issues/31))

***Docs***

- Usage docs are now generated from test cases ([#30](https://github.com/makukha/importloc/issues/30))


## [v0.3.0](https://github.com/makukha/importloc/releases/tag/v0.3.0) — 2025-02-05

***Breaking 🔥***

- Switched to class-based module organisation ([#26](https://github.com/makukha/importloc/issues/26))

***Removed 💨***

- Removed import functions ([#26](https://github.com/makukha/importloc/issues/26))

***Added 🌿***

- Test coverage and badges ([#24](https://github.com/makukha/importloc/issues/24))
- Module name conflict resolution strategies ([#26](https://github.com/makukha/importloc/issues/26))
- Module import is now atomic: previous state is restored on import error ([#26](https://github.com/makukha/importloc/issues/26))

***Docs***

- Added list of existing implementations ([#24](https://github.com/makukha/importloc/issues/24))

***Misc***

- Started using [Just](https://just.systems) ([#24](https://github.com/makukha/importloc/issues/24))
- Added pre-commit hooks ([#24](https://github.com/makukha/importloc/issues/24))


## [v0.2.0](https://github.com/makukha/importloc/releases/tag/v0.2.0) — 2025-01-18

***Breaking 🔥***

- Completely rethink naming ([#20](https://github.com/makukha/importloc/issues/20))

***Fixed:***

- Wrong exception type raised when module is already imported


## [v0.1.1](https://github.com/makukha/importloc/releases/tag/v0.1.1) — 2025-01-17

***Changed:***

- When importing module from file, path is resolved to absolute ([#7](https://github.com/makukha/importloc/issues/7))

***Docs:***

- Published documentation on [importloc.readthedocs.io](https://importloc.readthedocs.io) ([#4](https://github.com/makukha/importloc/issues/4))
- Added `sphinx.ext.viewcode` plugin to view source code ([#10](https://github.com/makukha/importloc/issues/10))
- Added changelog to readme ([#12](https://github.com/makukha/importloc/issues/12))
- Added ``sphinx-sitemap`` plugin for website sitemap ([#14](https://github.com/makukha/importloc/issues/14))
- Added API version history directives ([#15](https://github.com/makukha/importloc/issues/15))


## [v0.1.0](https://github.com/makukha/importloc/releases/tag/v0.1.0) — 2025-01-15

***Added 🌿***

- Initial release ([#1](https://github.com/makukha/importloc/issues/1))
