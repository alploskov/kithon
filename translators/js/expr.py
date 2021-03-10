from transPYler import handler, target_op


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
    return "\""+val+"\""

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
def arg(arg, type=""):
    return arg

@handler("list")
def _list(ls, _type):
    return f"[{', '.join(ls)}]"

@handler("index")
def index(arr, val):
    if val[0] == '-':
        return f"{arr}[{arr}.length{val}]"
    return f"{arr}[{val}]"

@handler("init")
def init(name, args):
    args = ", ".join(args)
    return f"new {name}(args)"

@handler("slice")
def slice(arr, lower, upper, step):
    if lower == 'None':
        lower = 0
    if upper == 'None':
        upper = " "
    if upper[0] == '-':
        upper = f"{arr}.length{upper}" 
    if not(step):
        step = 1
    return f"{arr}.slice({lower}, {upper})"

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
          "is": "==="
}
