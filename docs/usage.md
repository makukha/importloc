```python
from importloc import Location
```


## Various locations

### Import from file

#### Syntax
```python
Location('app/config.py:conf').load()
```

#### Example
```doctest
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
