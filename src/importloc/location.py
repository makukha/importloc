r"""
To use any of supported concrete location types, use *generic* `Location` class.
Upon construction, it will return one of *specific* location objects supported:
`ModuleLocation` or `PathLocation`. Alternatively, construct *specific* location types
directly to enforce corresponding location type.

.. list-table::
    :header-rows: 1
    :align: left

    * - Location
      - Format
    * - `PathLocation`
      - ``(?P<path>.*/[^/]*\.py)(:(?P<obj>[^./:]+(?:\.[^./:]+)*))?``
    * - `ModuleLocation`
      - ``(?P<module>[^./:]+(?:\.[^./:]+)*)(:(?P<obj>[^./:]+(?:\.[^./:]+)*))?``

.. list-table::
    :header-rows: 1
    :align: left

    * - Location
      - Examples
    * - `PathLocation`
      - ``svc1/main.py:app``, ``svc1/exceptions.py``, ``../config.py``
    * - `ModuleLocation`
      - ``app.__main__:cli``, ``logging:StreamHandler``

.. raw:: html
    :file: ../../docs/_static/classes-dark.svg
    :class: only-dark

.. raw:: html
    :file: ../../docs/_static/classes-default.svg
    :class: only-light

"""

from contextlib import contextmanager
from enum import Enum
import importlib.util
from importlib.machinery import ModuleSpec
from pathlib import Path
import re
import sys
from types import ModuleType
from typing import Any, Callable, Iterable, Literal, Optional, Tuple, TypeVar, Union

from typing_extensions import Self, override

from .exc import InvalidLocation, ModuleNameConflict
from .util import getattr_nested


_OBJ = r'[^./:]+(?:\.[^./:]+)*'
_PYPATH = r'.*/[^/]*\.py'


class ConflictResolution(str, Enum):
    """
    Conflict resolution strategy when module with given name is already imported.
    """

    #: Don't import again, use existing module from `sys.modules`.
    REUSE = 'reuse'
    #: Don't import again, apply `importlib.reload` to existing module in `sys.modules`.
    RELOAD = 'reload'
    #: Delete existing module and use the imported one.
    REPLACE = 'replace'
    #: Retry module import with new generated name, and raise
    #: `~importloc.exc.ModuleNameConflict` exception if conflict appears again.
    RENAME = 'rename'
    #: Raise `~importloc.exc.ModuleNameConflict` exception.
    RAISE = 'raise'


class Location:
    """
    __init__(self, spec: str) -> Union[ModuleLocation, PathLocation]

    Arbitrary importable location.

    :param spec:
        location specification string.

    :raises InvalidLocation:
        when location string format is incorrect.

    """

    spec: str
    obj: Optional[str]

    def __new__(cls, spec: str) -> Union['ModuleLocation', 'PathLocation']:  # type: ignore[misc]
        for cls in (ModuleLocation, PathLocation):
            loc = cls.from_spec(spec)
            if loc:
                return loc
        raise InvalidLocation(spec)

    @classmethod
    def from_spec(cls, spec: str) -> Optional[Self]:
        """
        Create location object from specification string, if possible.

        :param spec:
            location specification string.
        """
        for loc in (ModuleLocation, PathLocation):
            match = loc.match(spec)
            if match:
                return cls(**match.groupdict())
        return None

    def load(
        self,
        module_name: Union[str, Callable[[Self], str], None] = None,
        on_conflict: Union[ConflictResolution, str] = 'raise',
        retry_name: Optional[Callable[[Self], str]] = None,
    ) -> Union[object, ModuleType]:
        """
        Import requested object or the whole module object from location.

        This operation is atomic:

        * on import error, previous module with the same name is restored
        * on import error, new partially initialized module is removed from `sys.modules`

        :param module_name:
            name under which the module will be imported; if `str`,
            use ``module_name`` itself; if `~typing.Callable`, use result of
            calling ``module_name()`` with current `Location` object;
            otherwise, use default value (see `ModuleLocation.load`
            and `PathLocation.load` for details).

        :param on_conflict:
            behaviour if ``module_name`` is already present in `sys.modules`
            (see `ConflictResolution` for details).

        :param retry_name:
            callable used to generate new module name on name conflict and if
            ``on_conflict`` is ``rename``.

        :raises TypeError | ValueError:
            when passed arguments of wrong type.
        :raises ModuleNameConflict:
            see `ConflictResolution` for details.
        :raises Exception:
            see specific location classes.

        :return:
            `object` when ``obj`` part was specified, otherwise `~types.ModuleType`.
        """
        raise NotImplementedError

    # error helpers with unified error messages

    @staticmethod
    def _args_denied_with_spec() -> ValueError:
        return ValueError('Other arguments are not allowed when spec is passed')

    @staticmethod
    def _arg_required_with_no_spec(arg: str) -> ValueError:
        return ValueError(f'Argument {arg} is required when spec is not passed')

    @staticmethod
    def _import_error(module_name: str) -> ImportError:
        return ImportError(f'Module "{module_name}" cannot be imported')


