import re
from typing import Union
from unittest import TestCase

from caseutil import to_kebab
from docsub import click
from importloc import Location, get_subclasses, random_name


@click.group()
def x() -> None:
    pass


@x.command()
@click.argument('subcommand')
@click.argument('testpath', type=click.Path(exists=True, dir_okay=False))
@click.argument('nameregex')
def usage(subcommand: str, testpath: click.Path, nameregex: str) -> None:
    """
    Print usage section based on test cases docstrings
    """
    formatter = {'section': format_section, 'toc': format_toc}[subcommand]
    cases = get_subclasses(Location(str(testpath)).load(random_name), TestCase)
    cases.sort(key=lambda c: c.__firstlineno__)  # type: ignore[attr-defined]
    for case in cases:
        if re.fullmatch(nameregex, case.__name__):
            print(formatter(case.__doc__))


RX_DOCSTRING = re.compile(
    r'^(?P<title>.+?)\n\n(?P<body>.*)',
    re.DOTALL,
)
RX_DOCTEST = re.compile(
    r'(?<=\n)(?P<code>>>>.+?)(?=\n\n|\n$)',
    re.DOTALL,
)


def format_section(text: Union[str, None]) -> str:
    if text is None or (m := RX_DOCSTRING.fullmatch(text)) is None:
        raise ValueError('Invalid docstring format')

    body = m.group('body')
    body = re.sub(r'\n>>>', '\n_Example_\n>>>', body, count=1, flags=re.DOTALL)
    body = RX_DOCTEST.sub(r'```pycon\n\g<code>\n```', body)
    lines = (
        f'### {m.group("title")}\n\n',
        body,
    )
    return ''.join(lines)


def format_toc(text: Union[str, None]) -> str:
    if text is None or (m := RX_DOCSTRING.fullmatch(text)) is None:
        raise ValueError('Invalid docstring format')
    title = m.group('title')
    return f'* [{title}](#{to_kebab(title)})'
