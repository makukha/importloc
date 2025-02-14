from doctest import ELLIPSIS, FAIL_FAST
import sys
from typing import Tuple
from unittest import TestCase

from doctestcase import doctestcase

from importloc import Location
from importloc.dirlay import DirectoryLayout, File


def app_layout() -> 'DirectoryLayout':
    return DirectoryLayout(
        files=(
            File(
                'app/__main__.py',
                'def cli(): ...',
            ),
            File(
                'app/config.py',
                'class Config:\n  class Nested: ...\nconf = Config()',
            ),
            File(
                'app/errors.py',
                'class Error1(Exception): ...\nclass Error2(Exception): ...',
            ),
        ),
    )


@doctestcase(globals={'Location': Location}, options=ELLIPSIS | FAIL_FAST)
class DirTestCase(TestCase):
    layout = app_layout()
    prevmodules: Tuple[str, ...]

    def setUp(self) -> None:
        if self.__class__ is DirTestCase:
            self.skipTest('base class')  # no tests of the base class itself
        self.layout.create()
        self.layout.chdir = self.__doctestcase__.kwargs.get('chdir', '.')  # type: ignore
        self.layout.pushd()
        sys.path.insert(0, str(self.layout.cwd))
        # remember modules present initially
        self.prevmodules = tuple(sys.modules.keys())

    def tearDown(self) -> None:
        sys.path.pop(0)
        self.layout.popd()
        self.layout.destroy()
        # delete modules imported during the test
        for m in tuple(sys.modules):
            if m not in self.prevmodules:
                del sys.modules[m]
        self.prevmodules = ()


# various locations


@doctestcase()
class L1(DirTestCase):
    """
    Import from file

    ```python
    Location('app/config.py:conf').load()
    ```

    >>> loc = Location('app/config.py:conf')
    >>> loc
    <PathLocation 'app/config.py' obj='conf'>
    >>> loc.load()
    <config.Config object at 0x...>
    """


@doctestcase()
class L2(DirTestCase):
    """
    Import from module

    ```python
    Location('app.__main__:cli').load()
    ```

    >>> loc = Location('app.__main__:cli')
    >>> loc
    <ModuleLocation 'app.__main__' obj='cli'>
    >>> loc.load()
    <function cli at 0x...>
    """


@doctestcase(chdir='app')
class L3(DirTestCase):
    """
    Distinguish file and module locations

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


@doctestcase()
class T1(DirTestCase):
    """
    Import nested class

    ```python
    Location('app/config.py:Config.Nested').load()
    ```

    >>> loc = Location('app/config.py:Config.Nested')
    >>> loc
    <PathLocation 'app/config.py' obj='Config.Nested'>
    >>> loc.load()
    <class 'config.Config.Nested'>
    """


@doctestcase()
class T2(DirTestCase):
    """
    Import module as a whole

    ```python
    Location('app/config.py').load()
    ```

    >>> loc = Location('app/config.py')
    >>> loc
    <PathLocation 'app/config.py'>
    >>> loc.load()
    <module 'config' from '...'>
    """


@doctestcase(chdir='app')
class T3(DirTestCase):
    """
    Use `Path` object when loading module

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


@doctestcase()
class T4(DirTestCase):
    """
    Import all instances of some type

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


@doctestcase()
class T5(DirTestCase):
    """
    Import all subclasses

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


@doctestcase()
class N1(DirTestCase):
    """
    Use different module name

    ```python
    Location('...').load(modname='app_main')
    ```

    >>> Location('app/config.py:Config').load(modname='app_main')
    <class 'app_main.Config'>
    """


@doctestcase()
class N2(DirTestCase):
    """
    Generate module name at run time

    ```python
    Location('...').load(modname=random_name)
    ```

    >>> from importloc import random_name
    >>> Location('app/config.py:Config').load(modname=random_name)
    <class 'u....Config'>
    """


# module name conflict resolution


@doctestcase()
class R1(DirTestCase):
    """
    Module name conflict raises error by default

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


@doctestcase()
class R2(DirTestCase):
    """
    Reuse module that is already imported

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


@doctestcase()
class R3(DirTestCase):
    """
    Reload module that is already imported

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


@doctestcase()
class R4(DirTestCase):
    """
    Replace old module with imported one

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


@doctestcase()
class R5(DirTestCase):
    """
    Load module under different generated name

    ```python
    Location('...').load(on_conflict='rename', rename=random_name)
    ```

    >>> from importloc import random_name
    >>> Location('app/config.py').load()
    <module 'config' from ...>
    >>> Location('app/config.py').load(on_conflict='rename', rename=random_name)
    <module 'u...'>
    """


@doctestcase()
class R6(DirTestCase):
    """
    Combine override and rename

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


@doctestcase()
class O1(DirTestCase):
    """
    Missing object causes `AttributeError`

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
