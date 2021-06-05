import _ast
from .utils import transpyler_type
from .ast_decompiler import decompile
#from core import parser


def what_macro(name):
    if type(name) == tuple:
        name = (transpyler_type(name[0]), transpyler_type(name[1]), name[2])
        ol_data = [(name[0], name[1], name[2]),
                   (name[0], name[1], 'any'),
                   (name[0], 'any', name[2]),
                   ('any', 'any', name[2]),
                   ('any', 'any', 'any'),
                   ]
        for i in ol_data:
            if ol := macros.get(i):
                return ol

    elif type(name)==str:
        if name in macros:
            name = macros.get(name)
            return name
    else:
        for i in macros:
            if callable(i):
                if i(name):
                    return macros.get(i)

def macro(name, args):
    return eval(f"name{args}")

macros = {}
