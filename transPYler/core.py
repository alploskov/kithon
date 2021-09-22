import ast
import _ast
from dataclasses import dataclass
import re

import yaml
from jinja2 import Template
from hy.compiler import hy_compile, hy_parse
from coconut.convenience import parse, setup

from . import blocks, expressions, utils


class transpiler:
    tmpls = {
        'types': {},
        'operations': {}
    }

    nl = 0
    namespace = 'main'
    variables = {
        'main.str': 'type',
        'main.int': 'type',
        'main.float': 'type',
    }
    used = set([])
    def use(self, name):
        self.used.add(name)
        return ''
    elements = {
        _ast.Assign: blocks.assign,
        _ast.AnnAssign: blocks.ann_assign,
        _ast.Expr: blocks.expr,
        _ast.AugAssign: blocks.aug_assign,
        _ast.If: blocks._if,
        _ast.While: blocks._while,
        _ast.For: blocks._for,
        _ast.FunctionDef: blocks.define_function,
        _ast.Return: blocks.ret,
        _ast.Global: blocks._global,
        _ast.Nonlocal: blocks._nonlocal,
        _ast.Break: blocks._break,
        _ast.Continue: blocks._continue,

        _ast.Call: expressions.function_call,
        _ast.BinOp: expressions.math_op,
        _ast.BoolOp: expressions.bool_op,
        _ast.Compare: expressions.compare,
        _ast.List: expressions._list,
        _ast.Attribute: expressions.attribute,
        _ast.Name: expressions.name,
        _ast.Subscript: expressions.slice,
        _ast.Constant: expressions.const,
        _ast.arg: expressions.arg,
        _ast.UnaryOp: expressions.un_op,
        _ast.Dict: expressions._dict,
        type(None): lambda self, t: {
            'type': 'None',
            'val': ''
        }
    }

    def add_templ(self, t):
        tmpls = yaml.load(t.read(), Loader=yaml.FullLoader)
        for i in tmpls:
            if i in [
                'expr', 'assign', 'if', 'elif', 'else',
                'func', 'return', 'while', 'for', 'c_like_for',
                'break', 'continue', 'import', 'body',
                'name', 'Int', 'Float', 'Bool', 'Str',
                'bin_op', 'un_op', 'callfunc', 'getattr',
                'callmethod', 'arg', 'list', 'tuple',
                'dict', 'index', 'slice', 'new_var', 'main' 
            ]:
                tmpls[i] = Template(tmpls.get(i))
                tmpls[i].globals |= {
                    'type': utils.transpyler_type,
                    'is_const': (lambda n: type(n.ast) == _ast.Constant)
                }
        self.tmpls |= tmpls

    def __init__(self, t):
        for i in t:
            self.add_templ(i)

    def op_to_str(self, op):
        return {
            _ast.Add: '+',
            _ast.Sub: '-',
            _ast.Mult: '*',
            _ast.Div: '/',
            _ast.Mod: '%',
            _ast.Pow: '**',
            _ast.LShift: '<<',
            _ast.RShift: '>>',
            _ast.BitOr: '|',
            _ast.BitXor: '^',
            _ast.BitAnd: '&',
            _ast.FloorDiv: '//',
            _ast.Invert: '~',
            _ast.Not: 'not',
            _ast.UAdd: '+',
            _ast.USub: '-',
            _ast.Eq: '==',
            _ast.NotEq: '!=',
            _ast.Lt: '<',
            _ast.LtE: '<=',
            _ast.Gt: '>',
            _ast.GtE: '>=',
            _ast.Is: 'is',
            _ast.IsNot: 'is not',
            _ast.In: 'in',
            _ast.NotIn: 'not in',
            _ast.And: 'and',
            _ast.Or: 'or'
        }.get(type(op))

    @dataclass
    class node():
        val: str = ''
        type: str = ''
        ast: any = None
        def __call__(self):
            return self.val

    def visit(self, el, **kw):
        el_f = self.elements.get(type(el))
        c = el_f(self, el, **(kw or {}))
        if type(c) == str:
            return c
        return self.node(**c, ast=el)

    strings = []

    def generate(self, code, lang='py'):
        if lang == 'py':
            astree = ast.parse(code)
        elif lang == 'hy':
            astree = hy_compile(hy_parse(code), '__main__')
        elif lang == 'coco':
            setup(target="sys")
            astree = ast.parse(parse(code, 'block'))
        body = astree.body
        for i in body:
            i = self.visit(i)
            if '\n' in i:
                self.strings.extend(i.split('\n'))
            else:
                self.strings.append(i)
        if 'main' in self.tmpls:
            code = self.tmpls.get('main').render(
                body=self.strings,
                ctx=self)
        else:
            code = '\n'.join(self.strings)
        self.strings = []
        return {
            'recomend': self.tmpls.get('rec', ''),
            'code': code
        }
