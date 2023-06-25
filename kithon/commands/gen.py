import ast
import os
import sys
from pathlib import Path
from _ast import Import, ImportFrom
from typing import Optional
import typer
from jinja2 import Template
from . import configurator
from .. import Transpiler
from .watch import watch
try:
    import packed
    pyx = lambda code: packed.translate(code)
except:
    pyx = lambda code: code


def compilation_order(__dir__):
    modules = {}
    for _file in os.listdir(__dir__):
        if _file.startswith('.'):
            continue
        ext = _file.split('.')[-1]
        if ext in ['py', 'coco', 'hy', 'pyx', 'cocox']:
            name = os.path.split(_file)[1].removesuffix('.' + ext)
            code = open(os.path.join(__dir__, _file), 'r').read()
            if ext.endswith('x'):
                code = pyx(code)
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
    ),
    _build: Optional[bool] = typer.Option(
        False,
        '--build'
    ),
    build_command: Optional[str] = typer.Option(
        '',
        '--build-command'
    )
):
    """
    Transpile python code into chose language
    """
    transpiler = Transpiler()
    configurator.conf(
        transpiler, target or out.split('.')[-1], macro, templates
    )
    path = Path(file_name)
    if path.is_dir():
        _ext = transpiler.templates['meta'].get('ext')
        out_dir = out or file_name
        if not Path(out_dir).is_dir():
            os.mkdir(out)
        def g():
            order, modules = compilation_order(file_name)
            for m in order:
                try:
                    with open(os.path.join(out_dir, f'{m}.{_ext}'), 'w') as f:
                        f.write(transpiler.generate(
                            modules[m]['code'],
                            mode=m if m != order[-1] else 'main'
                        ))
                    print(f'\033[32mSucsess compile {m}\033[38m')
                except:
                    print(f'\033[31mFaile compile {m}\033[38m')
            print('----------')
    else:
        ext = path.suffix[1:]
        def g():
            code = open(file_name, 'r').read()
            if ext.endswith('x'):
                code = pyx(code)
            lang = input_lang or ext.removesuffix('x')
            _code = transpiler.generate(
                    code, lang=lang
            )
            print(
                _code,
                file=open(out, 'w') if out else sys.stdout
            )
            if _build:
                command = transpiler.templates['meta'].get('build')
            else:
                command = build_command
            if command:
                os.system(
                    Template(command).render(
                        out=out,
                        code=_code
                    )
                )
    g()
    if _watch:
        watch(g, file_name)
