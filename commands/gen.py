import sys
import time
from typing import Optional
import typer
import yaml
from kithon import Transpiler
from . import configurator
from .watch import watch
try:
    import packed
except:
    packed = None

def builder(conf):
    ...

def _gen(
    file_name: str = typer.Argument(
        None,
        metavar='FILE',
        help='Name of file for transpilation'
    ),
    templates: list[str] = configurator.templates,
    macro: list[str] = configurator.macro,
    target: Optional[str] = configurator.to,
    out: Optional[str] = typer.Option(
        '',
        '-o',
        '--out',
        help='Output file',
        show_default='stdout'
    ),
    input_lang: Optional[str] = typer.Option(
        '',
        '-l',
        '--lang',
        help='Marking the entrance language (py, hy, coco)',
        show_default='Determined by the filename'
    ),
    _watch: Optional[bool] = typer.Option(
        False,
        '-w',
        '--watch',
        help='Watch file changes'
    )
):
    """
    Transpile python code into chose language
    """
    transpiler = Transpiler()
    configurator.conf(
        transpiler, target, macro, templates
    )
    ext = file_name.split('.')[-1]
    code = open(file_name, 'r').read()
    if ext.endswith('x'):
        ext = ext[:-1]
        if packed is not None:
            code = packed.translate(code)
    lang = {
        'py': 'py',
        'python': 'py',
        'hy': 'hy',
        'hylang': 'hy',
        'coco': 'coco',
        'coconut': 'coco'
    }.get(input_lang or ext)
    def g(msg=True):
        if msg:
            print(f'{time.asctime()} -- generate --')
        print(
            transpiler.generate(
                code, lang=lang
            ), file=open(out, 'w') if out else sys.stdout
        )
    g(False)
    if _watch:
        watch(g, file_name)
