import ast
import _ast
from .tools import Parser


def bin_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = get_sign(tree.op)
    if callable(op):
        return op(left, right)
    handler = handlers.get("bin_op")
    return handler(left, right, op)


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
    "unary operations(not)"
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
    elif tree.attr in function_analog_method:
        attr_name = function_analog_method.get(attr_name)
    return handler(obj, attr_name)


def function_call(tree):
    handler = handlers.get("call")
    if type(tree.func) == _ast.Attribute:
        name = attribute(tree.func)
    else:
        name = tree.func.id

    args = list(map(parser, tree.args))
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
    elif name in function_analog_method:
        val = tree.args[0]
        name = attribute(ast.Attribute(value=val, attr=name))
        if len(tree.args) <= 1:
            return name
        args = args[1:]
    return handler(name, args)


def _list(tree):
    handler = handlers.get("list")
    return handler(tree.elts)


def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Index:
        index = parser(sl.value)
        handler = handlers.get("index")
        return handler(arr, index)
    elif type(sl) == _ast.Slice:
        handler = handlers.get("slice")
        return handler()


def name(tree):
    handler = handlers.get("name")
    name = tree.id
    return handler(name)


def const(tree):
    val = tree.value
    if type(val) == str:
        handler = handlers.get("string")
        return handler(val)
    handler = handlers.get("const")
    return handler(str(val))


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
            _ast.UnaryOp: un_op
}
parser = Parser(elements).parser

handlers = {}
function_analog_method = {}
function_analog_func = {}
lib = {}
types = {}
signs = {}
get_sign = lambda op: signs.get(type(op))
