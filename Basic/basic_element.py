import _ast
from Basic.execution_environment_api import function_analog, macros
from Basic.conf import configurator
config=configurator.conf_get("Basic/conf/js.cc")
space=" "
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
    _ast.And:"&&",
    _ast.Or:"|",
    _ast.BitAnd:"&",
    _ast.BitOr:"|"
}

def get_sign(op):
    return signs.get(type(op))

def bin_op(tree):
    """Math operation"""
    left=parser(tree.left)
    right=parser(tree.right)
    sign=signs.get(type(tree.op))
    return eval(config.get("bin_op"))

def bool_op(tree):
    """Logic operation"""
    op=get_sign(tree.op)
    els=list(map(parser, tree.values))
    first_el=els[0]
    other_el=els[1:]
    return eval(config.get("bool_op"))

def compare(tree):
    """Compare operation"""
    other_el=list(map(parser, tree.comparators))
    first_el=parser(tree.left)
    ops=list(map(get_sign, tree.ops))
    return eval(config.get("comp"))

def attribute(tree):
    attr_name=tree.attr
    if tree.attr in function_analog.method:
        attr_name=function_analog.method.get(attr_name)
    _class=tree.value.id
    return eval(config.get("attr"))

def function_call(tree):
    if type(tree.func)==_ast.Attribute:
        name=attribute(tree.func)
    else:
        name=tree.func.id

    arg=args(tree.args)
    if name in function_analog.func:
        name=function_analog.func.get(name)
        return f"{name}({arg})"

    elif name in function_analog.method:
        return parser(tree.args[0])+function_analog.method.get(name)

    elif name in dir(macros):
        return eval(f"macros.{name}({arg})")

    else:
        return f"{name}({arg})"

def data_struct(tree):
    t=type(tree)
    if t==_ast.List or t==_ast.Tuple:
        ret=[]
        for i in tree.elts:
            ret.append(parser(i))
        is_tuple=""
        if t==_ast.Tuple:
            is_tuple=""
        return is_tuple+str(ret)

    elif t==_ast.Dict:
        pass

def args(tree):
    return ", ".join(list(map(parser, tree)))

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

    elif _type==_ast.arg:
        return param.arg

    else:
        return operation.get(_type)(param)
