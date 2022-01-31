import os
from os import path
import sys
from typing import List, Optional
import typer
from .commands import get_lang
from .core import Transpiler
from . import supported_languages


tpy = typer.Typer()
tpy_gen = typer.Typer()
tpy_new = typer.Typer()
tpy_lang = typer.Typer()

@tpy_new.command()
@tpy.command('new')
def new(
    name: str = typer.Argument(
        '',
        metavar='Name',
        help='Name of new language'
    ),
):
    """
    Create template for new language
    """

@tpy_gen.command()
@tpy.command('gen')
def generate(
    file_name: str = typer.Argument(
        None,
        metavar='FILE',
        help='Name of file for transpilation'
    ),
    templates: List[typer.FileText] = typer.Option(
        [],
        '-t',
        '--templ',
        help='Names of template file'
    ),
    out: typer.FileTextWrite = typer.Option(
        sys.stdout,
        '-o',
        '--out',
        help='Output file',
        show_default='stdout'
    ),
    _js: Optional[bool] = typer.Option(False, '--js'),
    _go: Optional[bool] = typer.Option(False, '--go'),
    input_lang: Optional[str] = typer.Option(
        '',
        '-l',
        '--lang',
        help='Marking the entrance language (py, hy, coco)',
        show_default='Вetermined by the filename'
    ),
    target: Optional[str] = typer.Option(
        '',
        '--target',
        show_default=None
    )
):
    """
    Transpile python code into chose language
    """
    templates = '\n'.join(list(templates))
    for lang, value in {'js': _js, 'go': _go}.items():
        if value:
            target = lang
    if target and path.isdir(target):
        for dirr, _, files in os.walk(target):
            templates += '\n'.join([
                open(f'{dirr}/{f}', 'r').read()
                for f in files if f.endswith('.tp')
            ])
    elif target in supported_languages:
        templates += get_lang(target)
    ext = file_name.split('.')[-1]
    if ext.endswith('x'):
        ext = ext[:-1]
        source = open(file_name, 'r', encoding='pyxl').read()
    else:
        source = open(file_name, 'r').read()
    print(
        Transpiler(templates).generate(
            source,
            lang={
                'py': 'py',
                'python': 'py',
                'hy': 'hy',
                'hylang': 'hy',
                'coco': 'coco',
                'coconut': 'coco'
            }.get(input_lang or ext)
        ),
        file=out)
