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
    def __init__(self, env=None, tmp=None, name=None, parts=None, type=None, nl=1, own=None):
        if (tmp or '').startswith('type.'):
            self.name = 'type'
            self.tmp = Template(tmp.removeprefix('type.'))
        elif tmp in env.templates:
            self.name = name or tmp
            self.tmp = env.templates[tmp].get('tmp', '')
        else:
            self.name = name or 'unknown'
            self.tmp = Template(tmp or '')
        self.parts = parts
        self.type = type or 'None'
        self.env = env
        self.val = ''
        self.nl = nl
        self.ast = None
        self.parent = None
        self.own = own
        self.code_before = []

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
                part.render()
            elif isinstance(part, list):
                for part_el in part:
                    if isinstance(part_el, node):
                        part_el.parent = self
                        part_el.render()
        if getattr(self, 'tmp', None):
            self.val = self.tmp.render(
                env=self.env,
                node=self,
                nl=self.nl,
                parent=self.parent,
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
            'method', 'attr'
        ] and self.code_before:
            before = _get_val(self.code_before[0]) + '\n'
            for part in self.code_before[1:]:
                before += '    ' * self.nl
                before += _get_val(part) + '\n'
            self.clear_code_before()
            self.val = before + '    ' * self.nl + self.val
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

    def clear_code_before(self):
        self.code_before = []
        return ''

    def __str__(self):
        return self.val

    def __call__(self):
        return self.render()

for op in (lt, le, eq, ne, ge, gt):
    def operation(op):
        def _(self, other):
            if self.get_val() != 'unknown':
                if isinstance(other, node) and other.get_val() != 'unknown':
                    return op(self.get_val(), other.get_val())
                return op(self.get_val(), other)
            return False
        return _
    setattr(node, f'__{op.__name__}__', operation(op))
