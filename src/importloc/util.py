from base64 import b32encode
from enum import Enum
import inspect
from typing import Any, Callable, Optional, TypeVar, Union
from uuid import uuid4


#: Arbitrary type.
T = TypeVar('T', bound=object)


class OrderBy(str, Enum):
    """
    Objects sorting method.
    """

    #: Order by object name.
    NAME = 'name'

    #: Order by definition order in the source file, first by source filename path,
    #: then by first line number. This sorting method uses `inspect.getsourcefile`
    #: and `inspect.getsourcelines`, and inherits their requirements on objects
    #: and exceptions raised.
    SOURCE = 'source'


def get_instances(
    obj: object,
    cls: type[T],
    order: Union[OrderBy, str, Callable[[T], Any]] = 'name',
) -> list[T]:
    """
    Get object members that are instances of specified type. Uses `inspect.getmembers`
    and `isinstance`.

    Args:
        obj (``object``):
            object to get members from.
        cls (``type``):
            type of members to be returned.
        order (`OrderBy` | ``str`` | ``Callable[[T], Any]``):
            sorting method or sort key function; defaults to ``'name'``.

    Raises:
        `TypeError`: or other `Exception` raised by `inspect.getfile` and
            `inspect.getsourcelines` when sorting ``order='source'``.

    Returns:
        ``list[object]``:

    Example:
        >>> import app.plugins
        >>> plugins = get_instances(app.plugins, Plugin)
    """
    ret = [mem for name, mem in inspect.getmembers(obj) if isinstance(mem, cls)]
    order_key = get_sort_key_func(order)
    if order_key:
        ret.sort(key=order_key)
    return ret


def get_subclasses(
    obj: object,
    cls: type[T],
    order: Union[OrderBy, str, Callable[[T], Any]] = 'name',
) -> list[type[T]]:
    """
    Get object members that are subclasses of specified class (excluding the class
    itself). Uses `inspect.getmembers` and `issubclass`.

    Args:
        obj (`object`):
            object to get members from.
        cls (`type`):
            base class for returned subclasses.
        order (`OrderBy` | ``str`` | ``Callable[[T], Any]``):
            sorting method or sort key function; defaults to ``'name'``.

    Raises:
        `TypeError`: or other `Exception` raised by `inspect.getfile` and
            `inspect.getsourcelines` when sorting ``order='source'``.

    Returns:
        ``list[object]``:

    Example:
        >>> from unittest import TestCase
        >>> from tests import test_usage
        >>> cases = get_subclasses(test_usage, TestCase, order='source')
    """
    ret = [
        m
        for name, m in inspect.getmembers(obj)
        if isinstance(m, type) and issubclass(m, cls) and m is not cls
    ]
    order_key = get_sort_key_func(order)
    if order_key:
        ret.sort(key=order_key)
    return ret


def getattr_nested(
    obj: object,
    name: str,
    default: Union[type[Exception], Any] = AttributeError,
) -> object:
    """
    Get nested attribute value. If attribute chain does not exist, raise exception
    or return default value.

    Args:
        obj (`object`):
            object to get attribute value from.

        name (`str`):
            dot-separated nested attribute name.

        default (`Exception` | `Any`):
            raise exception if ``default`` is an `Exception` type (`AttributeError` by
            default); otherwise return ``default`` value.

    Raises:
        `AttributeError`:
            when nested attribute chain does not exist and ``default`` was not adjusted.
        `Exception`:
            when custom `Exception` passed as ``default``.

    Returns:
        nested attribute value or ``default`` value, if specified and not an
        `Exception` subclass.

    Example:
        >>> from app import config
        >>> options = getattr_nested(config, f'{config.primary}.options')
        >>> missing = getattr_nested(config, 'does.not.exist', None)
    """
    current = obj
    for part in name.split('.'):
        try:
            current = getattr(current, part)
        except AttributeError as exc:
            if isinstance(default, type) and issubclass(default, Exception):
                raise default(f'object has no attribute {name!r}') from exc
            else:
                return default
    return current


def random_name(*args: Any, **kwargs: Any) -> str:
    """
    Generate random module name based on UUID4.

    All arguments passed to this function will be ignored.

    Example:
        >>> random_name()
        'ufoh3xjrrozfcvfheyktg62pzia'
    """
    rand = b32encode(uuid4().bytes).decode('ascii').replace('=', '').lower()
    return f'u{rand}'


# undocumented helpers


def get_sort_key_func(
    order: Union[OrderBy, str, Callable[[T], Any]],
) -> Optional[Callable[[Any], Any]]:
    if order == 'name':
        return None
    elif order == 'source':
        return lambda o: (inspect.getsourcefile(o), inspect.getsourcelines(o)[1])
    elif callable(order):
        return order
    else:
        raise TypeError('Unexpected order type {}'.format(type(order)))
