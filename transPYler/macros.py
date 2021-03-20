import _ast
from .utils import transpyler_type
from .ast_decompiler import decompile


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
    def get_val(val):
        if type(val)==_ast.Constant:
            val = val.value
            if type(val) == str:
                val = '"'+val+'"'
            val = str(val)
            return val
        else:
            return decompile(val)
    args = str(tuple(map(get_val, args)))
    return eval(f"name{args}")

macros = {}
