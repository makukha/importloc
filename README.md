# importloc
> Import Python objects from arbitrary locations

<!-- docsub: begin -->
<!-- docsub: include docs/parts/badges.md -->
[![versions](https://img.shields.io/pypi/pyversions/importloc.svg)](https://pypi.org/project/importloc)
[![pypi](https://img.shields.io/pypi/v/importloc.svg#v0.2.0)](https://pypi.python.org/pypi/importloc)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![using docsub](https://img.shields.io/badge/using-docsub-royalblue)](https://github.com/makukha/docsub)
[![license](https://img.shields.io/github/license/makukha/importloc.svg)](https://github.com/makukha/importloc/blob/main/LICENSE)
<!-- docsub: end -->


# Features

* Import module from file `path/to/file.py`
* Import object from file `path/to/file.py:[parent.[...].]object`
* Import object from module `[pkg.[...].]module:[parent.[...].]object`
* No dependencies
* 100% test coverage *(to be implemented)*
* [Detailed documentation](http://importloc.readthedocs.io)


# Installation
<!-- docsub: begin -->
<!-- docsub: include docs/parts/installation.md -->
```shell
$ pip install importloc
```
<!-- docsub: end -->


# Usage

## [import_module_from_file](https://importloc.readthedocs.io/en/latest/#importloc.import_module_from_file)

<!-- docsub: begin -->
<!-- docsub: include tests/test_module_from_file.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> foobar = import_module_from_file('example/foobar.py', replace=True)
>>> foobar
<module 'foobar' from '/.../example/foobar.py'>
```
<!-- docsub: end -->

## [import_object_from_file](https://importloc.readthedocs.io/en/latest/#importloc.import_object_from_file)

<!-- docsub: begin -->
<!-- docsub: include tests/test_object_from_file.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> baz = import_object_from_file('example/foobar.py:baz', replace=True)
>>> baz
<function baz at 0x...>
```
<!-- docsub: end -->

## [import_object_from_module](https://importloc.readthedocs.io/en/latest/#importloc.import_object_from_module)

<!-- docsub: begin -->
<!-- docsub: include tests/test_object_from_module.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> baz = import_object_from_module('example.foobar:baz', replace=True)
>>> baz
<function baz at 0x...>
```
<!-- docsub: end -->


<!-- docsub: begin -->
<!-- docsub: include CHANGELOG.md -->
# Changelog

All notable changes to this project will be documented in this file. Changes for the *upcoming release* can be found in [News directory](https://github.com/makukha/importloc/tree/main/NEWS.d).

* The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
* This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)

<!-- towncrier release notes start -->

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
<!-- docsub: end -->
