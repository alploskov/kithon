from transPYler import handler, target_op
from transPYler.core import type_facts 


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
    return "\'"+val+"\'"

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

@handler("arg")
def arg(arg, type=""):
    return arg

target_op |= {"+": "+",
              "-": "-",
              "*": "*",
              "/": "/",
              "**": "**",
              "==": "=",
              "!=": "<>",
              ">": ">",
              "<": "<",
              ">=": ">=",
              "<=": "<=",
              "or": " or ",
              "and": " and ",
              "|": "|",
              "&": "&",
              "%": " mod ",
              "//": " div ",
              "not": "!",
              "is": "="
}

type_facts |= {('int', 'int', '%'): 'int',
               ('int', 'int', '+'): 'int',
               ('int', 'int', '-'): 'int',
               ('int', 'int', '//'): 'int',
               ('int', 'int', '*'): 'int'
               }
