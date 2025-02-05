from typing import Any


class InvalidLocation(ValueError):
    """
    Incorrect format of location specification string.
    """

class ModuleNameConflict(ImportError):
    """
    Module with this name is already imported.
    """
    def __init__(self, module_name: str, *args: Any, **kwargs: Any) -> None:
        msg = f'Module "{module_name}" is already imported'
        super().__init__(msg, *args, **kwargs)