class ModuleLocation(Location):
    """
    Package-based importable location, e.g. ``foo.bar:obj``
    """

    module: str
    RX = re.compile(rf'^(?P<module>{_OBJ})(?::(?P<obj>{_OBJ}))?$')

    # bypass Location.__new__
    def __new__(cls, *args: Any, **kwargs: Any) -> 'ModuleLocation':
        return object.__new__(cls)

    def __init__(
        self,
        spec: Optional[str] = None,
        *,
        module: Optional[str] = None,
        obj: Optional[str] = None,
    ) -> None:
        """
        :param spec:
            location specification string; if ``spec`` is passed, other arguments
            must be absent or `None`.

        :param module:
            importable module name; required, if ``spec`` is not passed.

        :param obj:
            dot-separated object name to be imported; when missing, the whole module
            will be loaded

        :raises ValueError:
            when passed incorrect arguments.
        :raises InvalidLocation:
            when location string format is incorrect.
        """
        if spec is not None:
            if module is not None or obj is not None:
                raise self._args_denied_with_spec()
            match = self.match(spec)
            if match is None:
                raise InvalidLocation(spec)
            self.spec = spec
            self.module = match.group('module')
            self.obj = match.groupdict().get('obj', None)
        else:
            if module is None:
                raise self._arg_required_with_no_spec('module')
            self.module = module
            self.obj = obj
            self.spec = module if self.obj is None else f'{self.module}:{self.obj}'

    @classmethod
    def from_spec(cls, spec: str) -> Optional[Self]:
        """
        Create module-based location object from specification string.

        :param spec:
            location specification string.
        """
        match = cls.match(spec)
        if match:
            return cls(**match.groupdict())
        return None

    @classmethod
    def match(cls, spec: str) -> Optional[re.Match[str]]:
        """
        Match location specification string with corresponding regular expression.

        :param spec:
            location specification string.
        """
        return cls.RX.match(spec)

    @override
    def load(
        self,
        module_name: Union[str, Callable[[Self], str], None] = None,
        on_conflict: Union[ConflictResolution, str] = 'raise',
        retry_name: Optional[Callable[[Self], str]] = None,
    ) -> Union[object, ModuleType]:
        """
        Import requested object or the whole module object from importable module.

        This operation is atomic:

        * on import error, previous module with the same name is restored
        * on import error, new partially initialized module is removed from `sys.modules`

        :param module_name:
            name under which the module will be imported; if `str`,
            use ``module_name`` itself; if `~typing.Callable`, use result of
            calling ``module_name()`` with current `Location` object;
            by default, use ``module`` from ``spec``.

        :param on_conflict:
            behaviour if ``module_name`` is already present in `sys.modules`
            (see `ConflictResolution` for details).

        :param retry_name:
            callable used to generate new module name on name conflict and if
            ``on_conflict`` is ``rename``.

        :raises TypeError | ValueError:
            when passed arguments of wrong type.
        :raises ModuleNameConflict:
            see `ConflictResolution` for details.
        :raises ModuleNotFoundError:
            when ``module_name`` is not discoverable.
        :raises ImportError:
            when module import fails.
        :raises AttributeError:
            when ``obj`` name can't be found in imported module.

        :return:
            `object` when ``obj`` part was specified, otherwise `~types.ModuleType`.
        """
        modname, action = resolve_module_name(
            default=self.module,
            override=module_name,
            on_conflict=on_conflict,
            retry_name=retry_name,
            loc=self,
        )
        # import module
        if action == 'import':
            with atomic_import(modname):
                try:
                    modobj = importlib.import_module(modname)
                except ModuleNotFoundError as exc:
                    raise exc
                except Exception as exc:
                    raise self._import_error(modname) from exc
        elif action == 'use':
            modobj = sys.modules[modname]
        else:
            raise RuntimeError('unreachable')
        # get object
        if self.obj is None:
            return modobj
        else:
            return getattr_nested(modobj, self.obj)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        if self.obj is None:
            return '<{} {!r}>'.format(cls, self.module)
        else:
            return '<{} {!r} obj={!r}>'.format(cls, self.module, self.obj)


