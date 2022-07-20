import typer
from .gen import _gen
from .new import _new
from .repl import _repl
from .run import _run


kithon = typer.Typer()

kithon.command('new')(_new)
kithon.command('gen')(_gen)
kithon.command('repl')(_repl)
kithon.command('run')(_run)
