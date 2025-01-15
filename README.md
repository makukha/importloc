# importloc
> Import Python objects from arbitrary locations

<!-- docsub: begin -->
<!-- docsub: include docs/parts/badges.md -->
[![versions](https://img.shields.io/pypi/pyversions/importloc.svg)](https://pypi.org/project/importloc)
[![pypi](https://img.shields.io/pypi/v/importloc.svg#v0.1.0)](https://pypi.python.org/pypi/importloc)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![using docsub](https://img.shields.io/badge/using-docsub-royalblue)](https://github.com/makukha/docsub)
[![license](https://img.shields.io/github/license/makukha/importloc.svg)](https://github.com/makukha/importloc/blob/main/LICENSE)
<!-- docsub: end -->


# Features

* Import module from file `path/to/file.py`
* Import object from file `path/to/file.py:object[.attr...]`
* Import object from module `[...package.]module:object[.attr...]`
* No dependencies


# Installation
<!-- docsub: begin -->
<!-- docsub: include docs/parts/installation.md -->
```shell
$ pip install importloc
```
<!-- docsub: end -->


# Usage

For more details, [read the docs](http://importloc.readthedocs.io).

## [module_from_file](https://importloc.readthedocs.io/en/latest/#importloc.module_from_file)

<!-- docsub: begin -->
<!-- docsub: include tests/test_module_from_file.txt -->
<!-- docsub: lines after 1 upto -1 -->
```doctest
>>> from importloc import *
>>> foobar = module_from_file('example/foobar.py')
>>> foobar
<module 'foobar' from ...example/foobar.py'>
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


# Changelog

Check repository [CHANGELOG.md](https://github.com/makukha/importloc/tree/main/CHANGELOG.md)
