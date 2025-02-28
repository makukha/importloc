# importloc
<!-- docsub: begin -->
<!-- docsub: include docs/desc.md -->
> *Import Python objects from arbitrary locations specified by string.*
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/importloc.svg)](https://github.com/makukha/importloc/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/importloc.svg#v0.3.1)](https://pypi.python.org/pypi/importloc)
[![python versions](https://img.shields.io/pypi/pyversions/importloc.svg)](https://pypi.org/project/importloc)
[![tests](https://raw.githubusercontent.com/makukha/importloc/v0.3.1/docs/_static/badge-tests.svg)](https://github.com/makukha/importloc)
[![coverage](https://raw.githubusercontent.com/makukha/importloc/v0.3.1/docs/_static/badge-coverage.svg)](https://github.com/makukha/importloc)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![uses docsub](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/makukha/docsub/refs/heads/main/docs/badge/v1.json)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->


<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
# Features

* Minimalistic fully typed package
* Import from files or named modules
* Import deeply nested objects
* Import all instances or all subclasses
* Configurable module name conflict resolution
* Atomicity: on import error, new module is removed, and previous, if any, is restored
<!-- docsub: end -->


# Installation

```shell
$ pip install importloc
```


# Usage

<!-- docsub: begin #readme -->
<!-- docsub: include docs/usage.md -->
* Various locations
    <!-- docsub: begin -->
    <!-- docsub: x toc tests/test_usage.py 'L[0-9]' -->
    * [Import from file](#import-from-file)
    * [Import from module](#import-from-module)
    * [Distinguish file and module locations](#distinguish-file-and-module-locations)
    <!-- docsub: end -->
* Various targets
    <!-- docsub: begin -->
    <!-- docsub: x toc tests/test_usage.py 'T[0-9]' -->
    * [Import nested class](#import-nested-class)
    * [Import module as a whole](#import-module-as-a-whole)
    * [Use `Path` object when loading module](#use-path-object-when-loading-module)
    * [Import all instances of some type](#import-all-instances-of-some-type)
    * [Import all subclasses](#import-all-subclasses)
    <!-- docsub: end -->
* Custom module name
    <!-- docsub: begin -->
    <!-- docsub: x toc tests/test_usage.py 'N[0-9]' -->
    * [Use different module name](#use-different-module-name)
    * [Generate module name at run time](#generate-module-name-at-run-time)
    <!-- docsub: end -->
* What if module is already imported?
    <!-- docsub: begin -->
    <!-- docsub: x toc tests/test_usage.py 'R[0-9]' -->
    * [Module name conflict raises error by default](#module-name-conflict-raises-error-by-default)
    * [Reuse module that is already imported](#reuse-module-that-is-already-imported)
    * [Reload module that is already imported](#reload-module-that-is-already-imported)
    * [Replace old module with imported one](#replace-old-module-with-imported-one)
    * [Load module under different generated name](#load-module-under-different-generated-name)
    * [Combine override and rename](#combine-override-and-rename)
    <!-- docsub: end -->
* What if object does not exist?
    <!-- docsub: begin -->
    <!-- docsub: x toc tests/test_usage.py 'O[0-9]' -->
    * [Missing object causes `AttributeError`](#missing-object-causes-attribute-error)
    <!-- docsub: end -->


## Quick start

The main and most used entity is `Location`.

```python
from importloc import Location
```


## Various locations

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'L[0-9]' -->
## Import from file

```python
Location('app/config.py:conf').load()
```

```pycon
>>> loc = Location('app/config.py:conf')
>>> loc
<PathLocation 'app/config.py' obj='conf'>
>>> loc.load()
<config.Config object at 0x...>
```

## Import from module

```python
Location('app.__main__:cli').load()
```

```pycon
>>> loc = Location('app.__main__:cli')
>>> loc
<ModuleLocation 'app.__main__' obj='cli'>
>>> loc.load()
<function cli at 0x...>
```

## Distinguish file and module locations

```python
Location('./config.py:conf').load()
```

```pycon
>>> loc = Location('config.py:conf')
>>> loc
<ModuleLocation 'config.py' obj='conf'>
>>> loc.load()
Traceback (most recent call last):
    ...
ModuleNotFoundError: No module named 'config.py'...
```

Use relative path (similar to Docker bind mount). Path separator will result in
`PathLocation` instead of `ModuleLocation`.

```pycon
>>> loc = Location('./config.py:conf')
>>> loc
<PathLocation 'config.py' obj='conf'>
>>> loc.load()
<config.Config object at 0x...>
```

<!-- docsub: end -->


## Various targets

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'T[0-9]' -->
## Import nested class

```python
Location('app/config.py:Config.Nested').load()
```

```pycon
>>> loc = Location('app/config.py:Config.Nested')
>>> loc
<PathLocation 'app/config.py' obj='Config.Nested'>
>>> loc.load()
<class 'config.Config.Nested'>
```

## Import module as a whole

```python
Location('app/config.py').load()
```

```pycon
>>> loc = Location('app/config.py')
>>> loc
<PathLocation 'app/config.py'>
>>> loc.load()
<module 'config' from '...'>
```

## Use `Path` object when loading module

```python
Location(Path('config.py')).load()
```

```pycon
>>> from pathlib import Path
>>> loc = Location(Path('config.py'))
>>> loc
<PathLocation 'config.py'>
>>> loc.load()
<module 'config' from '...'>
```

## Import all instances of some type

```python
get_instances(Location('app.__main__').load(), Callable)
```

```pycon
>>> from collections.abc import Callable
>>> from importloc import get_instances
>>> loc = Location('app.__main__')
>>> loc
<ModuleLocation 'app.__main__'>
>>> get_instances(loc.load(), Callable)
[<function cli at 0x...>]
```

## Import all subclasses

```python
get_subclasses(Location('app.errors').load(), Exception)
```

```pycon
>>> from importloc import get_subclasses
>>> loc = Location('app.errors')
>>> loc
<ModuleLocation 'app.errors'>
>>> get_subclasses(loc.load(), Exception)
[<class 'app.errors.Error1'>, <class 'app.errors.Error2'>]
```

<!-- docsub: end -->


## Custom module name

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'N[0-9]' -->
## Use different module name

```python
Location('...').load(modname='app_main')
```

```pycon
>>> Location('app/config.py:Config').load(modname='app_main')
<class 'app_main.Config'>
```

## Generate module name at run time

```python
Location('...').load(modname=random_name)
```

```pycon
>>> from importloc import random_name
>>> Location('app/config.py:Config').load(modname=random_name)
<class 'u....Config'>
```

<!-- docsub: end -->


## What if module is already imported?

The module name conflict can be resolved with one the methods:

* ``reuse`` existing module imported before
* ``reload`` existing module
* ``replace`` existing module
* ``rename`` new module (try to import under new name)
* ``raise`` exception (default)

For details, see documentation on [ConflictResolution](https://importloc.readthedocs.io/en/latest/api.html#ConflictResolution).

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'R[0-9]' -->
## Module name conflict raises error by default

```python
Location('...').load()
```

```pycon
>>> Location('app/config.py:Config').load()
<class 'config.Config'>
>>> Location('app/config.py:Config').load()
Traceback (most recent call last):
    ...
importloc.exc.ModuleNameConflict: Module "config" is already imported
```

## Reuse module that is already imported

```python
Location('...').load(on_conflict='reuse')
```

```pycon
>>> C = Location('app/config.py:Config').load()
>>> C
<class 'config.Config'>
>>> old_id = id(C)
>>> C = Location('app/config.py:Config').load(on_conflict='reuse')
>>> C
<class 'config.Config'>
>>> # C is the same object:
>>> id(C) == old_id
True
```

## Reload module that is already imported

```python
Location('...').load(on_conflict='reload')
```

```pycon
>>> import sys
>>> C = Location('app/config.py:Config').load()
>>> C
<class 'config.Config'>
>>> old_id = id(C)
>>> mod_id = id(sys.modules['config'])
>>> C = Location('app/config.py:Config').load(on_conflict='reload')
>>> C
<class 'config.Config'>
>>> # module object remains the same after reloading:
>>> id(sys.modules['config']) == mod_id
True
>>> # C is the new object from reloaded module:
>>> id(C) == old_id
False
```

## Replace old module with imported one

```python
Location('...').load(on_conflict='replace')
```

```pycon
>>> import sys
>>> C = Location('app/config.py:Config').load()
>>> C
<class 'config.Config'>
>>> mod_id = id(sys.modules['config'])
>>> C = Location('app/config.py:Config').load(on_conflict='replace')
>>> C
<class 'config.Config'>
>>> # module object is the new one:
>>> id(sys.modules['config']) == mod_id
False
```

## Load module under different generated name

```python
Location('...').load(on_conflict='rename', rename=random_name)
```

```pycon
>>> from importloc import random_name
>>> Location('app/config.py').load()
<module 'config' from ...>
>>> Location('app/config.py').load(on_conflict='rename', rename=random_name)
<module 'u...'>
```

## Combine override and rename

```python
Location('...').load(modname='...', on_conflict='rename', rename=random_name)
```

```pycon
>>> from importloc import random_name
>>> Location('app/config.py').load(modname='app_config')
<module 'app_config' from ...>
>>> Location('app/config.py').load(
...     modname='app_config', on_conflict='rename', rename=random_name
... )
<module 'u...' from ...>
```

<!-- docsub: end -->


## What if object does not exist?

<!-- docsub: begin -->
<!-- docsub: x cases tests/test_usage.py 'O[0-9]' -->
## Missing object causes `AttributeError`

When module was imported but requested object does not exist, `AttributeError`
is raised.

```pycon
>>> Location('app/config.py:unknown').load()
Traceback (most recent call last):
    ...
AttributeError: object has no attribute 'unknown'
>>> # due to import atomicity, module 'config' was removed
>>> import sys
>>> 'config' in sys.modules
False
```

<!-- docsub: end -->

<!-- docsub: end #readme -->

# See also

* [Similar implementations](https://importloc.readthedocs.io/en/latest/alternatives.html)
* [Project changelog](https://github.com/makukha/importloc/tree/main/CHANGELOG.md)
