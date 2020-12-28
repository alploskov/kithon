def bin_op(left, right, op):
    return f"({left}{op}{right})"

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
    other_el = els[1:]
    op_and_el="".join([ops[i]+el for i, el in enumerate(other_el)])
    return first_el+op_and_el

def bool_op(els, op):
    return els[0]+" "+"".join([op+" "+i for i in els[1:]])

def call(name, args):
    args = ", ".join(args)
    return f"{name}({args})"

def attr(obj, attr_name):
    return f"{obj}.{attr_name}"

def arg(arg):
    return arg

def _list(ls):
    return f"[{', '.join(ls)}]"

def slice(arr, *args):
    first = args[0]
    if len(args)==1:
        return f"{arr}[{first}]"
