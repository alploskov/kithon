import os
import sys
from typing import Optional
import typer
from jinja2 import Template
from kithon import Transpiler
from . import configurator
try:
    import packed
except:
    packed = None


def _run(
    file_name: str = typer.Argument(
        None,
        metavar='FILE',
        help='Name of file for transpilation'
    ),
    templates: list[str] = configurator.templates,
    macro: list[str] = configurator.macro,
    target: Optional[str] = configurator.to,
    input_lang: Optional[str] = typer.Option(
        '',
        '-l',
        '--lang',
        help='Marking the entrance language (py, hy, coco)',
        show_default='Determined by the filename'
    ),
    command: Optional[str] = typer.Option(
        '',
        '--command'
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
        return
    else:
        ext = file_name.split('.')[-1]
        code = open(file_name, 'r').read()
        if ext.endswith('x') and packed is not None:
            code = packed.translate(code)
        lang = input_lang or ext.removesuffix('x')
        command = command or transpiler.templates['meta']['run']
        if isinstance(command, dict):
            command = command.get(sys.platform)
        os.system(
            Template(command).render(
                code=transpiler.generate(
                    code, lang=lang
                )
            )
        )
