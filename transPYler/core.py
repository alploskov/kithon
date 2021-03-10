import ast
import _ast


elements = {}
handlers = {}
objects = {}
op_to_str = {_ast.Add: '+',
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
             _ast.Not: 'not ',
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
             }

def parser(el):
    el_f = elements.get(type(el))
    if el_f:
        return el_f(el)

namespace = "main"
variables = {"main": {}}

def compiler(code):
    strings = []
    body = ast.parse(code).body
    for i in body:
        i = parser(i)
        if i:
            strings.append(i)
    return '\n'.join(strings)
