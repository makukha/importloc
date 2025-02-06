from base64 import b32encode
import inspect
from typing import Any, TypeVar, Union
from uuid import uuid4


#: Arbitrary type.
T = TypeVar('T', bound=type)


def get_instances(obj: object, cls: type[T]) -> list[T]:
    """
    Get object member instances of specified type.

    Uses `inspect.getmembers` and `isinstance`.

    >>> import app.plugins
    >>> plugins = get_instances(app.plugins, Plugin)

    :param obj:
        object to get members from.

    :param cls:
        type of members to be returned.

    :return: list of object members.
    """
    return [mem for name, mem in inspect.getmembers(obj) if isinstance(mem, cls)]


def get_subclasses(obj: object, cls: type[T]) -> list[type[T]]:
    """
    Get object member subclasses of specified class, excluding the class itself.

    Uses `inspect.getmembers` and `issubclass`.

    >>> import app.enums
    >>> enums = get_subclasses(app.enums, Enum)

    :param obj:
        object to get members from.

    :param cls:
        type of members to be returned.

    :return: list of object member classes.
    """
    return [
        m
        for name, m in inspect.getmembers(obj)
        if isinstance(m, type) and issubclass(m, cls) and m is not cls
    ]


def getattr_nested(
    obj: object,
    name: str,
    default: Union[type[Exception], Any] = AttributeError,
) -> object:
    """
    Get nested attribute value.

    If attribute chain does not exist, raise exception or return default value.

    >>> from app import config
    >>> options = getattr_nested(config, f'{config.primary}.options')
    >>> missing = getattr_nested(config, 'does.not.exist', None)

    :param obj:
        object to get attribute from.

    :param name:
        dot-separated nested attribute name.

    :param default:
        raise exception if ``default`` is an `Exception` type (`AttributeError` by
        default); otherwise return ``default`` value.

    :raises AttributeError:
        when nested attribute chain does not exist and ``default`` was not adjusted.
    :raises Exception:
        when custom `Exception` passed as ``default``.

    :return:
        nested attribute value or ``default`` value, if specified and not an
        `Exception` subclass.
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

    >>> random_name()
    'ufoh3xjrrozfcvfheyktg62pzia'
    """
    rand = b32encode(uuid4().bytes).decode('ascii').replace('=', '').lower()
    return f'u{rand}'
