from os import path, walk, listdir
from kithon import __path__
import typer


def conf(transpiler, target, macro, templates):
    if target and path.isdir(target):
        for dirr, _, files in walk(target):
            for f in files:
                if f.endswith('.tp'):
                    transpiler.load_templs(
                        open(f'{dirr}/{f}', 'r').read()
                    )
    elif target in listdir(path.join(path.split(__path__[0])[0], 'translators')):
        transpiler.get_lang(target)
    for _macro in macro:
        transpiler.load_templs(_macro)
    for tmp in templates:
        transpiler.load_templs(open(tmp).read())

templates = typer.Option(
    [],
    '-t',
    '--templ',
    help='Names of template file'
)

to = typer.Option(
    '',
    '--to',
    show_default=None,
    help='Directory with template files or name of target language'
)

macro = typer.Option(
    [],
    '-m',
    '--macro',
    help='Macro in yaml format'
)
