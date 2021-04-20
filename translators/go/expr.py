from transPYler import handler, target_op
from utils import type_to_type


@handler("bin_op")
def bin_op(left, right, op):
    return f"({left} {op} {right})"

@handler("un_op")
def un_op(op, el):
    return f"{op}({el})"

@handler("name")
def name(name):
    return name

@handler("const")
def const(val):
    return val

@handler("string")
def c_str(val):
    return '"'+val+'"'

@handler("compare")
def compare(els, ops):
    first_el = els[0]
    other_els = els[1:]
    op_and_els = "".join([ops[i]+el for i, el in enumerate(other_els)])
    return first_el+op_and_els

@handler("bool_op")
def bool_op(els, op):
    return els[0]+" "+"".join([op+" "+i for i in els[1:]])

@handler("call")
def call(name, args):
    args = ", ".join(args)
    return f"{name}({args})"

@handler("attr")
def attr(obj, attr_name):
    return f"{obj}.{attr_name}"

@handler("arg")
def arg(arg, _type=""):
    return f'{arg} {type_to_type(_type)}'

@handler("list")
def _list(ls, _type):
    _type = type_to_type(_type)
    return f"[]{_type}{{{', '.join(ls)}}}"

@handler("index")
def index(arr, val):
    return f"""{arr}[Index({val}, len({arr}))]"""

@handler("init")
def init(name, args):
    args = ", ".join(args)
    return f"new {name}(args)"

@handler("slice")
def slice(arr, lower, upper, step):
    if lower == 'None':
        lower = 0
    if upper == 'None':
        upper = f"len({arr})" 
    if not(step):
        step = 1
    return f"{arr}[{lower}:Index({upper}, len({arr}))]"

target_op |= {"+": "+",
              "-": "-",
              "*": "*",
              "/": "/",
              "**": "**",
              "==": "==",
              "!=": "!=",
              ">": ">",
              "<": "<",
              ">=": ">=",
              "<=": "<=",
              "or": "||",
              "and": "&&",
              "|": "|",
              "&": "&",
              "%": "%",
              "not": "!",
              "is": "==",
              '//': '/'
}
