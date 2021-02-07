import _ast
import re
from . import core
from .core import parser, namespace, variables, handlers
from .macros import macro, what_macro


def bin_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = get_sign(tree.op)
    val = operation(left, right, op)
    return val

def bool_op(tree):
    """Logic operation(or, and)"""
    els = list(map(lambda a: parser(a).get('val'), tree.values))
    op = get_sign(tree.op)
    val = ''
    for i in els:
        pass
    return {'type': 'bool', 'val': handler(els, op)}

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = parser(tree.left).get('val')
    els = list(map(lambda a: parser(a).get('val'), tree.comparators))
    ops = []
    val = operation(f_el, els[0], ops[0])
    for el, op in zip(els[1], ):
        val += operation(left, right, op)
    return {"type": 'bool', 'val': handler(els, ops)}

def operation(left, right, op):
    handler = handlers.get("bbc_op")
    val = handler(left.get("val"), right.get("val"), op)
    return {'type': 'simple', 'val': val}

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
    _type = type_parse(obj.get('type'))
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
    if type(tree.func) == _ast.Attribute:
        attr = attribute(tree.func)
        #if 'macros' in attr.keys():
        #    args.insert(0, attr.get('obj'))
        #    name = attr.get('macros')
        #else:
        name = attr.get('val')
    else:
        name = tree.func.id    
    #if name in macros:
    #    return macro(name, tree.args)
    args = list(map(lambda a: parser(a).get('val'), tree.args))
    ret_type = 'None'
    return {"type": ret_type, "val": handler(name, args)}

def _list(tree):
    handler = handlers.get("list")
    elements = list(map(parser, tree.elts))
    els = list(map(lambda a: a.get('val'), elements))
    if len(elements):
        _type = elements[0].get('type')
    else:
        _type = 'None'
    return {"type": f'list[{_type}]', "val": handler(els, _type)}

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
        index = parser(sl).get('val')
        handler = handlers.get("index")
        val = handler(arr.get('val'), index)
        if re.search(r'\[.+]', arr.get('type')):
            _type = re.search(r'\[.+]', arr.get('type')).string[1:-1]
        else:
            _type = arr.get('type')
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
macros = {}
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
