import ast
import math
from itertools import product
import _ast
from . import types
from .core import visitor, op_to_str
from .side_effects import side_effect


@visitor
def un_op(self, tree: _ast.UnaryOp):
    """Unary operations(not...)"""
    el = self.visit(tree.operand)
    _type = el_type = el.type
    tmp = 'un_op'
    op = op_to_str(tree.op)
    overload = self.templates.get(f'{op}.{_type}')
    while el_type != 'any' and not overload:
        el_type = types.to_any(el_type)
        overload = self.templates.get(f'{op}.{el_type}')
    if overload:
        tmp = overload.get('code', tmp)
        _type = types.type_eval(
            overload,
            {'op': op, 'el': el}
        )
        side_effect(overload, {'op': op, 'el': el})
    return self.node(
        tmp=tmp,
        type=_type,
        parts={
            'op': self.templates['operators'].get(
                f'un{op}',
                self.templates['operators'].get(op, op)
            ),
            'el': el
        }
    )

@visitor
def bin_op(self, tree: _ast.BinOp):
    """Math operation(+, -, *, /...)"""
    return _bin_op(
        self,
        self.visit(tree.left),
        self.visit(tree.right),
        op_to_str(tree.op)
    )

@visitor
def bool_op(self, tree: _ast.BoolOp):
    """Boolean logic operation(or, and)"""
    els = list(map(self.visit, tree.values))
    op = op_to_str(tree.op)
    expr = _bin_op(self, els[0], els[1], op)
    for el in els[2:]:
        expr = _bin_op(self, expr, el, op)
    return expr

@visitor
def compare(self, tree: _ast.Compare):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = self.visit(tree.left)
    els = list(map(self.visit, tree.comparators))
    ops = list(map(op_to_str, tree.ops))
    expr = _bin_op(self, f_el, els[0], ops[0])
    for l, r, op in zip(els[:-1], els[1:], ops[1:]):
        expr = _bin_op(self, expr, _bin_op(self, l, r, op), 'and')
    return expr

def _bin_op(self, left, right, op):
    tmp = 'bin_op'
    left_t = left.type
    right_t = right.type
    left_possible_types = [str(left_t)]
    right_possible_types = [str(right_t)]
    _type = 'None'
    while left_t != 'any':
        left_t = types.to_any(left_t)
        left_possible_types.append(str(left_t))
    while right_t != 'any':
        right_t = types.to_any(right_t)
        right_possible_types.append(str(right_t))
    possible_type_pairs = product(
        left_possible_types,
        right_possible_types
    )
    for left_t, right_t in possible_type_pairs:
        overload = self.templates.get(
            f'{left_t}.{op}.{right_t}'
        )
        if overload:
            tmp = overload.get('code', tmp)
            side_effect(
                overload,
                {'left': left, 'right': right}
            )
            _type = types.type_eval(
                overload.get('type', 'None'),
                {'left': left, 'right': right}
            )
            break
    return self.node(
        parts={
            'left': left,
            'right': right,
            'op': self.templates['operators'].get(op, op)
        },
        tmp=tmp,
        type=_type
    )

def match_args(macro, args, kwargs):
    """
    Match args names with their values
    """
    if 'args' not in macro:
        return {}
    return dict(list(zip(macro['args'], args)))

@visitor
def kwarg(self, tree: _ast.keyword):
    value = self.visit(tree.value)
    return self.node(
        tmp='kwarg',
        type=value.type,
        parts={'name': tree.arg, 'value': value}
    )

@visitor
def attribute(self, tree: _ast.Attribute, args=None, kwargs=None, call=False):
    tmp = 'callmethod' if call else 'getattr'
    obj = self.visit(tree.value)
    attr = tree.attr
    macro = ''
    parts = {'obj': obj, 'attr': attr, 'args': args, 'kwargs': kwargs}
    _type = 'None'
    if isinstance(obj.type, types.Module):
        module_name = obj.type.name.split('.')
        module = self.templates[module_name[0]]
        for part in module_name[1:]:
            module = module[part]
        macro = module.get(attr)
    elif isinstance(obj.type, str) and obj.type in self.variables:
        _type = self.variables[f'{obj.type}.{attr}']['type']
        if call:
            _type = _type.ret_type
    if not macro:
        obj_type = obj.type
        macro = self.templates.get(f'{obj_type}.{attr}')
        while obj_type != 'any' and not macro:
            obj_type = types.to_any(obj_type)
            macro = self.templates.get(f'{obj_type}.{attr}')
    if macro:
        parts['attr'] = macro.get('alt_name', attr)
        tmp = macro.get('code', tmp)
        parts.update(match_args(macro, args, kwargs))
        side_effect(macro, parts)
        _type = types.type_eval(
            macro.get('ret_type' if call else 'type', _type),
            parts
        )
        if _type == 'module':
            _type = types.Module(f'{obj.type.name}.{attr}')
    return self.node(
        own=f'{obj.own}.{attr}',
        type=_type,
        tmp=tmp,
        parts=parts
    )

