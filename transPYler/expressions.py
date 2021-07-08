import _ast
import re
from . import core
from .utils import element_type, add_var, transpyler_type
from .core import parser, objects, tmpls, op_to_str, macros
from jinja2 import Template
from jinja2.nativetypes import NativeTemplate


def math_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = op_to_str(tree.op)
    return bin_op(left, right, op)     

def bool_op(tree):
    """Boolean logic operation(or, and)"""
    els = list(map(parser, tree.values))
    op = op_to_str(tree.op)
    expr = bin_op(els[0], els[1], op)
    for i in els[2:]:
        expr = bin_op(expr, i, op)
    return expr

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = parser(tree.left)
    els = list(map(parser, tree.comparators))
    ops = list(map(op_to_str, tree.ops))
    expr = bin_op(f_el, els[0], ops[0])
    for i in zip(els[:-1], els[1:], ops[1:]):
        expr = bin_op(expr, bin_op(i[0], i[1], i[2]), 'and')
    return expr

def bin_op(left, right, op):
    expr = (transpyler_type(left), transpyler_type(right), op)
    _type = 'None'
    if op in ['and', 'or', '==', '!=', '>',
              '<', '>=', '<=', 'in', 'is']:
        _type = 'bool'
    ex_data = [
        (expr[0], expr[1], expr[2]),
        (expr[0], expr[1], 'any'),
        (expr[0], 'any', expr[2]),
        ('any', expr[1], expr[2]),
        ('any', expr[1], 'any'),
        ('any', 'any', expr[2]),
        (expr[0], 'any', 'any'),
        ('any', 'any', 'any'),
    ]
    for i in ex_data:
        if ex := macros.get(i):
            if 'type' in ex:
                _type = NativeTemplate(ex.get('type')).render(
                    l=left(),
                    r=right(),
                    l_type=left.type,
                    r_type=right.type
                )
            if 'code' in ex:
                return {
                    'type': _type,
                    'val': Template(ex.get('code')).render(
                        l=left(),
                        r=right(),
                        l_type=left.type,
                        r_type=right.type
                    )
                }
    tmp = tmpls.get('bin_op')
    return {
        'type': _type,
        'val': tmp.render(
            left=left,
            right=right,
            op=tmpls.get('operations').get(op)
        )
    }

def un_op(tree):
    """Unary operations(not...)"""
    tmp = tmpls.get('un_op')
    op = tmpls.get('operations').get(op_to_str(tree.op))
    el = parser(tree.operand)
    return {
        'type': el.type,
        'val': tmp.render(
            op=op,
            el=el
        )
    }

def arg(tree):
    tmp = tmpls.get("arg")
    name = tree.arg
    if tree.annotation:
        t = tree.annotation.id
        add_var(name, t)
        _type = tmpls.get('types').get(t) if t in tmpls.get('types') else t
    else:
        t = ''
        _type = ''
        add_var(name, '')
    return {
        'type': t,
        'val': tmp.render(arg=name, _type=_type)
    }

def macro(m, args):
    if 'args' in m:
        _args = m.get('args')
    else:
        _args = [f'_{i+1}' for i in range(len(args))] 
    args = dict(zip(_args, args))
    tmp = Template(m.get('code'))
    return tmp.render(args=args)

def attribute(tree, args=None):
    obj = parser(tree.value)
    ret_type = 'None'
    attr = tree.attr
    if (transpyler_type(obj) in objects) or (obj() in objects):
        if obj() in objects:
            objct = obj()
        else:
            objct = transpyler_type(obj)
        attrs = objects.get(objct)
        if '__name__' in attrs.keys():
            obj['val'] = attrs.get('__name__')
        
        attr = attrs.get(attr)
        if 'type' in attr:
            ret_type = attr.get('type')
        if 'alt_name' in attr:
            attr = attr.get('alt_name')
        elif 'code' in attr:
            args = []
            args.insert(0, obj())
            return {
                'type': ret_type,
                'val': macro(attr, args)
            }
    if type(args) == list:
        tmp = tmpls.get('method')
    else:
        tmp = tmpls.get('attr')
    val = tmp.render(
        obj=obj(),
        attr_name=attr,
        args=args
    )
    return {'type': ret_type, 'val': val}

