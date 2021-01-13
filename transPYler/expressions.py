import ast
import _ast 
from .core_data import created_variables, namespace, handlers, Parser
print(handlers)
def operator_overloading(left, right, op):
    l_type = left.get('type')
    r_type = right.get('type') 
    handler = operator_overloading_data.get((l_type, r_type, op))
    return handler(left, right)

def auto_type(l_type, r_type, op):
    if (l_type, r_type, op) in type_by_bin_op:
        return type_by_bin_op.get((l_type, r_type, op))

def bin_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = get_sign(tree.op)
    
    l_type = left.get('type')
    r_type = right.get('type')
    if (l_type, r_type, op) in operator_overloading_data:
        operator_overloading(left, right, op)
    
    _type = auto_type(left.get("type"), right.get("type"), op)
    if callable(op):
        val = op(left, right)
    else:
        handler = handlers.get("bin_op")
        val = handler(left.get("val"), right.get("val"), op)
    return {"type": _type, "val": val}

def bool_op(tree):
    """Logic operation(or, and)"""
    handler = handlers.get("bool_op")
    els = list(map(parser, tree.values))
    op = get_sign(tree.op)
    return handler(els, op)

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    handler = handlers.get("compare")
    els = [parser(tree.left)]
    els += list(map(parser, tree.comparators))
    ops = list(map(get_sign, tree.ops))
    return handler(els, ops)

def un_op(tree):
    """unary operations(not)"""
    handler = handlers.get("un_op")
    op = get_sign(tree.op)
    el = parser(tree.operand)
    return handler(op, el)

def arg(tree):
    handler = handlers.get("arg")
    name = tree.arg
    if tree.annotation:
        return handler(name, type=parser(tree.annotation))
    return handler(name)

def attribute(tree):
    handler = handlers.get("attr")
    obj = parser(tree.value)
    attr_name = tree.attr
    if obj in lib:
        l = lib.get(obj)
        obj = l.get("__name__")
        attr_name = l.get(attr_name)
    return handler(obj, attr_name)

def function_call(tree):
    handler = handlers.get("call")
    if type(tree.func) == _ast.Attribute:
        name = attribute(tree.func)
    else:
        name = tree.func.id

    if name in function_analog_func:
        name = function_analog_func.get(name)
        if callable(name):
            param = []
            for i in tree.args:
                if type(i) == _ast.Constant:
                    val = i.value
                    if type(val) == str:
                        val = '"'+val+'"'
                    val = str(val)
                else:
                    val = parser(i)
                param.append(val)
            param = str(tuple(param))
            return eval(f"name{param}")
        
    args = list(map(parser, tree.args))
    ret_type = None
    return {"type": ret_type, "val": handler(name, args)}


def _list(tree):
    handler = handlers.get("list")
    return handler(list(map(parser, tree.elts)))


def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Index:
        index = parser(sl.value)
        handler = handlers.get("index")
        return handler(arr, index)
    elif type(sl) == _ast.Slice:
        handler = handlers.get("slice")
        lower = parser(sl.lower)
        upper = parser(sl.upper)
        step = parser(sl.step)
        return handler(arr, lower, upper, step)


def name(tree):
    handler = handlers.get("name")
    name = tree.id
    _type = vars.get(namespace).get(name).get("type")
    return {"type": _type, "val": handler(name)}

def const(tree):
    val = tree.value
    if type(val) == str:
        handler = handlers.get("string")
        return {"type": 'str', "val": handler(val)}
    handler = handlers.get("const")
    _type = str(type(val)).replace("<class '", "").replace("'>", "")
    return {"type": _type, "val": handler(str(val))}

elements = {_ast.Call: function_call,
            _ast.BinOp: bin_op,
            _ast.BoolOp: bool_op,
            _ast.Compare: compare,
            _ast.List: _list,
            _ast.Attribute: attribute,
            _ast.Name: name,
            _ast.Subscript: slice,
            _ast.Constant: const,
            _ast.arg: arg,
            _ast.UnaryOp: un_op,
            type(None): lambda t: None
}
parser = Parser(elements).parser


function_analog_func = {}
lib = {}
types = {}
signs = {}
get_sign = lambda op: signs.get(type(op))
operator_overloading_data = {} 
type_by_op = {}