@visitor
def function_call(self, tree: _ast.Call):
    args = list(map(self.visit, tree.args))
    kwargs = list(map(self.visit, tree.keywords))
    if isinstance(tree.func, _ast.Attribute):
        return self.attribute(tree.func, args=args, kwargs=kwargs, call=True)
    func = self.visit(tree.func)
    ret_type = getattr(func.type, 'ret_type', 'None')
    tmp = 'callfunc'
    parts = {'func': func, 'args': args, 'kwargs': kwargs}
    macro = None
    if (isinstance(tree.func, _ast.Name)
        and tree.func.id in self.templates):
        macro = self.templates.get(tree.func.id)
    elif func.type == 'class':
        tmp = 'new'
        ret_type = func.own
    elif str(func.type) in self.templates:
        macro = self.templates.get(str(func.type))
    if macro:
        parts.update(match_args(macro, args, kwargs))
        tmp = macro.get('code', 'callfunc')
        side_effect(macro, parts)
        ret_type = types.type_eval(
            macro.get('ret_type', 'None'),
            parts
        )
    return self.node(
        tmp=tmp,
        type=ret_type,
        parts=parts
    )

@visitor
def _list(self, tree: _ast.List):
    elements = list(map(self.visit, tree.elts))
    if len(elements) > 0:
        el_type = elements[0].type
    else:
        el_type = 'generic'
    return self.node(
        tmp='List',
        type=types.List(el_type),
        parts={'ls': elements}
    )

@visitor
def _tuple(self, tree: _ast.Tuple):
    elements = list(map(self.visit, tree.elts))
    # Used if we can find out which element we are taking
    els_types = tuple(e.type for e in elements)
    # Used in other cases
    el_type = tuple(set(els_types))
    return self.node(
        tmp='Tuple',
        type=types.Tuple(el_type, els_types),
        parts={'ls': elements}
    )

@visitor
def _dict(self, tree: _ast.Dict):
    keys = list(map(self.visit, tree.keys))
    values = list(map(self.visit, tree.values))
    if len(keys):
        el_type = values[0].type
        key_type = keys[0].type
    else:
        el_type = 'generic'
        key_type = 'generic'
    return self.node(
        tmp='Dict',
        type=types.Dict(key_type, el_type),
        parts={
            'keys': keys,
            'values': values,
            'keys_val': list(zip(keys, values))
        }
    )

@visitor
def slice(self, tree: _ast.Subscript):
    obj = self.visit(tree.value)
    _slice = tree.slice
    ctx = {
        _ast.Store: 'store',
        _ast.Load: 'load'
    }.get(type(tree.ctx))
    if not isinstance(_slice, _ast.Slice):
        return self.node(
            type=getattr(obj.type, 'el_type', 'None'),
            tmp='index',
            own=obj.own,
            parts={'obj': obj, 'key': self.visit(_slice), 'ctx': ctx}
        )
    return self.node(
        tmp = 'slice',
        type = obj.type,
        own=obj.own,
        parts = {
            'obj': obj,
            'ctx': ctx,
            'low': self.visit(
                _slice.lower or ast.Constant(value=0)
            ),
            'up': self.visit(
                _slice.upper or ast.Call(
                    func=ast.Name(id='len', ctx=_ast.Load),
                    args=[tree.value],
                    keywords=[]
            )),
            'step': self.visit(
                _slice.step or ast.Constant(value=1)
            )
        }
    )

@visitor
def name(self, tree: _ast.Name):
    _name = tree.id
    if _name.startswith('x_'):
        _name = _name[2:]
    _type = 'None'
    ctx = {
        _ast.Store: 'store',
        _ast.Load: 'load'
    }.get(type(tree.ctx))
    if _name == 'self':
        tmp = self.templates.get('self', 'name')
        var_info = self.variables[self.get_ctx()]
    else:
        var_info = self.getvar(_name)
    if var_info:
        _type = var_info['type']
    elif _name in self.templates:
        macro = self.templates[_name]
        _type = macro.get('type', _type)
        if _type == 'module':
            _type = types.Module(_name)
        _name = macro.get('alt_name', _name)
    return self.node(
        type=_type,
        tmp='name',
        own=var_info.get('own'),
        parts={
            'name': _name,
            'ctx': ctx
        }
    )

@visitor
def const(self, tree: _ast.Constant):
    _val = tree.value
    if isinstance(_val, type(None)):
        return none(self, tree)
    _type = str(type(_val))[8:-2]
    parts={'val': _val}
    if isinstance(_val, float):
        parts |= {'parts': math.modf(_val)}
    return self.node(
        type=_type,
        tmp=_type.capitalize(),
        parts=parts
    )

@visitor
def none(self, tree: type(None)):
    return self.node(
        tmp='None',
        type='None'
    )
