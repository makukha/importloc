# importloc
> Import Python objects from arbitrary locations

<!-- docsub: begin -->
<!-- docsub: include docs/parts/badges.md -->
[![versions](https://img.shields.io/pypi/pyversions/importloc.svg)](https://pypi.org/project/importloc)
[![pypi](https://img.shields.io/pypi/v/importloc.svg#v0.1.1)](https://pypi.python.org/pypi/importloc)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![using docsub](https://img.shields.io/badge/using-docsub-royalblue)](https://github.com/makukha/docsub)
[![license](https://img.shields.io/github/license/makukha/importloc.svg)](https://github.com/makukha/importloc/blob/main/LICENSE)
<!-- docsub: end -->


# Features

* Import module from file `path/to/file.py`
* Import object from file `path/to/file.py:object[.attr...]`
* Import object from module `[...package.]module:object[.attr...]`
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

## [module_from_file](https://importloc.readthedocs.io/en/latest/#importloc.module_from_file)

<!-- docsub: begin -->
<!-- docsub: include tests/test_module_from_file.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> foobar = module_from_file('example/foobar.py')
>>> foobar
<module 'foobar' from '/.../example/foobar.py'>
```
<!-- docsub: end -->

## [object_from_file](https://importloc.readthedocs.io/en/latest/#importloc.object_from_file)

<!-- docsub: begin -->
<!-- docsub: include tests/test_object_from_file.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> baz = object_from_file('example/foobar.py:baz')
>>> baz
<function baz at 0x...>
```
<!-- docsub: end -->

## [object_from_module](https://importloc.readthedocs.io/en/latest/#importloc.object_from_module)

<!-- docsub: begin -->
<!-- docsub: include tests/test_object_from_module.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> baz = object_from_module('example.foobar:baz')
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
