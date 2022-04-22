import pprint
from typing import Optional
import pexpect
import typer
from ptpython.python_input import PythonInput
from kithon import Transpiler
from . import configurator


def _repl(
    templates: list[typer.FileText] = configurator.templates,
    macro: list[str] = configurator.macro,
    _js: Optional[bool] = configurator._js,
    _go: Optional[bool] = configurator._go,
    target: Optional[str] = configurator.target,
    repl_name: Optional[str] = typer.Option(
        '',
        '--repl',
        help='Name of repl'
    ),
    separator: Optional[str] = typer.Option(
        '',
        '--sep',
        help='Input prompt including spaces'
    )
):
    prompt = PythonInput()
    transpiler = Transpiler()
    configurator.conf(
        transpiler, _js, _go,
        target, macro, templates
    )
    if _js and not repl_name:
        repl_name = 'node'
        separator = '> '
    repl = pexpect.spawn(repl_name)
    repl.expect(separator)
    code = ''
    while 1:
        src = prompt.app.run()
        if src.strip() == 'vars':
            pprint.pprint(transpiler.variables)
            continue
        if src.strip() == 'code':
            print(code)
            continue
        code = transpiler.generate(src, mode='block')
        repl.sendline(code)
        repl.expect(separator)
        print(
            '\n'.join(repl.before.decode('utf-8').split('\n')[
                len(code.split('\n')):-1
            ])
        )
