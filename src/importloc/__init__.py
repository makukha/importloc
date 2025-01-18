import importlib.util
from pathlib import Path
import sys
from types import ModuleType
from typing import Any, Union

from .__version__ import __version__

__all__ = [
    '__version__',
    'import_module_from_file',
    'import_object_from_file',
    'import_object_from_module',
]


def import_module_from_file(
    path: Union[str, Path],
    mod_name: Union[str, None] = None,
    replace: bool = False,
) -> ModuleType:
    """
    Create module from ``path/to/file.py``

    >>> foobar = import_module_from_file('example/foobar.py')
    >>> foobar
    <module 'foobar' from '.../example/foobar.py'>

    :param path:
        path to import as module

    :param mod_name:
        name to assign to module created, defaults to ``path`` stem

    :param replace:
        if module ``mod_name`` is already imported and ``replace`` is ``True``,
        overwrite it, otherwise raise ``RuntimeError``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``mod_name`` can't be a module identifier
    :raises FileNotFoundError: when ``path`` does not exist
    :raises IsADirectoryError: when ``path`` is a directory
    :raises RuntimeError: when ``mod_name`` is already imported and ``replace``
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

    # prepare mod_name
    if mod_name is None:
        mod_name = path.stem

    # validate mod_name
    if not mod_name.isidentifier():
        raise ValueError(f'"{mod_name}" is not a valid identifier.')
    elif mod_name in sys.modules and not replace:
        raise ValueError(f'Module "{mod_name}" already imported.')

    # import
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Module "{mod_name}" cannot be imported.')
    mod_obj = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod_obj
    spec.loader.exec_module(mod_obj)
    return mod_obj


def import_object_from_file(
    path_spec: str,
    mod_name: Union[str, None] = None,
    replace: bool = False,
) -> Any:
    """
    Load object from ``path/to/file.py:[parent.[...].]object``

    >>> baz = import_object_from_file('example/foobar.py:baz')
    >>> baz
    <function baz at 0x...>

    :param path_spec:
        import string in format ``path/to/file.py:[parent.[...].]object``

    :param mod_name:
        name to assign to module created, defaults to ``path`` stem

    :param replace:
        if module ``mod_name`` is already imported and ``replace`` is ``True``,
        overwrite it, otherwise raise ``RuntimeError``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``path_spec`` is incorrect
    :raises ValueError: when ``mod_name`` can't be a module identifier
    :raises ValueError: when ``object`` is not a valid identifier
    :raises FileNotFoundError: when ``path/to/file`` does not exist
    :raises IsADirectoryError: when ``path/to/file`` is a directory
    :raises ImportError: when ``object`` is not defined in file
    :raises RuntimeError: when ``mod_name`` is already imported and ``replace``
        is ``False``

    :return: Imported object.

    .. versionadded:: 0.1.1
    """
    # todo: validate types

    # parse path_spec
    path, _, obj_name = path_spec.partition(':')
    if not path or not obj_name:
        raise ValueError(
            f'Import string "{path_spec}" '
            'must be in format "path/to/file.py:object[.attr...]".'
        )

    # validate object
    validate_identifier(obj_name)

    # import
    mod_obj = import_module_from_file(path, mod_name=mod_name, replace=replace)
    return get_nested_object(mod_obj, obj_name)


def import_object_from_module(mod_spec: str, replace: bool = False) -> Any:
    """
    Load object from ``[pkg.[...].]module:[parent.[...].]object``

    >>> baz = import_object_from_module('example.foobar:baz')
    >>> baz
    <function baz at 0x...>

    :param mod_spec:
        import string in format ``[pkg.[...].]module:[parent.[...].]object``

    :param replace:
        if ``module`` is already imported and ``replace`` is ``True``,
        overwrite it, otherwise raise ``RuntimeError``

    :raises TypeError: when passed arguments of wrong type
    :raises ValueError: when ``mod_spec`` is incorrect
    :raises ValueError: when ``object`` is not a valid identifier
    :raises ImportError: when ``module`` cannot be imported
    :raises ImportError: when ``object`` is not defined in ``module``
    :raises RuntimeError: when ``module`` is already imported and ``replace``
        is ``False``

    :return: Imported object.

    .. versionadded:: 0.1.1
    """
    # todo: validate types

    # parse mod_spec
    mod_name, _, obj_name = mod_spec.partition(':')
    if not mod_name or not obj_name:
        raise ValueError(
            f'Import string "{mod_spec}" must be in format '
            '"[...package.]module:object[.attr...]".'
        )

    # validate module
    validate_identifier(mod_name)
    if mod_name in sys.modules and not replace:
        raise ValueError(f'Module "{mod_name}" already imported.')

    # validate object
    validate_identifier(obj_name)

    # import
    mod_obj = importlib.import_module(mod_name)
    return get_nested_object(mod_obj, obj_name)


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
