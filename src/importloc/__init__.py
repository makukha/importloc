import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Union


__version__ = '0.1.1'
__all__ = [
    'module_from_file',
    'object_from_file',
    'object_from_module',
]


def module_from_file(
    path: Union[str, Path],
    modname: Union[str, None] = None,
    exist_ok: bool = False,
) -> ModuleType:
    """
    Create module from file.

    >>> foobar = module_from_file('example/foobar.py')
    >>> foobar
    <module 'foobar' from '.../example/foobar.py'>

    :param path:
        path to import as module

    :param modname:
        name to assign to module created, defaults to ``path`` stem

    :param exist_ok:
        if module ``modname`` already imported and ``exist_ok`` is ``True``,
        overwrite it, otherwise raise ``RuntimeError``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``modname`` can't be a module identifier
    :raises FileNotFoundError: when ``path`` does not exist
    :raises IsADirectoryError: when ``path`` is a directory
    :raises RuntimeError: when ``modname`` is already imported and ``exist_ok``
        is ``False``

    :return: Imported module object.

    .. versionadded:: 0.1.1
    """
    # todo: validate types

    # prepare path
    if isinstance(path, str):
        path = Path(path)
    path = path.resolve()

    # validate path
    if not path.exists():
        raise FileNotFoundError(f'Path "{path}" does not exist.')
    elif path.is_dir():
        raise IsADirectoryError(f'Path "{path}" is a directory.')

    # prepare modname
    if modname is None:
        modname = path.stem

    # validate modname
    if not modname.isidentifier():
        raise ValueError(f'"{modname}" is not a valid identifier.')
    elif modname in sys.modules and not exist_ok:
        raise ValueError(f'Module "{modname}" already imported.')

    # import
    spec = importlib.util.spec_from_file_location(modname, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Module "{modname}" cannot be imported.')
    mod_obj = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod_obj
    spec.loader.exec_module(mod_obj)

    return mod_obj


def object_from_file(
    pathspec: str,
    modname: Union[str, None] = None,
    exist_ok: bool = False,
) -> Any:
    """
    Load object from file.

    >>> baz = object_from_file('example/foobar.py:baz')
    >>> baz
    <function baz at 0x...>

    :param pathspec:
        import string in format ``path/to/file.py:object[.attr...]``

    :param modname:
        name to assign to module created, defaults to ``path`` stem

    :param exist_ok:
        if module ``modname`` already imported and ``exist_ok`` is ``True``,
        overwrite it, otherwise raise ``RuntimeError``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``pathspec`` is incorrect
    :raises ValueError: when ``modname`` can't be a module identifier
    :raises ValueError: when ``object`` is not a valid identifier
    :raises FileNotFoundError: when ``path/to/file`` does not exist
    :raises IsADirectoryError: when ``path/to/file`` is a directory
    :raises ImportError: when ``object`` is not defined in file
    :raises RuntimeError: when ``modname`` is already imported and ``exist_ok``
        is ``False``

    :return: Imported object.

    .. versionadded:: 0.1.1
    """
    # todo: validate types

    # parse pathspec
    path, _, objname = pathspec.partition(':')
    if not path or not objname:
        raise ValueError(
            f'Import string "{pathspec}" '
            'must be in format "path/to/file.py:object[.attr...]".'
        )

    validate_identifier(objname)
    mod_obj = module_from_file(path, modname=modname, exist_ok=exist_ok)
    return get_nested_object(mod_obj, objname)


def object_from_module(modspec: str) -> Any:
    """
    Load object from module.

    >>> baz = object_from_module('example.foobar:baz')
    >>> baz
    <function baz at 0x...>

    :param modspec:
        import string in format ``[...package.]module:object[.attr...]``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``modspec`` is incorrect
    :raises ValueError: when ``object`` is not a valid identifier
    :raises ImportError: when ``package.module`` cannot be imported
    :raises ImportError: when ``object`` is not defined in ``package.module``

    :return: Imported object.

    .. versionadded:: 0.1.1
    """
    # todo: validate types

    # parse modspec
    modname, _, objname = modspec.partition(':')
    if not modname or not objname:
        raise ValueError(
            f'Import string "{modspec}" must be in format '
            '"[...package.]module:object[.attr...]".'
        )

    validate_identifier(objname)
    mod_obj = importlib.import_module(modname)  # todo: add test modname in sys.modules
    return get_nested_object(mod_obj, objname)


# helpers


def validate_identifier(name: str) -> None:
    for part in name.split('.'):
        if not part.isidentifier():
            raise ValueError(f'"{name}" is not a valid identifier.')


def get_nested_object(mod_obj: ModuleType, name: str) -> Any:
    item = mod_obj
    for part in name.split('.'):
        if not part.isidentifier():
            raise ValueError(f'"{name}" is not a valid identifier.')
        try:
            item = getattr(item, part)
        except AttributeError as exc:
            raise ImportError(
                f'Object "{name}" not found in module "{mod_obj.__name__}".'
            ) from exc
    return item