def function_call(tree):
    args = [parser(a)() for a in tree.args]
    ret_type = 'None'
    if type(tree.func) == _ast.Attribute:
        return attribute(tree.func, args=args)
    else:
        tmp = tmpls.get('call')
        name = tree.func.id
        if name in macros:
            macr = macros.get(name)
            if 'type' in macr:
                ret_type = macr.get('type')
            if 'alt_name' in macr:
                name = macr.get('alt_name')
            elif 'code' in macr:
                return {
                    'type': ret_type,
                    'val': macro(macr, args)
                }
    return {
        'type': ret_type,
        'val': tmp.render(name=name, args=args)
    }

def _list(tree):
    tmp = tmpls.get('list')
    elements = list(map(parser, tree.elts))
    ls = list(map(lambda a: a(), elements))
    if len(elements):
        el_type = elements[0].type
    else:
        el_type = 'None'
    if 'types' in tmpls:
        r_type = tmpls.get('types').get(el_type) or el_type
    else:
        r_type = el_type
    return {
        'type': {
            'base_type': 'list',
            'el_type': el_type 
        },
        'val': tmp.render(
            ls=ls,
            _type=r_type
        )
    }

def _dict(tree):
    tmp = tmpls.get('dict')
    keys = list(map(parser, tree.keys))
    values = list(map(parser, tree.values))
    if len(keys):
        el_type = values[0].type
        key_type = keys[0].type
    else:
        el_type = 'None'
        key_type = 'None'
    if 'types' in tmpls:
        r_key_type = tmpls.get('types').get(key_type)
        r_el_type =tmpls.get('types').get(el_type)
    else:
        r_key_type = key_type
        r_el_type = el_type
    key_val = list(map(
        lambda x: {'key': x[0], 'val': x[1]},
        zip(keys, values)
    ))
    return {
        'type': {
            'base_type': 'dict',
            'key_type': key_type,
            'el_type': el_type 
        },
        'val': tmp.render(
            key_val=key_val,
            el_type=r_el_type,
            key_type=r_key_type
        )
    }

def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Slice:
        tmp = tmpls.get('slice')
        lower = parser(sl.lower)
        upper = parser(sl.upper)
        step = parser(sl.step)
        val = tmp.render(
            arr=arr,
            low=lower,
            up=upper,
            step=step
        )
        return {'type': arr.type, 'val': val}
    else:
        tmp = tmpls.get('index')
        index = parser(sl)()
        val = tmp.render(arr=arr, val=index)
        _type = element_type(arr)
        return {'type': _type, 'val': val}

def name(tree):
    tmp = tmpls.get('name')
    name = tree.id
    _type = core.variables.get(core.namespace).get(name)
    return {'type': _type, 'val': tmp.render(name=name, type=_type)}

def const(tree):
    val = tree.value
    if type(val) == str:
        tmp = tmpls.get('string')
        return {'type': 'str', 'val': tmp.render(val=val)}
    tmp = tmpls.get('const')
    _type = re.search(r'\'.*\'', str(type(val))).group()[1:-1]
    return {'type': _type, 'val': tmp.render(val=val, type=_type)}

core.elements |= {
    _ast.Call: function_call,
    _ast.BinOp: math_op,
    _ast.BoolOp: bool_op,
    _ast.Compare: compare,
    _ast.List: _list,
    _ast.Attribute: attribute,
    _ast.Name: name,
    _ast.Subscript: slice,
    _ast.Constant: const,
    _ast.arg: arg,
    _ast.UnaryOp: un_op,
    _ast.Dict: _dict,
    type(None): lambda t: {
        'type': 'None',
        'val': ''
    }
}
