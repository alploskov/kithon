from . import core
from . import expressions
from .expressions import target_op
from . import blocks
from . import macros
from . import utils


def handler(key):
    def _handler(func):
        def add_handler():
            core.handlers.update({key: func})
        add_handler()
        return add_handler
    return _handler

def macro(name):
    if type(name) == dict:
        macros.macros.update(name)
        return
    def _macro(func):
        def add_macro():
            macros.macros.update({name: func})
        add_macro()
        return add_macro
    return _macro
