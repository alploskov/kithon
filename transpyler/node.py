import ast
import _ast
from . import templ_utils, types


class _node():
    def __init__(self, env=None, tmp=None, parts={}, type=None, ctx=None, nl=1, own=None, obj=None):
        if isinstance(tmp, str):
            self.name = tmp
            self.tmp = env.templates.get(tmp)
        else:
            self.name = 'unknown'
            self.tmp = tmp
        self.parts = parts
        self.type = type
        self.ctx = ctx
        self.env = env
        self.val = ''
        self.nl = nl
        self.parent = None
        self.own = own
        self.obj = obj

    def render(self):
        parts = self.parts
        if parts.get('own'):
            _type = self.env.variables[parts['own']]['type']
        else:
            _type = self.type
        for part in parts.values():
            if isinstance(part, _node):
                part.parent = self
                part.render()
            elif isinstance(part, list):
                for part_el in part:
                    if not isinstance(part_el, (str, tuple)):
                        part_el.parent = self
                        part_el.render()
        if not self.tmp:
            return ''
        self.val = self.tmp.render(
            env=self.env,
            nl=self.nl,
            parent=self.parent,
            _type=types.type_render(self.env, _type),
            isinstance=isinstance,
            **types.types,
            **templ_utils.utils,
            **parts
        )
        return self.val

    def is_const(node):
        tree = node.ast
        return (
            isinstance(tree, _ast.Constant)
            or isinstance(tree, _ast.UnaryOp) and isinstance(tree.operand, _ast.Constant)
        )

    def get_val(self):
        if not self.is_const():
            return 'unknown'
        return ast.literal_eval(self.ast)

    def __str__(self):
        return self.val

    def __call__(self):
        return self.val

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
    
