import ast
from operator import (lt, le, eq, ne, ge, gt)
import _ast
from jinja2 import Template
from .types import types


def type_to_node(env, _type):
    if isinstance(_type, (list, tuple)):
        return [type_to_node(env, t) for t in _type]
    type_name = getattr(_type, 'name', _type)
    tmp = env.templates['types'].get(type_name, type_name)
    if isinstance(_type, str):
        return env.node(tmp=f'type.{tmp}')
    return env.node(
        tmp=tmp,
        name='type',
        parts={
            f: type_to_node(env, getattr(_type, f))
            for f in _type.fields
        }
    )

class node:
    def __init__(self, env=None, tmp='', name=None, parts={}, type=None, own=None, code_before=None):
        if tmp.startswith('type.'):
            self.name = 'type'
            self.tmp = Template(tmp.removeprefix('type.'))
        elif tmp in env.templates:
            self.name = name or tmp
            self.tmp = env.templates[tmp].get('tmp', '')
        else:
            self.name = name or 'unknown'
            self.tmp = Template(tmp)
        self.parts = parts
        self.type = type or 'None'
        self.env = env
        self.val = ''
        self.nl = env.nl
        self.ctx = env.ctx[-1]
        self.ast = None
        self.parent = None
        self.part_name = ''
        self.own = own
        self.code_before = code_before or []

    def render(self):
        _get_val = lambda el: el.render() if isinstance(el, node) else el
        _type = self.env.variables.get(
            self.own, {}
        ).get('type', self.type)
        if self.name != 'type':
            type = type_to_node(self.env, _type)
            type.render()
        else:
            type = _type
        for _name, part in self.parts.items():
            if self.name != 'type' and _name.endswith('type'):
                self.parts[_name] = part = type_to_node(self.env, part)
            if isinstance(part, node):
                part.parent = self
                part.part_name = _name
                part.render()
            elif isinstance(part, list):
                for part_el in part:
                    if isinstance(part_el, node):
                        part_el.parent = self
                        part_el.part_name = _name
                        part_el.render()
        if getattr(self, 'tmp', None):
            self.val = self.tmp.render(
                env=self.env,
                node=self,
                nl=self.nl,
                parent=self.parent,
                part_name=self.part_name,
                _type=_type,
                type=type,
                types=types,
                isinstance=isinstance,
                **self.parts
            )
        if self.name in [
                'expr', 'assign', 'set_attr',
                'new_attr', 'assignment_by_key', 'new_var',
                'if', 'elif', 'else', 'func',
                'return', 'while', 'for',
                'c_like_for', 'class', 'init',
                'method', 'attr', 'var_prototype',
                'break', 'continue'
        ] and self.code_before:
            before = _get_val(self.code_before[0]) + '\n'
            for part in self.code_before[1:]:
                before += '    ' * self.nl
                before += _get_val(part) + '\n'
            self.val = before + '    ' * self.nl + self.val
            self.code_before = []
        elif self.parent:
            self.parent.code_before.extend(self.code_before)
        return self.val

    def is_const(self):
        return (
            isinstance(self.ast, _ast.Constant)
            or isinstance(self.ast, _ast.UnaryOp)
            and isinstance(self.ast.operand, _ast.Constant)
        )

    def get_val(self):
        if not self.is_const():
            return 'unknown'
        return ast.literal_eval(self.ast)

    def add_code_before(self, code):
        self.code_before.append(code)
        return ''

    def __str__(self):
        return self.val

    def __call__(self):
        return self.render()

    def __eq__(self, other):
        if isinstance(other, node):
            if self.is_const() and other.is_const():
                return self.get_val() == other.get_val()
            return self.parts == other.parts
        if self.is_const():
            return self.get_val() == other
        return False

    def __ne__(self, other):
        return not self == other

for op in (lt, le, ge, gt):
    def operation(op):
        def _(self, other):
            if self.is_const():
                if isinstance(other, node) and other.is_const():
                    return op(self.get_val(), other.get_val())
                return op(self.get_val(), other)
            return False
        return _
    setattr(node, f'__{op.__name__}__', operation(op))
