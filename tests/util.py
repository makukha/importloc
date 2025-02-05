from dataclasses import dataclass
import doctest
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, Union
import unittest

from importloc import Location


@dataclass
class File:
    path: str
    text: str


@dataclass
class DirectoryLayout:
    files: Tuple[File, ...]
    chdir: Union[str, Path] = '.'

    def __post_init__(self) -> None:
        self._tempdir: Optional[TemporaryDirectory[str]] = None
        self._oldcwd: Optional[str] = None

    def create(self) -> None:
        self._tempdir = TemporaryDirectory()
        for f in self.files:
            p = Path(self._tempdir.name) / f.path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f.text)

    def pushd(self) -> None:
        self._oldcwd = os.getcwd()
        os.chdir(self.cwd)

    @property
    def cwd(self) -> Path:
        if self._tempdir is None:
            raise RuntimeError('Directory layout must be created first')
        return Path(self._tempdir.name) / self.chdir

    def popd(self) -> None:
        if self._oldcwd is None:
            raise RuntimeError('Directory stack is already empty')
        os.chdir(self._oldcwd)
        self._oldcwd = None

    def destroy(self) -> None:
        if self._tempdir is None:
            raise RuntimeError('Directory layout already destroyed')
        self._tempdir.cleanup()
        self._tempdir = None


class TestCase(unittest.TestCase):
    layout: DirectoryLayout
    modnames: Tuple[str, ...]
    __test__ = False

    def __init_subclass__(cls, layout: DirectoryLayout) -> None:
        cls.layout = layout
        cls.__test__ = True

    def setUp(self) -> None:
        self.layout.create()
        self.layout.pushd()
        self.modnames = tuple(sys.modules.keys())
        sys.path.insert(0, str(self.layout.cwd))

    def tearDown(self) -> None:
        sys.path.pop(0)
        self.layout.popd()
        self.layout.destroy()
        for m in tuple(sys.modules):
            if m not in self.modnames:
                del sys.modules[m]
        self.modnames = ()

    def test_case(self) -> None:
        finder = doctest.DocTestFinder(recurse=False)
        runner = doctest.DocTestRunner(optionflags=doctest.ELLIPSIS | doctest.FAIL_FAST)
        globs = globals() | {'Location': Location}
        for test in finder.find(self.__doc__, self.__class__.__name__, globs=globs):
            ret = runner.run(test)
            self.assertFalse(ret.failed)
