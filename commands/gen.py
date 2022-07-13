import ast
import os
import sys
import time
from _ast import Import, ImportFrom
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


def compilation_order(__dir__):
    modules = {}
    for _file in os.listdir(__dir__):
        if _file.startswith('.'):
            continue
        ext = _file.split('.')[-1]
        if ext in ['py', 'coco', 'hy', 'pyx', 'cocox']:
            name = os.path.split(_file)[1].removesuffix('.' + ext)
            code = open(os.path.join(__dir__, _file), 'r').read()
            if ext.endswith('x') and packed != None:
                code = packed.translate(code)
            modules |= {name: {
                'count_dependent': 0,
                'code': code
            }}
    for mod in modules:
        tree = ast.parse(modules[mod]['code']).body
        for node in tree:
            if isinstance(node, Import):
                name = node.names[0].name
            elif isinstance(node, ImportFrom):
                name = node.module
            else:
                continue
            if name in modules:
                modules[name]['count_dependent'] += 1
    return sorted(
        modules,
        key=lambda k: modules[k]['count_dependent'],
        reverse=True
    ), modules

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
    if os.path.isdir(file_name):
        _ext = transpiler.templates['meta'].get('ext')
        out_dir = out or file_name
        if not os.path.isdir(out_dir):
            os.mkdir(out)
        def g():
            order, modules = compilation_order(file_name)
            for m in order:
                with open(os.path.join(out_dir, f'{m}.{_ext}'), 'w') as f:
                    f.write(transpiler.generate(
                        modules[m]['code'],
                        mode=m if m != order[-1] else 'main'
                    ))
    else:
        ext = file_name.split('.')[-1]
        def g():
            code = open(file_name, 'r').read()
            if ext.endswith('x') and packed is not None:
                code = packed.translate(code)
            lang = input_lang or ext.removesuffix('x')
            print(
                transpiler.generate(
                    code, lang=lang
                ), file=open(out, 'w') if out else sys.stdout
            )
    g()
    if _watch:
        watch(g, file_name)
