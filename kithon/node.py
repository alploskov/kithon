import ast
from operator import (lt, le, eq, ne, ge, gt)
import _ast
from jinja2 import Template
from .types import types


class node:
    def __init__(self, env=None, tmp=None, name='unknown', parts=None, type=None, nl=1, own=None):
        if tmp in env.templates:
            self.name = tmp
            self.tmp = env.templates[tmp].get('tmp', '')
        else:
            self.name = name
            self.tmp = Template(tmp)
        self.parts = parts
        self.type = type
        self.env = env
        self.val = ''
        self.nl = nl
        self.ast = None
        self.parent = None
        self.own = own
        self.code_before = []
        self.prefix = '    '

    def render(self):
        _get_val = lambda el: el.render() if isinstance(el, node) else el
        if self.own and self.own in self.env.variables:
            _type = self.env.variables[self.own]['type']
        else:
            _type = self.type
        for _name, part in self.parts.items():
            if _name.endswith('_type'):
                part = str(part)
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
                types=types,
                isinstance=isinstance,
                **self.parts
            )
        if self.name in [
            'expr', 'assign', 'set_attr',
            'new_attr', 'assignment_by_key',
            'new_key', 'new_var', 'if',
            'elif', 'else', 'func',
            'return', 'while', 'for',
            'c_like_for', 'class', 'init',
            'method', 'attr', 'new'
        ] and self.code_before:
            before = _get_val(self.code_before[0]) + '\n'
            for part in self.code_before[1:]:
                before += self.prefix * self.nl
                before += _get_val(part) + '\n'
            self.val = before +  self.prefix * self.nl + self.val
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

    def inc_nl(self):
        self.nl += 1
        return ''

    def dec_nl(self):
        self.nl -= 1
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
