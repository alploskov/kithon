from os import path, walk
import typer


def conf(transpiler, _js, _go, target, macro, templates):
    for lang, value in {'js': _js, 'go': _go}.items():
        if value:
            transpiler.get_lang(lang)
    if target and path.isdir(target):
        for dirr, _, files in walk(target):
            for f in files:
                if f.endswith('.tp'):
                    transpiler.load_templs(
                        open(f'{dirr}/{f}', 'r').read()
                    )
    elif target in ['js', 'go', 'python']:
        transpiler.get_lang(target)
    for _macro in macro:
        transpiler.load_templs(_macro)
    for tmp in templates:
        transpiler.load_templs(open(tmp).read())

_js = typer.Option(False, '--js')
_go = typer.Option(False, '--go')
templates = typer.Option(
    [],
    '-t',
    '--templ',
    help='Names of template file'
)

target = typer.Option(
    '',
    '--target',
    show_default=None,
    help='Directory with template files'
)

macro = typer.Option(
    [],
    '-m',
    '--macro',
    help='Macro in yaml format'
)
