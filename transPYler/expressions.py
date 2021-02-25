import _ast
import re
from . import core
from .utils import element_type, transpyler_type 
from .macros import macro, what_macro
from .core import parser, namespace, variables, handlers


def bin_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    if overload := what_macro((left, right, type(tree.op))):
        return overload(left, right)
    handler = handlers.get("bin_op")
    op = get_sign(tree.op)
    val = handler(left.get('val'), right.get('val'), op)
    return {'type': 'int', 'val': val}

def bool_op(tree):
    """Logic operation(or, and)"""
    els = list(map(lambda a: parser(a).get('val'), tree.values))
    op = get_sign(tree.op)
    if overload := what_macro((els[0], els[1], type(op))):
        return overload(els[0], els[1])
    handler = handlers.get("bool_op")
    els = list(map(lambda a: a.get('val'), els))
    return {'type': 'bool', 'val': handler(els, op)}

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = parser(tree.left)
    els = list(map(parser, tree.comparators))
    if overload := what_macro((f_el, els[0], type(tree.ops[0]))):
        return overload(f_el, els[0])
    handler = handlers.get("compare")
    ops = list(map(get_sign, tree.ops))
    els.insert(0, f_el)
    els = list(map(lambda a: a.get('val'), els))
    return {"type": 'bool', 'val': handler(els, ops)}

def un_op(tree):
    """unary operations(not)"""
    handler = handlers.get("un_op")
    op = get_sign(tree.op)
    el = parser(tree.operand)
    return {'type': el.get('type'),
            'val': handler(op, el.get('val'))
            }

def arg(tree):
    handler = handlers.get("arg")
    name = tree.arg
    if tree.annotation:
        return handler(name, type=parser(tree.annotation))
    return handler(name)

def attribute(tree):
    obj = parser(tree.value)
    _type = obj.get('type')
    obj = obj.get('val')
    attr = tree.attr
    #if _type in objects or obj in objects:
    #    if obj in objects:
    #        object = obj
    #    else:
    #        object = _type
    #    o = objects.get(object)
    #    if '__name__' in o.keys():
    #        obj = o.get('__name__')
    #    attr = o.get(attr).get('val')
    #    if callable(attr):
    #        return {'type': 'None',
    #                'obj': obj,
    #                'macros': attr
    #                }
    handler = handlers.get("attr")
    return {'type': 'None', 'val': handler(obj, attr)}

def function_call(tree):
    handler = handlers.get("call")
    args = tree.args
    ret_type = 'None'
    if type(tree.func) == _ast.Attribute:
        attr = attribute(tree.func)
        #if 'macros' in attr.keys():
        #    args.insert(0, attr.get('obj'))
        #    name = attr.get('macros')
        #else:
        name = attr.get('val')
    else:
        name = tree.func.id    
    if name1 := what_macro(name):
        if callable(name1):
            return macro(name1, tree.args)
        name = name1
        if 'type' in name:
            ret_type = name.get('type')
            name = name.get('val')
    elif name in objects:
        name = objects.get('__name__')
        handler = handlers.get('init')
    args = list(map(lambda a: parser(a).get('val'), tree.args))
    return {"type": ret_type, "val": handler(name, args)}

def _list(tree):
    handler = handlers.get("list")
    elements = list(map(parser, tree.elts))
    els = list(map(lambda a: a.get('val'), elements))
    if len(elements):
        _type = elements[0].get('type')
    else:
        _type = 'None'
    print(_type)
    return {"type": f'list<{_type}>', "val": handler(els, _type)}

def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Slice:
        handler = handlers.get("slice")
        lower = parser(sl.lower).get('val')
        upper = parser(sl.upper).get('val')
        step = parser(sl.step).get('val')
        val = handler(arr.get('val'), lower, upper, step)
        return {"type": arr.get('type'), "val": val}
    else:
        handler = handlers.get("index")
        index = parser(sl).get('val')
        val = handler(arr.get('val'), index)
        _type = element_type(arr)
        print(transpyler_type(arr))
        print(_type)
        return {"type": _type, "val": val}

def name(tree):
    handler = handlers.get("name")
    name = tree.id
    _type = str(variables.get(namespace).get(name))
    return {"type": _type, "val": handler(name)}

def const(tree):
    val = tree.value
    if type(val) == str:
        handler = handlers.get("string")
        return {"type": 'str', "val": handler(val)}
    handler = handlers.get("const")
    _type = str(type(val)).replace("<class '", "").replace("'>", "")
    return {"type": _type, "val": handler(str(val))}

signs = {}
get_sign = lambda op: signs.get(type(op))
type_by_op = {}
objects = {}
core.elements |= {_ast.Call: function_call,
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
                  type(None): lambda t: {'type': 'None',
                                         'val': 'None'
                                         }
}
