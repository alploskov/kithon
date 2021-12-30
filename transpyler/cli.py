import codecs
import os
import sys
from typing import List, Optional
import typer
from .core import Transpiler


tpy = typer.Typer()
tpy_gen = typer.Typer()
tpy_new = typer.Typer()

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
    input_lang: Optional[str] = typer.Option(
        'Вetermined by the filename',
        '-l',
        '--lang',
        help='Marking the entrance language (py, hy, coco)'
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
    templates = list(templates)
    if target:
        if os.path.isdir(target):
            for dirr, _, files in os.walk(target):
                templates += [\
                    open(f'{dirr}/{f}', 'r') \
                    for f in files if f.endswith('.tp')\
                ]
    ext = file_name.split('.')[-1]
    if ext.endswith('x'):
        ext = ext[:-1]
        source = open(file_name, 'r', encoding='pyxl').read()
    else:
        source = open(file_name, 'r').read()
    input_lang = {
        'py': 'py',
        'python': 'py',
        'hy': 'hy',
        'hylang': 'hy',
        'coco': 'coco',
        'coconut': 'coco'
    }.get(ext)
    transpiler = Transpiler('\n'.join(list(map(lambda t: t.read(), templates))))
    result = transpiler.generate(source, lang=input_lang)
    print(result, file=out)
