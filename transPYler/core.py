import ast
import _ast
from dataclasses import dataclass
from . import blocks, expressions, utils
import re
import yaml
from jinja2 import Template, Environment, DictLoader


class transpiler:
    tmpls = {
        'types': {},
        'operations': {}
    }

    nl = 0
    namespace = 'main'
    variables = {'main': {
        'str': 'type',
        'int': 'type',
        'float': 'type',
    }}

    macros = {}
    objects = {}

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
        _ast.Global: blocks.scope_of_view,
        _ast.Nonlocal: blocks.scope_of_view,
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
        type(None): lambda t: {
            'type': 'None',
            'val': ''
        }
    }

    def add_templ(self, t):
        tmpls = yaml.load(open(t, 'r').read())
        for i in tmpls:
            if i not in ['operations', 'types']:
                tmpls[i] = Template(tmpls.get(i))
                tmpls[i].globals |= {
                    'type': utils.transpyler_type,
                }
        self.tmpls |= tmpls

    def add_macros(self, m):
        self.macros |= yaml.load(open(m, 'r').read())
        if 'classes' in self.macros:
            self.objects |= self.macros.get('classes')

    def __init__(self, t, m):
        for i in t:
            self.add_templ(i)
        for i in m:
            self.add_macros(i)

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

    def parser(self, el):
        el_f = self.elements.get(type(el))
        comp = el_f(self, el)
        if type(comp) == str:
            return comp
        return self.node(**comp, ast=el)

    def compiler(self, code):
        strings = []
        body = ast.parse(code).body
        for i in body:
            i = self.parser(i)
            if '\n' in i:
                strings.extend(i.split('\n'))
            else:
                strings.append(i)
        if 'main' not in self.tmpls:
            return '\n'.join(strings)
        return self.tmpls.get('main').render(body=strings)
