import ast
import _ast
import yaml
from jinja2 import Template
#from hy.compiler import hy_compile, hy_parse
from coconut.convenience import parse, setup
from . import templ_utils, types
from .types import type_render, Dict, List
import pprint


def visitor(func):
    setattr(transpiler, func.__name__, func)
    transpiler.elements[func.__annotations__['tree']] = func
    return func

def op_to_str(op):
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
    def __init__(
        self, env=None,
        tmp=None, parts=None,
        type=None, ctx=None,
        is_const=None 
    ):
        self.tmp = env.tmpls.get(tmp, '') \
            if isinstance(tmp, str) \
            else tmp
        self.parts = parts
        self.type = type
        self.ctx = ctx
        self.env = env
        self.val = ''

    def render(self):
        parts = self.parts
        for name, part in parts.items():
            if isinstance(part, _node):
                part.render()
            elif isinstance(part, list):
                [p.render() for p in part]
        if not self.tmp:
             return ''
        self.val = self.tmp.render(
            env=self.env,
            _type=type_render(self.env, self.type),
            isinstance=isinstance,
            **{'Dict': Dict, 'List': List},
            **parts
        )
        return self.val

    def __call__(self):
        return self.val


class transpiler:
    tmpls = dict.fromkeys([
        'expr', 'assign', 'if', 'elif', 'else',
        'func', 'return', 'while', 'for', 'c_like_for',
        'break', 'continue', 'import', 'body',
        'name', 'Int', 'Float', 'Bool', 'Str',
        'bin_op', 'un_op', 'callfunc', 'attr',
        'callmethod', 'arg', 'List', 'tuple',
        'dict', 'index', 'slice', 'new_var', 'main',
        'global', 'nonlocal'
    ],'') | {'types': {}, 'operators': {}} 
    elements = {}

    def __init__(self, *tmpls):
        self.default_state()
        for t in tmpls:
            self.add_templ(t)

    def use(self, name):
        self.used.add(name)
        return ''
    def default_state(self):
        self.strings = []
        self.used = set([])
        self.nl = 0
        self.namespace = 'main'
        self.variables = {
            'main.str': {'own': 'main.str', 'type': ['type']},
            'main.int': {'own': 'main.int', 'type': ['type']},
            'main.float': {'own': 'main.float', 'type': ['type']},
        }
    def node(self, tmp=None, parts=None, type=None, ctx=None):
        return _node(
            env=self, tmp=tmp,
            parts=parts, type=type,
            ctx=ctx
        )
        
    def add_templ(self, t):
        tmpls = yaml.load(
            t.expandtabs(2),
            Loader=yaml.FullLoader)
        for name, tmp in tmpls.items():
            if self.tmpls.get(name) == '':
                tmpls[name] = Template(tmp)
                tmpls[name].globals |= {
                    'is_const': templ_utils.is_const
                }
            elif 'code' in tmp:
                tmpls[name]['code'] = Template(tmp['code'])
        self.tmpls |= tmpls

    def visit(self, el, **kw):
        a = self.elements.get(type(el))(
            self, el,
            **(kw or {})
        )
        a.ast = el
        return a

    def generate(self, code, lang='py'):
        if lang == 'py':
            astree = ast.parse(code)
        elif lang == 'hy':
            astree = hy_compile(hy_parse(code), '__main__')
        elif lang == 'coco':
            setup(target='sys')
            astree = ast.parse(parse(code, 'block'))
        body = list(map(self.visit, astree.body))
        for i in body:
            self.strings.extend(i.render().split('\n'))
        if 'main' in self.tmpls:
            code = self.tmpls.get('main').render(
                body=self.strings,
                env=self)
        else:
            code = '\n'.join(self.strings)
        self.default_state()
        return code
