import ast
import _ast
import re
import math
import copy
from .utils import element_type, transpyler_type, getvar, types_to_id
from jinja2 import Template
from jinja2.nativetypes import NativeTemplate
from .types import List
import pprint


def un_op(self, tree):
    """Unary operations(not...)"""
    tmp = self.tmpls.get('un_op')
    op = self.tmpls.get('operations').get(self.op_to_str(tree.op))
    el = self.visit(tree.operand)
    return {
        'type': el.type,
        'val': tmp.render(
            op=op,
            el=el
        )}

def math_op(self, tree):
    """Math operation(+, -, *, /...)"""
    left = self.visit(tree.left)
    right = self.visit(tree.right)
    op = self.op_to_str(tree.op)
    return bin_op(self, left, right, op)     

def bool_op(self, tree):
    """Boolean logic operation(or, and)"""
    els = list(map(self.visit, tree.values))
    op = self.op_to_str(tree.op)
    expr = bin_op(self, els[0], els[1], op)
    for i in els[2:]:
        expr = bin_op(self, expr, i, op)
    return expr

def compare(self, tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = self.visit(tree.left)
    els = list(map(self.visit, tree.comparators))
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
    attrs = self.tmpls.get(
        left_t,
        self.tmpls.get('any', [])
    )
    if op in attrs:
        ex = attrs[op].get(right_t, attrs[op].get('any', []))
        if 'type' in ex:
            _type = NativeTemplate(ex.get('type')).render(
                l=left,
                r=right
            )
        if 'code' in ex:
            return {
                'type': _type,
                'val': macro(self,ex, [left, right], ['l', 'r'])
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
    t = getattr(tree.annotation, 'id', 'any')
    self.variables.update({f'{self.namespace}.{name}': {
        'type': [t]
    }})
#    _type = self.tmpls.get('types').get(t)
    return {
        'type': t,
        'val': tmp.render(arg=name, _type='_type')
    }

def macro(self,m, args, args_names=[]):
    tmp = Template(m.get('code'))
    if 'args' in m:
        args_names = m.get('args')
        if type(args_names) == str and args_names == '*args':
            return tmp.render(args=args, ctx=self)
        if len(args_names) < len(args):
            args_names.insert(0, 'obj')
    elif args_names == []:
        args_names = [f'_{i+1}' for i in range(len(args))]
    args = dict(zip(args_names, args))
    return tmp.render(**args, ctx=self)

def attribute(self, tree, args=None):
    tmpls = self.tmpls
    obj = self.visit(tree.value)
    ret_type = 'None'
    attr = tree.attr
    attrs = tmpls.get(
        transpyler_type(obj),
        tmpls.get(
            tree.value.id,
            tmpls.get('any', [])))
    if attr in attrs:
        macro_attr = attrs.get(attr)
        ret_type = macro_attr.get('type', ret_type)
        attr = macro_attr.get('alt_name', attr)
        if 'code' in macro_attr:
            args = args or []
            args.insert(0, obj())
            return {
                'type': ret_type,
                'val': macro(self,macro_attr, args)}
    if type(args) == list:
        tmp = self.tmpls.get('callmethod')
        args = [a() for a in args]
    else:
        tmp = self.tmpls.get('getattr')
    val = tmp.render(
        obj=obj,
        attr_name=attr,
        args=args)
    return {'type': ret_type, 'val': val}

def function_call(self, tree):
    args = [self.visit(a) for a in tree.args]
    if type(tree.func) == _ast.Attribute:
        return attribute(self, tree.func, args=args)
    name = tree.func.id
    ret_type = 'None'
    if name in self.tmpls:
        macr = self.tmpls.get(name)
        ret_type = macr.get('type', ret_type)
        name = macr.get('alt_name', name)
        if 'code' in macr:
            return {
                'type': ret_type,
                'val': macro(self,macr, args)
            }
    tmp = self.tmpls.get('callfunc')
    return {
        'type': ret_type,
        'val': tmp.render(name=name, args=args)
    }

def _list(self, tree):
    tmp = self.tmpls.get('list')
    elements = list(map(self.visit, tree.elts))
    if len(elements):
        el_type = elements[0].type
    else:
        el_type = 'None'
    ren_type = self.tmpls.get('types').get(el_type, el_type)
    return {
        'type': List(el_type),
        'val': tmp.render(
            ls=elements,
            type=ren_type
        )
    }

def _dict(self, tree):
    tmp = self.tmpls.get('dict')
    keys = list(map(self.visit, tree.keys))
    values = list(map(self.visit, tree.values))
    if len(keys):
        el_type = values[0].type
        key_type = keys[0].type
    else:
        el_type = 'any'
        key_type = 'any'
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
    obj = self.visit(tree.value)
    sl = tree.slice
    if type(sl) != _ast.Slice:
        tmp = self.tmpls.get('index')
        index = self.visit(sl)
        val = tmp.render(obj=obj, val=index, ctx=self)
        _type = element_type(obj)
        return {'type': _type, 'val': val}
    tmp = self.tmpls.get('slice')
    lower = self.visit(sl.lower)
    upper = self.visit(sl.upper)
    step = self.visit(sl.step)
    val = tmp.render(
        obj=obj,
        low=lower,
        up=upper,
        step=step,
        ctx=self
    )
    return {'type': obj.type, 'val': val}

def name(self, tree):
    tmp = self.tmpls.get('name')
    name = tree.id
    ctx = {
        _ast.Store: 'store',
        _ast.Load: 'load'
    }.get(type(tree.ctx))
    _type = 'None'
    var_info = getvar(self, name)
    if var_info:
       _type = var_info['type'][-1]
    macr = self.tmpls.get(name, {})
    if type(macr) != Template: 
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
        'val': self.tmpls.get('Bool').render(val=_val)
    }
    elif _type == int: return {
        'type': 'int',
        'val': self.tmpls.get('Int').render(val=_val)
    }
    elif _type == float: return {
        'type': 'float',
        'val': self.tmpls.get('Float').render(
            val=_val,
            parts=math.modf(_val)
        )
    }
    elif _type == str: return {
        'type': 'str',
        'val': self.tmpls.get('Str').render(val=_val)
    }
