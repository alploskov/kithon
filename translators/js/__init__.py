from . import blocks, expr
from .macros import macros


attrs = {"list": {"index": {"val": "indexOf"},
                  "append": {"val": "push"}
                  },
         "math": {"__name__": "Math",
                  "pi": {'val': 'PI',
                         'type': 'float'
                         }
                  },
         "json": {"__name__": "JSON",
                  "dumps": {'val': 'stringify'},
                  "loads": {'val': 'parse'}
                  }
}

signs = {"+": "+",
         "-": "-",
         "*": "*",
         "/": "/",
         "**": "**",
         "==": "===",
         "!=": "!==",
         ">": ">",
         "<": "<",
         ">=": ">=",
         "<=": "<=",
         "or": "||",
         "and": "&&",
         "|": "|",
         "&": "&",
         "%": "%",
         "not": "!"
}

handlers = {"bbc_op": expr.op,
            "name": expr.name,
            "un_op": expr.un_op,
            "const": expr.const,
            "string": expr.c_str,
            "attr": expr.attr,
            "call": expr.call,
            "arg": expr.arg,
            "index": expr.index,
            "slice": expr.slice,
            "list": expr._list,
            "assign": blocks.assign,
            "new_var": blocks.new_var,
            "expr": blocks.expr,
            "aug_assign": blocks.aug_assign,
            "if": blocks._if,
            "statement_block": blocks.statement_block,
            "else": blocks._else,
            "else_if": blocks.else_if,
            "def": blocks.def_f,
            "return": blocks.ret,
            "for": blocks._for,
            "c_like_for": blocks.c_like_for,
            "while": blocks._while
}