class PathLocation(Location):
    """
    __init__(self, spec: str) -> None
    __init__(self, *, path: Union[Path, str], obj: Optional[str] = None) -> None

    Filesystem-based importable location, e.g. ``foo/bar.py:obj``

    >>> loc = PathLocation('example/foobar.py:Parent.Nested')
    <PathLocation 'example/foobar.py:Parent.Nested'>
    >>> loc.load()
    <module 'foobar' from '.../example/foobar.py'>
    """

    path: Path
    RX = re.compile(rf'^(?P<path>{_PYPATH})(?::(?P<obj>{_OBJ}))?$')

    # bypass Location.__new__
    def __new__(cls, *args: Any, **kwargs: Any) -> 'PathLocation':
        return object.__new__(cls)

    def __init__(
        self,
        spec: Optional[str] = None,
        *,
        path: Union[Path, str, None] = None,
        obj: Optional[str] = None,
    ) -> None:
        """
        :param spec:
            location specification string; if ``spec`` is passed, other arguments
            must be absent or `None`.

        :param path:
            path to python source file to import from; required, if ``spec`` is
            not passed.

        :param obj:
            dot-separated object name to be imported; when missing, the whole file
            will be imported as module

        :raises ValueError:
            when passed incorrect arguments.
        :raises InvalidLocation:
            when location string format is incorrect.
        """
        if spec is not None:
            if path is not None or obj is not None:
                raise self._args_denied_with_spec()
            match = self.match(spec)
            if match is None:
                raise InvalidLocation(spec)
            self.spec = spec
            self.path = Path(match.group('path'))
            self.obj = match.groupdict().get('obj', None)
        else:
            if path is None:
                raise self._arg_required_with_no_spec('path')
            self.path = Path(path)
            self.obj = obj
            self.spec = str(path) if self.obj is None else f'{self.path}:{self.obj}'

    @classmethod
    def from_spec(cls, spec: str) -> Optional[Self]:
        """
        Create path-based location object from specification string.

        :param spec:
            location specification string.
        """
        match = cls.match(spec)
        if match:
            return cls(**match.groupdict())
        return None

    @classmethod
    def match(cls, spec: str) -> Optional[re.Match[str]]:
        """
        Match location specification string with corresponding regular expression.

        :param spec:
            location specification string.
        """
        return cls.RX.match(spec)

    @override
    def load(
        self,
        module_name: Union[str, Callable[[Self], str], None] = None,
        on_conflict: Union[ConflictResolution, str] = 'raise',
        retry_name: Optional[Callable[[Self], str]] = None,
    ) -> Union[object, ModuleType]:
        """
        Import requested object or the whole module object from location.

        This operation is atomic:

        * on import error, previous module with the same name is restored
        * on import error, new partially initialized module is removed from `sys.modules`

        :param module_name:
            name under which the module will be imported; if `str`,
            use ``module_name`` itself; if `~typing.Callable`, use result of
            calling ``module_name()`` with current `Location` object;
            by default, use ``path`` stem from ``spec``.

        :param on_conflict:
            behaviour if ``module_name`` is already present in `sys.modules`
            (see `ConflictResolution` for details).

        :param retry_name:
            callable used to generate new module name on name conflict and if
            ``on_conflict`` is ``rename``.

        :raises TypeError | ValueError:
            when passed arguments of wrong type.
        :raises ModuleNameConflict:
            see `ConflictResolution` for details.
        :raises FileNotFoundError:
            when ``path`` does not exist.
        :raises IsADirectoryError:
            when ``path`` is a directory.
        :raises ImportError:
            when module import fails.
        :raises AttributeError:
            when ``obj`` name can't be found in imported module.

        :return:
            `object` when ``obj`` part was specified, otherwise `~types.ModuleType`.
        """
        modname, action = resolve_module_name(
            default=self.path.stem,
            override=module_name,
            on_conflict=on_conflict,
            retry_name=retry_name,
            loc=self,
        )
        # validate path
        path = self.path.resolve()
        if not path.exists():
            raise FileNotFoundError(f'Path "{path}" does not exist.')
        elif path.is_dir():
            raise IsADirectoryError(f'Path "{path}" is a directory.')
        # import module
        if action == 'import':
            with atomic_import(modname):
                spec = importlib.util.spec_from_file_location(modname, path)
                if spec is None or spec.loader is None:
                    raise self._import_error(modname)
                try:
                    modobj = load_from_spec(spec)
                except Exception as exc:
                    raise self._import_error(modname) from exc
        elif action == 'use':
            modobj = sys.modules[modname]
        else:
            raise RuntimeError('unreachable')
        # get object
        if self.obj is None:
            return modobj
        else:
            return getattr_nested(modobj, self.obj)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        if self.obj is None:
            return '<{} {!r}>'.format(cls, str(self.path))
        else:
            return '<{} {!r} obj={!r}>'.format(cls, str(self.path), self.obj)


