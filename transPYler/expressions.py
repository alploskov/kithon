import _ast
import re
import math
from .utils import element_type, transpyler_type
from jinja2 import Template
from jinja2.nativetypes import NativeTemplate


def un_op(self, tree):
    """Unary operations(not...)"""
    tmp = self.tmpls.get('un_op')
    op = self.tmpls.get('operations').get(self.op_to_str(tree.op))
    el = self.parser(tree.operand)
    return {
        'type': el.type,
        'val': tmp.render(
            op=op,
            el=el
        )
    }

def math_op(self, tree):
    """Math operation(+, -, *, /...)"""
    left = self.parser(tree.left)
    right = self.parser(tree.right)
    op = self.op_to_str(tree.op)
    return bin_op(self, left, right, op)     

def bool_op(self, tree):
    """Boolean logic operation(or, and)"""
    els = list(map(self.parser, tree.values))
    op = self.op_to_str(tree.op)
    expr = bin_op(self, els[0], els[1], op)
    for i in els[2:]:
        expr = bin_op(self, expr, i, op)
    return expr

def compare(self, tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = self.parser(tree.left)
    els = list(map(self.parser, tree.comparators))
    ops = list(map(self.op_to_str, tree.ops))
    expr = bin_op(self, f_el, els[0], ops[0])
    for i in zip(els[:-1], els[1:], ops[1:]):
        expr = bin_op(self, expr, bin_op(i[0], i[1], i[2]), 'and')
    return expr

def bin_op(self, left, right, op):
    left_t = transpyler_type(left)
    right_t = transpyler_type(right)
    _type = 'None'
    if op in [
        'and', 'or', '==', '!=', '>',
        '<', '>=', '<=', 'in', 'is'
    ]:
        _type = 'bool'
    attrs = self.objects.get(
        left_t, 
        self.objects.get('any', [])
    )
    if op in attrs:
        ex = self.objects[left_t][op].get(right_t, 'any')
        if 'type' in ex:
            _type = NativeTemplate(ex.get('type')).render(
                l=left,
                r=right
            )
        if 'code' in ex:
            return {
                'type': _type,
                'val': macro(ex, [left, right], ['l', 'r'])
            }
    tmp = self.tmpls.get('bin_op')
    return {
        'type': _type,
        'val': tmp.render(
            left=left,
            right=right,
            op=self.tmpls.get('operations').get(op)
        )
    }

def arg(self, tree):
    tmp = self.tmpls.get('arg')
    name = tree.arg
    if tree.annotation:
        t = tree.annotation.id
        add_var(name, t)
        _type = self.tmpls.get('types').get(t, t)
    else:
        t = 'None'
        _type = 'None'
        add_var(name, '')
    return {
        'type': t,
        'val': tmp.render(arg=name, type=_type)
    }

def macro(m, args, args_names=[]):
    if 'args' in m:
        args_names = m.get('args')
        if len(args_names) < len(args):
            args_names.insert(0, 'obj')
    elif args_names == []:
        args_names = [f'_{i+1}' for i in range(len(args))]
    args = dict(zip(args_names, args))
    code = m.get('code')
    return tmp.render(**args)

def attribute(self, tree, args=None):
    objects = self.objects
    obj = self.parser(tree.value)
    ret_type = 'None'
    attr = tree.attr
    attrs = objects.get(
        transpyler_type(obj),
        objects.get(
            obj(),
            objects.get('any', [])
        )
    )
    if attr in attrs:
        macro_attr = attrs.get(attr)
        obj.val = attrs.get('__name__', obj())
        ret_type = macro_attr.get('type', ret_type)
        attr = macro_attr.get('alt_name', attr)
        if 'code' in macro_attr:
            args = args or []
            args.insert(0, obj())
            return {
                'type': ret_type,
                'val': macro(macro_attr, args)
            }
    if type(args) == list:
        tmp = self.tmpls.get('method')
        args = [a() for a in args]
    else:
        tmp = self.tmpls.get('attr')
    val = tmp.render(
        obj=obj(),
        attr_name=attr,
        args=args
    )
    return {'type': ret_type, 'val': val}

def function_call(self, tree):
    args = [self.parser(a) for a in tree.args]
    if type(tree.func) == _ast.Attribute:
        return attribute(self, tree.func, args=args)
    tmp = self.tmpls.get('call')
    name = tree.func.id
    ret_type = 'None'
    if name in self.variables.get(self.namespace):
        ret_type = self.variables.get(self.namespace)[name]['ret_type']
    elif name in self.macros:
        macr = self.macros.get(name)
        ret_type = macr.get('type', ret_type)
        name = macr.get('alt_name', name)
        if 'code' in macr:
            return {
                'type': ret_type,
                'val': macro(macr, args)
            }
    args = [a() for a in args]
    return {
        'type': ret_type,
        'val': tmp.render(name=name, args=args)
    }

def _list(self, tree):
    tmp = self.tmpls.get('list')
    elements = list(map(self.parser, tree.elts))
    if len(elements):
        el_type = elements[0].type
    else:
        el_type = 'None'
    ren_type = self.tmpls.get('types').get(el_type, el_type)
    return {
        'type': {
            'base_type': 'list',
            'el_type': el_type 
        },
        'val': tmp.render(
            ls=elements,
            type=ren_type
        )
    }

def _dict(self, tree):
    tmp = self.tmpls.get('dict')
    keys = list(map(self.parser, tree.keys))
    values = list(map(self.parser, tree.values))
    if len(keys):
        el_type = values[0].type
        key_type = keys[0].type
    else:
        el_type = 'None'
        key_type = 'None'
    ren_key_type = self.tmpls.get('types').get(key_type, key_type)
    ren_el_type = self.tmpls.get('types').get(el_type, el_type)
    key_val = [{'key': x[0], 'val': x[1]} for x in zip(keys, values)]
    return {
        'type': {
            'base_type': 'dict',
            'key_type': key_type,
            'el_type': el_type 
        },
        'val': tmp.render(
            key_val=key_val,
            el_type=ren_el_type,
            key_type=ren_key_type
        )
    }

def slice(self, tree):
    obj = self.parser(tree.value)
    sl = tree.slice
    if type(sl) != _ast.Slice:
        tmp = self.tmpls.get('index')
        index = self.parser(sl)
        val = tmp.render(obj=obj, val=index)
        _type = element_type(obj)
        return {'type': _type, 'val': val}
    tmp = self.tmpls.get('slice')
    lower = self.parser(sl.lower)
    upper = self.parser(sl.upper)
    step = self.parser(sl.step)
    val = tmp.render(
        obj=obj,
        low=lower,
        up=upper,
        step=step
    )
    return {'type': obj.type, 'val': val}

def name(self, tree):
    tmp = self.tmpls.get('name')
    name = tree.id
    ctx = {
        _ast.Store: 'store',
        _ast.Load: 'load'
    }.get(type(tree.ctx))
    _type = self.variables.get(self.namespace).get(name)
    macr = self.macros.get(name, {})
    _type = macr.get('type', _type)
    name = macr.get('alt_name', name)
    return {
        'type': _type,
        'val': tmp.render(name=name, type=_type, ctx=ctx)
    }

def const(self, tree):
    _val = tree.value
    _type = type(_val)
    if _type == bool: return {
        'type': 'bool',
        'val': self.self.tmpls.get('bool').render(val=_val)
    }
    elif _type == int: return {
        'type': 'int',
        'val': self.tmpls.get('int').render(val=_val)
    }
    elif _type == float: return {
        'type': 'float',
        'val': self.tmpls.get('float').render(
            val=_val,
            parts=math.modf(_val)
        )
    }
    elif _type == str: return {
        'type': 'str',
        'val': self.tmpls.get('str').render(val=_val)
    }
