import _ast
#from Lib import *
from Basic.execution_environment_api import function_analog, api


signs={_ast.Add:"+",
    _ast.Mult:"*",
    _ast.Sub:"-",
    _ast.Div:"/",
    _ast.Eq:"==",
    _ast.NotEq:"!=",
    _ast.Gt:">",
    _ast.Lt:"<",
    _ast.GtE:">=",
    _ast.LtE:"<=",
    _ast.And:"&",
    _ast.Or:"|",
    _ast.BitAnd:"&",
    _ast.BitOr:"|"
}

def bin_op(tree):
    """Math operation"""
    return f"{parser(tree.left)} {signs.get(type(tree.op))} {parser(tree.right)}"

def bool_op(tree):
    """Logic operation"""
    el=""
    for i in tree.values[:-1]:
        el+=parser(i)+" "
        el+=signs.get(type(tree.op))+" "
    el+=parser(tree.values[-1])
    return el

def compare(tree):
    ret=parser(tree.left)
    for i in range(len(tree.ops)):
        ret+=signs.get(type(tree.ops[i]))
        ret+=parser(tree.comparators[i])
    return ret

def attribute(tree):
    return f"{tree.value.id}.{tree.attr}"

def function_call(tree):
    if type(tree.func)==_ast.Attribute:
        name=attribute(tree.func)
    else:
        name=tree.func.id
    arg=""
    if len(tree.args)>0:
        for i in tree.args[:-1]:
            arg+=parser(i)+", "
        arg+=parser(tree.args[-1])

    if name in function_analog.func:
        name=function_analog.func.get(name)
        return f"{name}({arg})"

    elif name in function_analog.method:
        return parser(tree.args[0])+function_analog.method.get(name)

    elif name in dir(api):
        return eval(f"api.{name}({arg})")
    else:
        return f"{name}({arg})"



def data_struct(tree):
    t=type(tree)
    if t==_ast.List or t==_ast.Tuple:
        ret=[]
        for i in tree.elts:
            ret.append(parser(i))
        return str(ret)

    elif t==_ast.Dict:
        pass
    pass

def arg(tree):
    args=[i.arg for i in tree]
    return tuple(args)

operation={_ast.Call:function_call,
    _ast.BinOp:bin_op,
    _ast.BoolOp:bool_op,
    _ast.Compare:compare,
    _ast.List:data_struct,
    _ast.Dict:data_struct,
    _ast.Tuple:data_struct,
    _ast.Attribute:attribute
}

def parser(param):
    _type=type(param)
    if _type==_ast.Name:
        return param.id

    elif _type==_ast.Constant:
        val=param.value
        if type(val)==str:
            return "\""+val+"\""
        return str(val)

    else:
        return operation.get(_type)(param)
