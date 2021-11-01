import ast
import _ast
import yaml
from jinja2 import Template
from . import templ_utils, types


def visitor(func):
    setattr(Transpiler, func.__name__, func)
    Transpiler.elements[func.__annotations__['tree']] = func
    return func

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

class _node():
    def __init__(self, env=None, tmp=None, parts=None, type=None, ctx=None):
        self.tmp = env.templates.get(tmp) if isinstance(tmp, str) else tmp
        self.parts = parts
        self.type = type
        self.ctx = ctx
        self.env = env
        self.val = ''

    def render(self):
        parts = self.parts
        if parts.get('own'):
            _type = self.env.variables[parts['own']]['type']
        else:
            _type = self.type
        for part in parts.values():
            if isinstance(part, _node):
                part.render()
            elif isinstance(part, list):
                for part_el in part:
                    part_el.render()
        if not self.tmp:
            return ''
        self.val = self.tmp.render(
            env=self.env,
            _type=types.type_render(self.env, _type),
            isinstance=isinstance,
            **types.types,
            is_const=templ_utils.is_const,
            **parts
        )
        return self.val

    def __str__(self):
        return self.val

    def __call__(self):
        return self.val

class Transpiler:
    templates = dict.fromkeys([
        'expr', 'assign', 'if', 'elif', 'else',
        'func', 'return', 'while', 'for', 'c_like_for',
        'break', 'continue', 'import', 'body',
        'name', 'Int', 'Float', 'Bool', 'Str',
        'bin_op', 'un_op', 'callfunc', 'attr',
        'callmethod', 'arg', 'list', 'tuple',
        'dict', 'index', 'slice', 'new_var', 'main',
        'global', 'nonlocal'
    ],'') | {'types': {}, 'operators': {}}
    elements = {}

    def __init__(self, templates):
        self.default_state()
        self.add_templ(templates)

    def use(self, name):
        self.used.add(name)
        return ''

    def default_state(self):
        self.strings = []
        self.used = set([])
        self.nl = 0
        self.namespace = 'main'
        self.variables = {
            'main.str': {'type': types.Type('str')},
            'main.int': {'type': types.Type('int')},
            'main.float': {'type': types.Type('float')},
        }
    def node(self, tmp=None, parts=None, type=None, ctx=None):
        return _node(
            env=self, tmp=tmp,
            parts=parts, type=type,
            ctx=ctx
        )

    def add_templ(self, templates):
        templates = yaml.load(
            templates.expandtabs(2),
            Loader=yaml.FullLoader
        )
        for name, template in templates.items():
            if self.templates.get(name) == '':
                templates[name] = Template(template)
            elif 'code' in template:
                templates[name]['code'] = Template(
                    template['code']
                )
        self.templates |= templates

    def visit(self, tree, **kw):
        node = self.elements.get(type(tree))(
            self, tree,
            **(kw or {})
        )
        node.ast = tree
        return node

    def generate(self, code, lang='py', mode='main'):
        if lang == 'py':
            astree = ast.parse(code)
        elif lang == 'hy':
            from hy.compiler import hy_compile, hy_parse
            astree = hy_compile(hy_parse(code), '__main__')
        elif lang == 'coco':
            from coconut.convenience import parse, setup
            setup(target='sys')
            astree = ast.parse(parse(code, 'block'))
        body = list(map(self.visit, astree.body))
        for block in body:
            self.strings.extend(block.render().split('\n'))
        if 'main' in self.templates and mode == 'main':
            code = self.templates.get('main').render(
                body=self.strings,
                env=self
            )
        else:
            code = '\n'.join(self.strings)
        if mode != 'block':
            self.default_state()
        return code