# undocumented helpers


@contextmanager
def atomic_import(modname: str) -> Any:
    old = {m: sys.modules.get(m, None) for m in explode_module_name(modname)}
    try:
        yield
    except Exception:
        for name, value in old.items():
            if value is not None:
                sys.modules[name] = value
            elif name in sys.modules:
                del sys.modules[name]
        raise


def load_from_spec(spec: ModuleSpec) -> ModuleType:
    modobj = importlib.util.module_from_spec(spec)
    modobj.__importloc_spec__ = spec  # type: ignore[attr-defined]
    sys.modules[spec.name] = modobj
    if spec.loader is None:
        raise ImportError(f'Loader not provided for module {spec.name}')
    spec.loader.exec_module(modobj)
    return modobj


def reload(modobj: ModuleType) -> None:
    spec = getattr(modobj, '__importloc_spec__', None)
    if spec:
        spec.loader.exec_module(modobj)
    else:
        importlib.reload(modobj)


L = TypeVar('L', bound=Location)


def resolve_module_name(
    default: str,
    override: Union[str, Callable[[L], str], None],
    on_conflict: Union[ConflictResolution, str],
    retry_name: Optional[Callable[[L], str]],
    loc: L,
) -> Tuple[str, Literal['use', 'import']]:
    # validate args
    on_conflict = ConflictResolution(on_conflict)
    if on_conflict == ConflictResolution.RENAME and not callable(retry_name):
        raise ValueError('retry_name must be callable')

    # determine initial module name
    if override is None:
        modname = default
    elif isinstance(override, str):
        modname = override
    elif callable(override):
        modname = override(loc)
    else:
        raise ValueError(f'Unexpected module_name override type {type(override)}')

    # module already imported?
    if modname not in sys.modules:
        return modname, 'import'

    # resolve
    if on_conflict == ConflictResolution.REUSE:
        return modname, 'use'
    elif on_conflict == ConflictResolution.RELOAD:
        reload(sys.modules[modname])
        return modname, 'use'
    elif on_conflict == ConflictResolution.REPLACE:
        return modname, 'import'
    elif on_conflict == ConflictResolution.RENAME:
        modname = retry_name(loc)  # type: ignore # checked above
        if modname in sys.modules:
            raise ModuleNameConflict(modname)
        return modname, 'import'
    elif on_conflict == ConflictResolution.RAISE:
        raise ModuleNameConflict(modname)
    else:
        raise RuntimeError('unreachable')


def explode_module_name(modname: str) -> Iterable[str]:
    end = 0
    while end != -1:
        end = modname.find('.', end + 1)
        yield modname[:end]
