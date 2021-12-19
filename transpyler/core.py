import ast
import _ast
import yaml
from jinja2 import Template
from . import types, node


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

class Transpiler:
    elements = {}

    def __init__(self, templates):
        self.templates = dict.fromkeys([
            'expr', 'assign', 'if', 'elif', 'else',
            'func', 'return', 'while', 'for', 'c_like_for',
            'break', 'continue', 'import', 'body',
            'name', 'Int', 'Float', 'Bool', 'Str',
            'bin_op', 'un_op', 'callfunc', 'getattr',
            'callmethod', 'arg', 'List', 'Tuple',
            'Dict', 'index', 'slice', 'new_var', 'Main',
            'global', 'nonlocal', 'assignment_by_key',
            'class', 'init', 'attr', 'method', 'new',
            'set_attr', 'new_attr', 'new_key'
        ], '') | {'types': {}, 'operators': {}}
        self.default_state()
        self.add_templ(templates)

    def use(self, name):
        self.used.add(name)
        return ''

    def default_state(self):
        self.strings = []
        self.used = set([])
        self.nl = 0
        self.namespace = '__main__'
        self.variables = {
            '__main__': {'type': types.Module('__main__')},
            '__main__.str': {'type': types.Type('str')},
            '__main__.int': {'type': types.Type('int')},
            '__main__.float': {'type': types.Type('float')},
        }
    def node(self, tmp=None, parts={}, type=None, ctx=None, own=None, obj=None):
        return node._node(
            env=self, tmp=tmp,
            parts=parts, type=type,
            ctx=ctx, nl=self.nl,
            own=own, obj=obj
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
        if type(tree) not in self.elements:
            return self.node()
        node = self.elements.get(type(tree))(
            self, tree,
            **(kw or {})
        )
        node.ast = tree
        return node

    def generate(self, code, lang='py', mode='Main'):
        
        if lang == 'py':
            astree = ast.parse(code)
        elif lang == 'hy':
            from hy.compiler import hy_compile, hy_parse
            astree = hy_compile(hy_parse(code), '__main__')
        elif lang == 'coco':
            from coconut.convenience import parse, setup
            setup(target='sys')
            astree = ast.parse(parse(code, 'block'))
        body = []
        body = list(map(self.visit, astree.body))
        for block in body:
            if not block:
                continue
            self.strings.extend(block.render().split('\n'))
        if isinstance(self.templates['Main'], Template) and mode == 'Main':
            code = self.templates.get('Main').render(
                _body=self.strings,
                body='\n'.join(self.strings),
                env=self
            )
        else:
            code = '\n'.join(self.strings)
        if mode != 'block':
            self.default_state()
        return code
