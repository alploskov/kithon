import _ast


def bin_op(left, right, op):
    return left+op+right
    pass

def name(name):
    return name

def const(val):
    return val

def expr(value):
    return value+";"

def assign(var, value):
    return f"{var} = {value};"

signs = {"+": "+",
         "-": "-",
         "*": "*",
         "/": "/"
}

expr_handlers = {_ast.BinOp: bin_op,
                 _ast.Name: name,
                 _ast.Constant: const
}
blocks_handlers = {_ast.Assign: assign,
                   _ast.Expr: expr
}
