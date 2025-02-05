# importloc
<!-- docsub: begin -->
<!-- docsub: include docs/desc.md -->
> *Import Python objects from arbitrary locations specified by string.*
<!-- docsub: end -->

<!-- docsub: begin -->
<!-- docsub: include docs/badges.md -->
[![license](https://img.shields.io/github/license/makukha/importloc.svg)](https://github.com/makukha/importloc/blob/main/LICENSE)
[![pypi](https://img.shields.io/pypi/v/importloc.svg#v0.3.0)](https://pypi.python.org/pypi/importloc)
[![python versions](https://img.shields.io/pypi/pyversions/importloc.svg)](https://pypi.org/project/importloc)
[![tests](https://raw.githubusercontent.com/makukha/importloc/v0.3.0/docs/_static/badge-tests.svg)](https://github.com/makukha/importloc)
[![coverage](https://raw.githubusercontent.com/makukha/importloc/v0.3.0/docs/_static/badge-coverage.svg)](https://github.com/makukha/importloc)
[![tested with multipython](https://img.shields.io/badge/tested_with-multipython-x)](https://github.com/makukha/multipython)
[![using docsub](https://img.shields.io/badge/using-docsub-royalblue)](https://github.com/makukha/docsub)
[![mypy](https://img.shields.io/badge/type_checked-mypy-%231674b1)](http://mypy.readthedocs.io)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<!-- docsub: end -->


<!-- docsub: begin -->
<!-- docsub: include docs/features.md -->
# Features

* Minimalistic fully typed package
* Importable locations: files and named modules
* Handy helper utils
* Configurable resolution when module is already imported: `reuse`, `reload`, `replace`, `rename`, `raise`
* Atomic import: on `ImportError`, old module with the same name will be restored, and partially initialized module will be removed
<!-- docsub: end -->


# Installation

```shell
$ pip install importloc
```


# Usage

<!-- docsub: begin -->
<!-- docsub: include docs/usage.md -->
```python
from importloc import Location
```


## Various locations

### Import from file

````{note}
```python
Location('app/config.py:conf').load()
```
````

```pycon
>>> loc = Location('app/config.py:conf')
>>> loc
<PathLocation 'app/config.py' obj='conf'>
>>> loc.load()
<config.Config object at 0x...>
```

### Import from module

````{note}
```python
Location('app.__main__:cli').load()
```
````

```pycon
>>> loc = Location('app.__main__:cli')
>>> loc
<ModuleLocation 'app.__main__' obj='cli'>
>>> loc.load()
<function cli at 0x...>
```

### Distinguish file and module locations

````{note}
```python
Location('./config.py:conf').load()
```
````

```pycon
>>> loc = Location('config.py:conf')
>>> loc
<ModuleLocation 'config.py' obj='conf'>
>>> loc.load()
Traceback (most recent call last):
    ...
ModuleNotFoundError: No module named 'config.py'...
```

Use explicitly relative path. Path separator will result in `PathLocation`
instead of `ModuleLocation`.

```pycon
>>> loc = Location('./config.py:conf')
>>> loc
<PathLocation 'config.py' obj='conf'>
>>> loc.load()
<config.Config object at 0x...>
```


## Various targets

### Import nested class

````{note}
```python
Location('app/config.py:Config.Nested').load()
```
````

```pycon
>>> loc = Location('app/config.py:Config.Nested')
>>> loc
<PathLocation 'app/config.py' obj='Config.Nested'>
>>> loc.load()
<class 'config.Config.Nested'>
```

### Import module as a whole

````{note}
```python
Location('app/config.py').load()
```
````

```pycon
>>> loc = Location('app/config.py')
>>> loc
<PathLocation 'app/config.py'>
>>> loc.load()
<module 'config' from '...'>
```

### Use `Path` object when loading module

````{note}
```python
Location(Path('config.py')).load()
```
````

```pycon
>>> from pathlib import Path
>>> loc = Location(Path('config.py'))
>>> loc
<PathLocation 'config.py'>
>>> loc.load()
<module 'config' from '...'>
```

### Import all instances of some type

````{note}
```python
get_instances(Location('app.__main__').load(), Callable)
```
````

```pycon
>>> from collections.abc import Callable
>>> from importloc import get_instances
>>> loc = Location('app.__main__')
>>> loc
<ModuleLocation 'app.__main__'>
>>> get_instances(loc.load(), Callable)
[<function cli at 0x...>]
```

### Import all subclasses

````{note}
```python
get_subclasses(Location('app.errors').load(), Exception)
```
````

```pycon
>>> from importloc import get_subclasses
>>> loc = Location('app.errors')
>>> loc
<ModuleLocation 'app.errors'>
>>> get_subclasses(loc.load(), Exception)
[<class 'app.errors.Error1'>, <class 'app.errors.Error2'>]
```


## Custom module name

### Use different module name

````{note}
```python
Location('...').load(modname='app_main')
```
````

```pycon
>>> Location('app/config.py:Config').load(modname='app_main')
<class 'app_main.Config'>
```

### Generate module name at run time

````{note}
```python
Location('...').load(modname=random_name)
```
````

```pycon
>>> from importloc import random_name
>>> Location('app/config.py:Config').load(modname=random_name)
<class 'u....Config'>
```


## What if module is already imported?

The module name conflict can be resolved with one the methods:

* ``reuse`` existing module imported before
* ``reload`` existing module
* ``replace`` existing module
* ``rename`` new module (try to import under new name)
* ``raise`` exception (default)

For details, see documentation on [ConflictResolution](https://importloc.readthedocs.io/en/latest/api.html#ConflictResolution).

### Module name conflict raises error by default

````{note}
```python
Location('...').load()
```
````

```pycon
>>> Location('app/config.py:Config').load()
<class 'config.Config'>
>>> Location('app/config.py:Config').load()
Traceback (most recent call last):
    ...
importloc.exc.ModuleNameConflict: Module "config" is already imported
```

### Reuse module that is already imported

````{note}
```python
Location('...').load(on_conflict='reuse')
```
````

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

### Reload module that is already imported

````{note}
```python
Location('...').load(on_conflict='reload')
```
````

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

### Replace old module with imported one

````{note}
```python
Location('...').load(on_conflict='replace')
```
````

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

### Load module under different generated name

````{note}
```python
Location('...').load(on_conflict='rename', rename=random_name)
```
````

```pycon
>>> from importloc import random_name
>>> Location('app/config.py').load()
<module 'config' from ...>
>>> Location('app/config.py').load(on_conflict='rename', rename=random_name)
<module 'u...'>
```

### Combine override and rename

````{note}
```python
Location('...').load(modname='...', on_conflict='rename', rename=random_name)
```
````

```pycon
>>> from importloc import random_name
>>> Location('app/config.py').load(modname='app_config')
<module 'app_config' from ...>
>>> Location('app/config.py').load(
...     modname='app_config', on_conflict='rename', rename=random_name
... )
<module 'u...' from ...>
```


## What if object does not exist?

When module was imported but requested object does not exist, `AttributeError` is raised.
<!-- docsub: end -->

# See also

* [Similar implementations](https://importloc.readthedocs.io/en/latest/alternatives.html)
* [Project changelog](https://github.com/makukha/importloc/tree/main/CHANGELOG.md)
