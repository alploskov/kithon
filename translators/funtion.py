import _ast


def bin_op(left, right, op):
    return left+op+right

def name(name):
    return name

def const(val):
    return val

def expr(value):
    return value+";"

def assign(var, value):
    return f"{var} = {value};"

def call(name, args):
    return f"{name}({args})"

def attr(obj, attr_name):
    return f"{obj}.{attr_name}"

def arg(arg):
    return arg

def args(args):
    return ", ".join(args)

a_func={"print":"alert",
        "input":"prompt"
}

a_attr={"len":"length",
        "append":"push"
}

signs = {"+": "+",
         "-": "-",
         "*": "*",
         "/": "/"
}

expr_handlers = {_ast.BinOp: bin_op,
                 _ast.Name: name,
                 _ast.Constant: const,
                 _ast.Attribute: attr,
                 _ast.Call: call,
                 "args": args,
                 _ast.arg: arg
}

blocks_handlers = {_ast.Assign: assign,
                   _ast.Expr: expr
}
