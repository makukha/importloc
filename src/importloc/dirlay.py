from dataclasses import dataclass
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional, Tuple, Union


@dataclass
class File:
    path: str
    text: str


@dataclass
class DirectoryLayout:
    files: Tuple[File, ...]
    chdir: Union[str, Path] = Path('.')

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
