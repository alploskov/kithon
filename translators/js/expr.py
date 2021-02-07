def op(left, right, op):
    return f"({left} {op} {right})"

def un_op(op, el):
    return f"{op}({el})"

def name(name):
    return name

def const(val):
    return val

def c_str(val):
    return "\""+val+"\""
    
def compare(els, ops):
    first_el = els[0]
    other_els = els[1:]
    op_and_els = "".join([ops[i]+el for i, el in enumerate(other_els)])
    return first_el+op_and_els

def bool_op(els, op):
    return els[0]+" "+"".join([op+" "+i for i in els[1:]])

def call(name, args):
    args = ", ".join(args)
    return f"{name}({args})"

def attr(obj, attr_name):
    return f"{obj}.{attr_name}"

def arg(arg, type=""):
    return arg

def _list(ls, _type):
    return f"[{', '.join(ls)}]"

def index(arr, val):
    if val[0] == '-':
        return f"{arr}[{arr}.length{val}]"
    return f"{arr}[{val}]"

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
