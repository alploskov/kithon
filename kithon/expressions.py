import ast
import math
import _ast
from .types import types, type_eval
from .core import visitor
from .side_effects import side_effect


def op_to_str(op):
    """Return a sign instead of ast"""
    return {
        _ast.Add: '+',     _ast.Sub: '-',
        _ast.Mult: '*',    _ast.Div: '/',
        _ast.Mod: '%',     _ast.Pow: '**',
        _ast.LShift: '<<', _ast.RShift: '>>',
        _ast.BitOr: '|',   _ast.BitXor: '^',
        _ast.BitAnd: '&',  _ast.FloorDiv: '//',
        _ast.Invert: '~',  _ast.Not: 'not',
        _ast.UAdd: '+',    _ast.USub: '-',
        _ast.Eq: '==',     _ast.NotEq: '!=',
        _ast.Lt: '<',      _ast.LtE: '<=',
        _ast.Gt: '>',      _ast.GtE: '>=',
        _ast.Is: 'is',     _ast.IsNot: 'is_not',
        _ast.In: 'in',     _ast.NotIn: 'not_in',
        _ast.And: 'and',   _ast.Or: 'or'
    }.get(type(op))

@visitor
def un_op(self, tree: _ast.UnaryOp):
    """Unary operations(not...)"""
    el = self.visit(tree.operand)
    op = op_to_str(tree.op)
    overload, _ = self.get_macro(
        _type=el.type,
        selector=op + '.{_}',
        is_reducing=True
    )
    side_effect(overload, {'op': op, 'el': el})
    return self.node(
        tmp=overload.get('code', 'un_op'),
        name='un_op',
        type=type_eval(
            overload.get('type'),
            {'op': op, 'el': el}
        ) or el.type,
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
    overload, _ = self.get_macro(
        _type=(left.type, right.type),
        selector='{_[0]}.' + op + '.{_[1]}',
        is_reducing=True
    )
    side_effect(overload, {'left': left, 'right': right})
    return self.node(
        tmp=overload.get('code', 'bin_op'),
        name='bin_op',
        type=type_eval(
            overload.get('type', 'any'),
            {'left': left, 'right': right}
        ),
        parts={
            'left': left,
            'right': right,
            'op': self.templates['operators'].get(op, op)
        }
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
def attribute(self, tree: _ast.Attribute):
    obj = self.visit(tree.value)
    own = f'{obj.own}.{tree.attr}'
    macro, own = self.get_macro(
        obj.own,
        obj.type,
        selector='{_}.' + tree.attr
    )
    side_effect(macro, {'obj': obj, 'attr': tree.attr})
    inf = self.variables.get(own, {})
    return self.node(
        tmp=macro.get('get', 'attr'),
        name='attr',
        type=inf.get('type') or type_eval(
            macro.get('type', 'None'),
            {'obj': obj, 'attr': tree.attr}
        ),
        own=own,
        parts={
            'obj': obj,
            'attr': macro.get('alt_name', tree.attr),
            'attr_inf': inf
        }
    )

@visitor
def call(self, tree: _ast.Call):
    func = self.visit(tree.func)
    args = list(map(self.visit, tree.args))
    kwargs = list(map(self.visit, tree.keywords))
    tmp = 'call'
    ret_type = getattr(func.type, 'ret_type', 'None')
    macro, _ = self.get_macro(func.own, func.type)
    if func.type == 'type':
        tmp = 'new'
        ret_type = func.own
    parts = {
        'func': func,
        'args': args,
        'kwargs': kwargs,
        'obj': func.parts.get('obj')
    } | match_args(macro, args, kwargs)
    side_effect(macro, parts)
    return self.node(
        tmp=macro.get('code', tmp),
        name=tmp,
        type=type_eval(
            macro.get('ret_type'), parts
        ) or ret_type,
        parts=parts
    )

@visitor
def _list(self, tree: _ast.List):
    elements = list(map(self.visit, tree.elts))
    return self.node(
        tmp='list',
        type=types['list'](
            elements[0].type if len(elements)
            else 'any'
        ),
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
        tmp='tuple',
        type=types['tuple'](el_type, els_types),
        parts={'ls': elements}
    )

@visitor
def _dict(self, tree: _ast.Dict):
    keys = list(map(self.visit, tree.keys))
    values = list(map(self.visit, tree.values))
    return self.node(
        tmp='dict',
        type=types['dict'](
            keys[0].type if len(keys) else 'any',
            values[0].type if len(values) else 'any'
        ),
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
        macro, _ = self.get_macro(
            obj.own,
            obj.type,
            selector='{_}.__getitem__'
        )
        parts = {'obj': obj, 'key': self.visit(_slice), 'ctx': ctx}
        return self.node(
            tmp=macro.get('code', 'index'),
            type=(
                type_eval(macro.get('ret_type'), parts)
                or getattr(obj.type, 'el_type', 'any')
            ),
            own=f'{obj.own}.[]',
            parts=parts
        )
    return self.node(
        tmp='slice',
        type=obj.type,
        own=f'{obj.own}.[]',
        parts={
            'obj': obj,
            'ctx': ctx,
            'low': self.visit(
                _slice.lower
                or ast.Constant(value=0)
            ),
            'up': self.visit(
                _slice.upper
                or ast.Call(
                    func=ast.Name(id='len', ctx=_ast.Load),
                    args=[tree.value],
                    keywords=[])
            ),
            'step': self.visit(
                _slice.step
                or ast.Constant(value=1)
            )
        }
    )

@visitor
def ternary(self, tree: _ast.IfExp):
    cond = self.visit(tree.test)
    body = self.visit(tree.body)
    els = self.visit(tree.orelse)
    if not self.templates['ternary']['tmp']:
        var_name = self.get_temp_var('ifepx')
        exp = self.node(
            tmp='name',
            name='ternary',
            type=body.type,
            parts={'name': var_name, 'ctx': _ast.Load}
        )
        exp.add_code_before(self.var_prototype(var_name))
        _assign = lambda val: ast.Assign(
            targets=[ast.Name(id=var_name, ctx=ast.Store())],
            value=val
        )
        exp.add_code_before(
            self.node(
                tmp='if',
                parts={
                    'condition': cond,
                    'body': self.expression_block([_assign(tree.body)]),
                    'els': self._else([_assign(tree.orelse)])
                }
            )
        )
        return exp
    return self.node(
        tmp='ternary',
        type=body.type,
        parts={
            'condition': cond,
            'body': body,
            'els': els
        }
    )

@visitor
def name(self, tree: _ast.Name):
    ctx = {
        _ast.Store: 'store',
        _ast.Load: 'load'
    }.get(type(tree.ctx))
    ns = (self.namespace + '.').split('.')
    for ln in range(len(ns)):
        var_info = self.variables.get(
            f'{".".join(ns[:-(ln + 1)])}.{tree.id}', {}
        )
        if var_info: break
    var_info = (
        {'own': f'{self.namespace}.{tree.id}'}
        | var_info
    )
    macro = {}
    if tree.id in self.templates:
        macro, var_info['own'] = self.get_macro(tree.id)
    else:
        macro, var_info['own'] = self.get_macro(var_info.get('own'))
    return self.node(
        tmp='name',
        type=var_info.get(
            'type',
            type_eval(
                macro.get('type', 'None'),
                {'name': tree.id, 'ctx': ctx}
            )
        ),
        own=var_info.get('own'),
        parts={
            'name': macro.get('alt_name', tree.id),
            'ctx': ctx
        }
    )

@visitor
def const(self, tree: _ast.Constant):
    _val = tree.value
    if _val is None:
        return none(self, tree)
    _type = str(type(_val))[8:-2]
    parts={'val': _val}
    if isinstance(_val, float):
        parts |= {'parts': math.modf(_val)}
    return self.node(
        tmp=_type,
        type=_type,
        parts=parts
    )

@visitor
def none(self, tree: type(None)):
    return self.node(
        tmp='None',
        type='None'
    )
