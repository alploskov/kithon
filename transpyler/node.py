import ast
import _ast
from jinja2 import Template
from . import types


class _node:
    def __init__(self, env=None, tmp=None, parts={}, type=None, ctx=None, nl=1, own=None):
        if tmp in env.templates:
            self.name = tmp
            self.tmp = env.templates.get(tmp)
        else:
            self.name = 'unknown'
            if isinstance(tmp, str):
                self.tmp = Template(tmp)
            else:
                self.tmp = tmp
        self.parts = parts
        self.type = type
        self.ctx = ctx
        self.env = env
        self.val = ''
        self.nl = nl
        self.ast = None
        self.parent = None
        self.own = own
        self.code_before = []
        self.prefix = '    '

    def render(self):
        _get_val = lambda el: el.render() if isinstance(el, _node) else el
        if self.own and self.own in self.env.variables:
            _type = self.env.variables[self.own]['type']
        else:
            _type = self.type
        for part in self.parts.values():
            if isinstance(part, _node):
                part.parent = self
                part.render()
            elif isinstance(part, list):
                for part_el in part:
                    if isinstance(part_el, _node):
                        part_el.parent = self
                        part_el.render()
        if self.tmp:
            self.val = self.tmp.render(
                env=self.env,
                node=self,
                nl=self.nl,
                parent=self.parent,
                _type=types.type_render(self.env, _type),
                isinstance=isinstance,
                **types.types,
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
        ]:
            if self.code_before:
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

    def del_code_before(self):
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

    def __gt__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() > other.get_val()
            return self.get_val() > other
        return False

    def __ge__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() >= other.get_val()
            return self.get_val() >= other
        return False

    def __le__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() <= other.get_val()
            return self.get_val() <= other
        return False

    def __lt__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() < other.get_val()
            return self.get_val() < other
        return False

    def __eq__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() == other.get_val()
            return self.get_val() == other
        return False

    def __nq__(self, other):
        if self.get_val() != 'unknown':
            if isinstance(other, _node) and other.get_val() != 'unknown':
                return self.get_val() != other.get_val()
            return self.get_val() != other
        return False
