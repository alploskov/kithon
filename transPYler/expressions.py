import _ast
import ast
import os
import importlib


signs = {}

def get_sign(op):
    return signs.get(type(op))
    
def bin_op(tree):
    """Math operation"""
    handler = expr_handlers.get("bin_op")
    left = parser(tree.left)
    right = parser(tree.right)
    op = get_sign(tree.op)
    return handler(left, right, op)

def bool_op(tree):
    """Logic operation"""
    handler = expr_handlers.get("bool_op")
    els = list(map(parser, tree.values))
    op = get_sign(tree.op) 
    return handler(els, op)

def compare(tree):
    """Compare operation"""
    handler = expr_handlers.get("compare")
    els = [parser(tree.left)]
    els += list(map(parser, tree.comparators))
    ops = list(map(get_sign, tree.ops))
    return handler(els, ops)

function_analog_method = {}
function_analog_func = {}
lib = {}

def args(tree):
    handler = expr_handlers.get("args")
    return handler(list(map(parser, tree)))

def arg(tree):
    handler = expr_handlers.get("arg")
    #_type = parser(tree.annotation)
    name =  tree.arg
    return handler(name)

def attribute(tree):
    handler = expr_handlers.get("attr")
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
    handler = expr_handlers.get("call")
    if type(tree.func) == _ast.Attribute:
        name = attribute(tree.func)        # if called function is method of any class that name will be an attribute of the class
    else:
        name = tree.func.id
        
    arg = args(tree.args)   

    if name in function_analog_func:
        name = function_analog_func.get(name)

    elif name in function_analog_method:
        val = tree.args[0]
        name = attribute(ast.Attribute(value=val, attr=name))   # func -> attribute

        if len(tree.args)<=1:
            return name
        arg = args(tree.args[1:])

    return handler(name, arg)

def _list(tree):
    handler = expr_handlers.get("list")
    return handler(args(tree.elts))

def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Index:
        index = parser(sl.value)
        handler = expr_handlers.get("index")
        return handler(arr, index)
    elif type(sl) == _ast.Slice:
        handler = expr_handlers.get("slice")
        
def name(tree):
    handler = expr_handlers.get("name")
    name = tree.id
    return handler(name)

def const(tree):
    val = tree.value
    if type(val) == str:
        handler = expr_handlers.get("string") 
        return handler(val)
    handler = expr_handlers.get("const")
    return handler(str(val))


operation = {_ast.Call: function_call,
             _ast.BinOp: bin_op,
             _ast.BoolOp: bool_op,
             _ast.Compare: compare,
             _ast.List: _list,
             _ast.Attribute: attribute,
             _ast.Name: name,
             _ast.Subscript: slice,
             _ast.Constant: const,
             _ast.arg: arg
}

expr_handlers = {}

def parser(param):
    _type = type(param)
    return operation.get(_type)(param)
