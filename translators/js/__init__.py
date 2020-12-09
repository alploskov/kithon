import _ast
from . import blocks
from . import expr


a_func={"print":"alert",
        "input":"prompt"
}

a_attr={"len":"length",
        "append":"push"
}

signs = {"+": "+",
         "-": "-",
         "*": "*",
         "/": "/",
         "==": "==",
         "!=": "!=",
         ">": ">",
         "<": "<",
         ">=": ">=",
         "<=": "<=",
         "or": "||",
         "and": "&&",
         "|": "|",
         "&": "&"
}

expr_handlers = {_ast.BinOp: expr.bin_op,
                 _ast.Name: expr.name,
                 _ast.Constant: expr.const,
                 _ast.Attribute: expr.attr,
                 _ast.Call: expr.call,
                 "args": expr.args,
                 _ast.arg: expr.arg,
                 _ast.Compare: expr.compare
}

blocks_handlers = {_ast.Assign: blocks.assign,
                   _ast.Expr: blocks.expr,
                   _ast.If: blocks._if,
                   "statement_block": blocks.statement_block,
                   "else": blocks._else,
                   "else_if": blocks.else_if
}
