import re
from unittest import TestCase

from caseutil import to_kebab
from docsub import click
from doctestcase import get_title, to_markdown
from importloc import Location, get_subclasses, random_name


@click.group()
def x() -> None:
    pass


@x.command()
@click.argument('testpath', type=click.Path(exists=True, dir_okay=False))
@click.argument('nameregex')
def cases(testpath: click.Path, nameregex: str) -> None:
    """
    Print usage section based on test cases docstrings
    """
    cases = get_subclasses(Location(str(testpath)).load(random_name), TestCase)
    cases.sort(key=lambda c: c.__firstlineno__)  # type: ignore[attr-defined]
    for case in cases:
        if re.fullmatch(nameregex, case.__name__):
            click.echo(to_markdown(case))


@x.command()
@click.argument('testpath', type=click.Path(exists=True, dir_okay=False))
@click.argument('nameregex')
def toc(testpath: click.Path, nameregex: str) -> None:
    """
    Print ToC based on test cases docstrings
    """
    cases = get_subclasses(Location(str(testpath)).load(random_name), TestCase)
    cases.sort(key=lambda c: c.__firstlineno__)  # type: ignore[attr-defined]
    for case in cases:
        if re.fullmatch(nameregex, case.__name__):
            title = get_title(case)
            click.echo(f'* [{title}](#{to_kebab(title)})')
