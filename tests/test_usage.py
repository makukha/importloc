from dataclasses import replace

from util import TestCase, DirectoryLayout, File


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

    >>> loc = Location('app/config.py:conf')
    >>> loc
    <PathLocation 'app/config.py' obj='conf'>
    >>> loc.load()
    <config.Config object at 0x...>
    """


class L2(TestCase, layout=app_layout):
    """Import from module

    >>> loc = Location('app.__main__:cli')
    >>> loc
    <ModuleLocation 'app.__main__' obj='cli'>
    >>> loc.load()
    <function cli at 0x...>
    """


class L3(TestCase, layout=replace(app_layout, chdir='app')):
    """Distinguish file and module locations

    With chdir to ./app

    >>> loc = Location('config.py:conf')
    >>> loc
    <ModuleLocation 'config.py' obj='conf'>
    >>> loc.load()
    Traceback (most recent call last):
        ...
    ModuleNotFoundError: No module named 'config.py'...

    Use explicitly relative path. Any path separator will result in `PathLocation`
    instead of `ModuleLocation`.

    >>> loc = Location('./config.py:conf')
    >>> loc
    <PathLocation 'config.py' obj='conf'>
    >>> loc.load()
    <config.Config object at 0x...>
    """


# various targets


class T1(TestCase, layout=app_layout):
    """Import nested class

    >>> loc = Location('app/config.py:Config.Nested')
    >>> loc
    <PathLocation 'app/config.py' obj='Config.Nested'>
    >>> loc.load()
    <class 'config.Config.Nested'>
    """


class T2(TestCase, layout=app_layout):
    """Import module as a whole

    >>> loc = Location('app/config.py')
    >>> loc
    <PathLocation 'app/config.py'>
    >>> loc.load()
    <module 'config' from '...'>
    """


class T3(TestCase, layout=replace(app_layout, chdir='app')):
    """Use `Path` object when loading module

    >>> from pathlib import Path
    >>> loc = Location(Path('config.py'))
    >>> loc
    <PathLocation 'config.py'>
    >>> loc.load()
    <module 'config' from '...'>
    """


class T4(TestCase, layout=app_layout):
    """Import all instances of a type

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

    >>> Location('app/config.py:Config').load(modname='app_main')
    <class 'app_main.Config'>
    """


class N2(TestCase, layout=app_layout):
    """Generate module name at run time

    >>> from importloc import random_name
    >>> Location('app/config.py:Config').load(modname=random_name)
    <class 'u....Config'>
    """


# module name conflict resolution


class R1(TestCase, layout=app_layout):
    """Module name conflict raises error by default

    >>> Location('app/config.py:Config').load()
    <class 'config.Config'>
    >>> Location('app/config.py:Config').load()
    Traceback (most recent call last):
        ...
    importloc.exc.ModuleNameConflict: Module "config" is already imported
    """


class R2(TestCase, layout=app_layout):
    """Reuse module that is already imported

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
    """Relad module that is already imported

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

    >>> import sys
    >>> C = Location('app/config.py:Config').load()
    >>> C
    <class 'config.Config'>
    >>> mod_id = id(sys.modules['config'])
    >>> C = Location('app/config.py:Config').load(on_conflict='replace')
    >>> C
    <class 'config.Config'>
    >>> # module object is the new one
    >>> id(sys.modules['config']) == mod_id
    False
    """


class R5(TestCase, layout=app_layout):
    """Load module under different generated name

    >>> from importloc import random_name
    >>> Location('app/config.py').load()
    <module 'config' from ...>
    >>> Location('app/config.py').load(on_conflict='rename', rename=random_name)
    <module 'u...'>
    """


class R6(TestCase, layout=app_layout):
    """Combine override and rename

    >>> from importloc import random_name
    >>> Location('app/config.py').load(modname='app_config')
    <module 'app_config' from ...>
    >>> Location('app/config.py').load(
    ...     modname='app_config', on_conflict='rename', rename=random_name
    ... )
    <module 'u...' from ...>
    """
