from os import path, mkdir, listdir, symlink, getcwd
from shutil import copytree
from typing import Optional
import typer
from kithon import __path__


def _new(
    name: str = typer.Argument(
        '',
        help='Name of new language'
    ),
    base: Optional[str] = typer.Option(
        '',
        '--base',
        help='Base for new language(c, lisp, ...)'
    ),
    _global: Optional[bool] = typer.Option(
        False,
        '-g',
        '--global',
        help='Make transpiler global'
    )
):
    translators_dirr = path.join(path.split(__path__[0])[0], 'translators')
    if path.isdir(name):
        typer.echo('Translator already exists')
        raise typer.Exit()
    _base = {
        'c': 'c-like',
        'lisp': 'lisp-like'
    }.get(base.lower(), base.lower())
    if _base in listdir(translators_dirr):
        copytree(f'{translators_dirr}/{_base}', name)
    else:
        mkdir(name)
        open(path.join(name, 'core.tp'), 'w').close()
        open(path.join(name, 'macros.tp'), 'w').close()
        mkdir(path.join(name, 'libs'))
        mkdir(path.join(name, 'objects'))
    if _global:
        symlink(
            path.join(getcwd(), name),
            path.join(translators_dirr, name)
        )
