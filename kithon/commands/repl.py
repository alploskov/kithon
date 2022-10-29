import pprint
from typing import Optional
import typer
try:
    import pexpect
    from ptpython.python_input import PythonInput
    is_repl_install = True
except ImportError:
    is_repl_install = False
from kithon import Transpiler
from . import configurator


def _repl(
    templates: list[typer.FileText] = configurator.templates,
    macro: list[str] = configurator.macro,
    target: Optional[str] = configurator.to,
    repl_name: Optional[str] = typer.Option(
        '',
        '--repl',
        help='Name of repl'
    ),
    separator: Optional[str] = typer.Option(
        '',
        '--prompt',
        help='Input prompt including spaces'
    )
):
    if not is_repl_install:
        raise Exception(
            "requires pexpect, ptpython\n"
            "\trun 'python -m pip install kithon[repl]' to fix"
        )
    prompt = PythonInput()
    transpiler = Transpiler()
    configurator.conf(
        transpiler, target, macro, templates
    )
    repl = pexpect.spawn(
        repl_name
        or transpiler.templates['meta']['repl']['name']
    )
    sep = separator or transpiler.templates['meta']['repl']['prompt']
    repl.expect(sep)
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
        repl.expect(sep)
        print(
            '\n'.join(repl.before.decode('utf-8').split('\n')[
                len(code.split('\n')):-1
            ])
        )
