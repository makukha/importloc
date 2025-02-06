from dataclasses import replace

from importloc.testing import TestCase, DirectoryLayout, File


app_layout = DirectoryLayout(
    files=(
        File('app/__main__.py', 'def cli(): ...'),
        File('app/config.py', 'class Config:\n  class Nested: ...\nconf = Config()'),
        File(
            'app/errors.py',
            'class Error1(Exception): ...\nclass Error2(Exception): ...',
        ),
    ),
)


# various locations


class L1(TestCase, layout=app_layout):
    """Import from file

    ```python
    Location('app/config.py:conf').load()
    ```

    >>> loc = Location('app/config.py:conf')
    >>> loc
    <PathLocation 'app/config.py' obj='conf'>
    >>> loc.load()
    <config.Config object at 0x...>
    """


class L2(TestCase, layout=app_layout):
    """Import from module

    ```python
    Location('app.__main__:cli').load()
    ```

    >>> loc = Location('app.__main__:cli')
    >>> loc
    <ModuleLocation 'app.__main__' obj='cli'>
    >>> loc.load()
    <function cli at 0x...>
    """


class L3(TestCase, layout=replace(app_layout, chdir='app')):
    """Distinguish file and module locations

    ```python
    Location('./config.py:conf').load()
    ```

    >>> loc = Location('config.py:conf')
    >>> loc
    <ModuleLocation 'config.py' obj='conf'>
    >>> loc.load()
    Traceback (most recent call last):
        ...
    ModuleNotFoundError: No module named 'config.py'...

    Use relative path (similar to Docker bind mount). Path separator will result in
    `PathLocation` instead of `ModuleLocation`.

    >>> loc = Location('./config.py:conf')
    >>> loc
    <PathLocation 'config.py' obj='conf'>
    >>> loc.load()
    <config.Config object at 0x...>
    """


# various targets


class T1(TestCase, layout=app_layout):
    """Import nested class

    ```python
    Location('app/config.py:Config.Nested').load()
    ```

    >>> loc = Location('app/config.py:Config.Nested')
    >>> loc
    <PathLocation 'app/config.py' obj='Config.Nested'>
    >>> loc.load()
    <class 'config.Config.Nested'>
    """


class T2(TestCase, layout=app_layout):
    """Import module as a whole

    ```python
    Location('app/config.py').load()
    ```

    >>> loc = Location('app/config.py')
    >>> loc
    <PathLocation 'app/config.py'>
    >>> loc.load()
    <module 'config' from '...'>
    """


class T3(TestCase, layout=replace(app_layout, chdir='app')):
    """Use `Path` object when loading module

    ```python
    Location(Path('config.py')).load()
    ```

    >>> from pathlib import Path
    >>> loc = Location(Path('config.py'))
    >>> loc
    <PathLocation 'config.py'>
    >>> loc.load()
    <module 'config' from '...'>
    """


class T4(TestCase, layout=app_layout):
    """Import all instances of some type

    ```python
    get_instances(Location('app.__main__').load(), Callable)
    ```

    >>> from collections.abc import Callable
    >>> from importloc import get_instances
    >>> loc = Location('app.__main__')
    >>> loc
    <ModuleLocation 'app.__main__'>
    >>> get_instances(loc.load(), Callable)
    [<function cli at 0x...>]
    """


class T5(TestCase, layout=app_layout):
    """Import all subclasses

    ```python
    get_subclasses(Location('app.errors').load(), Exception)
    ```

    >>> from importloc import get_subclasses
    >>> loc = Location('app.errors')
    >>> loc
    <ModuleLocation 'app.errors'>
    >>> get_subclasses(loc.load(), Exception)
    [<class 'app.errors.Error1'>, <class 'app.errors.Error2'>]
    """


# override default module name


class N1(TestCase, layout=app_layout):
    """Use different module name

    ```python
    Location('...').load(modname='app_main')
    ```

    >>> Location('app/config.py:Config').load(modname='app_main')
    <class 'app_main.Config'>
    """


class N2(TestCase, layout=app_layout):
    """Generate module name at run time

    ```python
    Location('...').load(modname=random_name)
    ```

    >>> from importloc import random_name
    >>> Location('app/config.py:Config').load(modname=random_name)
    <class 'u....Config'>
    """


# module name conflict resolution


class R1(TestCase, layout=app_layout):
    """Module name conflict raises error by default

    ```python
    Location('...').load()
    ```

    >>> Location('app/config.py:Config').load()
    <class 'config.Config'>
    >>> Location('app/config.py:Config').load()
    Traceback (most recent call last):
        ...
    importloc.exc.ModuleNameConflict: Module "config" is already imported
    """


class R2(TestCase, layout=app_layout):
    """Reuse module that is already imported

    ```python
    Location('...').load(on_conflict='reuse')
    ```

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
    """


class R3(TestCase, layout=app_layout):
    """Reload module that is already imported

    ```python
    Location('...').load(on_conflict='reload')
    ```

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
    """


class R4(TestCase, layout=app_layout):
    """Replace old module with imported one

    ```python
    Location('...').load(on_conflict='replace')
    ```

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
    """


class R5(TestCase, layout=app_layout):
    """Load module under different generated name

    ```python
    Location('...').load(on_conflict='rename', rename=random_name)
    ```

    >>> from importloc import random_name
    >>> Location('app/config.py').load()
    <module 'config' from ...>
    >>> Location('app/config.py').load(on_conflict='rename', rename=random_name)
    <module 'u...'>
    """


class R6(TestCase, layout=app_layout):
    """Combine override and rename

    ```python
    Location('...').load(modname='...', on_conflict='rename', rename=random_name)
    ```

    >>> from importloc import random_name
    >>> Location('app/config.py').load(modname='app_config')
    <module 'app_config' from ...>
    >>> Location('app/config.py').load(
    ...     modname='app_config', on_conflict='rename', rename=random_name
    ... )
    <module 'u...' from ...>
    """


class O1(TestCase, layout=app_layout):
    """Missing object causes `AttributeError`

    When module was imported but requested object does not exist, `AttributeError`
    is raised.

    >>> Location('app/config.py:unknown').load()
    Traceback (most recent call last):
        ...
    AttributeError: object has no attribute 'unknown'
    >>> # due to import atomicity, module 'config' was removed
    >>> import sys
    >>> 'config' in sys.modules
    False
    """
