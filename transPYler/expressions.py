import _ast
import ast
import os
import importlib

signs = {}
def get_sign(op):
    return translator.signs.get(type(op))


def bin_op(tree, handler):
    """Math operation"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = signs.get(type(tree.op))
    return handler(left, right, op)


def bool_op(tree, handler):
    """Logic operation"""
    els = list(map(parser, tree.values))
    op = get_sign(tree.op)
    return handler(els, op)


def compare(tree, handler):
    """Compare operation"""
    els = parser(tree.left)
    els += list(map(parser, tree.comparators))
    ops = list(map(get_sign, tree.ops))
    return handler(els, ops)


def attribute(tree, handler):
    attr_name = tree.attr
    if tree.attr in translator.function_analog.method:
        attr_name = translator.function_analog.method.get(attr_name)
    obj = parser(tree.value)
    return eval(config.get("attr"))


def function_call(tree, handler):
    if type(tree.func) == _ast.Attribute:
        name = attribute(tree.func)
    else:
        name = parser(tree.func)
        
    arg = args(tree.args)

    if name in translator.function_analog.func:
        name = translator.function_analog.func.get(name)

    elif name in translator.function_analog.method:
        val = tree.args[0]
        name = attribute(ast.Attribute(value=val, attr=name))
        if len(tree.args)<=1:
            return name
        arg = args(tree.args[1:])

    elif name in translator.macros:
        return eval(f"{translator.macros.get(name)}({arg})")

    return eval('f"{name}({arg})"')


def _list(tree, handler):
    t = type(tree)
    if t == _ast.List or t == _ast.Tuple:
        ret = []
        for i in tree.elts:
            ret.append(parser(i))
        is_tuple = ""
        if t == _ast.Tuple:
            is_tuple = ""
        return is_tuple + str(ret)

    elif t == _ast.Dict:
        pass


def args(tree, handler):
    return ", ".join(list(map(parser, tree)))

def name(tree, handler):
    name = tree.id
    return handler(name)

def const(tree, handler):
    val = tree.value
    if type(val) == str:
        return "\"" + val + "\""
    return handler(str(val))

operation = {_ast.Call: function_call,
             _ast.BinOp: bin_op,
             _ast.BoolOp: bool_op,
             _ast.Compare: compare,
             _ast.List: _list,
             _ast.Attribute: attribute,
             _ast.Name: name,
             _ast.Constant: const
}

expr_handlers = {}

def parser(param):
    _type = type(param)
    return operation.get(_type)(param, expr_handlers.get(_type))
