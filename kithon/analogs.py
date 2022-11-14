"""
Code generators for some python constructions
"""
import ast
from jinja2 import Template


def name(self, name, ctx='load'):
    return self.visit(ast.Name(
        id=name,
        ctx={
            'load': ast.Load(),
            'store': ast.Store()
        }.get(ctx)
    ))

def call(self, func_name, args=[], kwargs=[]):
    return self.visit(ast.Call(
        func=(
            func_name if not isinstance(func_name, str)
            else name(self, func_name)
        ),
        args=args, keywords=kwargs
    ))

def assign(self, var_name, value):
    return self.visit(ast.Assign(
        targets=[name(self, var_name, ctx='store')],
        value=value
    ))

def ternary(self, cond, body, els):
    var_name = self.get_temp_var('ifepx')
    exp = name(self, var_name)
    exp.code_before = [
        self.var_prototype(var_name, type=body.type),
        self.node(
            tmp='if',
            parts={
                'condition': cond,
                'body': self.expression_block([
                    assign(self, var_name, body)
                ]),
                'els': self._else([
                    assign(self, var_name, els)
                ]),
            }
        )
    ]
    return exp

def slice(self, obj, low, up, step):
    slice_name = self.get_temp_var('slice')
    exp = name(self, slice_name)
    exp.code_before += [
        self.var_prototype(slice_name, type=obj.type),
        self.visit(ast.For(
            iter=call(self, 'range', args=[low, up, step]),
            target=name(self, 'i', ctx='store'),
            body=[ast.Expr(value=call(
                self,
                ast.Attribute(
                    value=name(self, slice_name),
                    attr='append', ctx=ast.Load()
                ),
                args=[self.index(
                    obj=obj,
                    key=name(self, 'i'),
                    ctx='load'
                )],
            ))],
            orelse=[]
        ))
    ]
    return exp

def index(self, obj, _index):
    invert = lambda: self.visit(ast.BinOp(
        left=call(self, 'len', [obj]),
        op=ast.Add(),
        right=_index
    ))
    if _index >= 0:
        return _index
    if _index < 0:
        return invert()
    _index.type = 'int'
    return self.visit(ast.IfExp(
        test=ast.BinOp(left=_index, op=ast.GtE(), right=0),
        body=_index,
        orelse=invert()
    ))

def keyword(self, kw):
    if kw not in self.templates['meta']['keywords']:
        return kw
    return Template(self.templates['meta']['keyword_tmp']).render(
        keyword=kw
    )

def loop_else(self, loop):
    if not self.ctx[-1].els:
        return loop
    var_name = f"{self.ctx[-1].name}_broken"
    loop.parts['els'] = self.node(
        tmp='if',
        parts={
            'condition': self.visit(ast.UnaryOp(
                op=ast.Not(),
                operand=name(self, var_name)
            )),
            'body': loop.parts['els'],
            'els': '',
        },
    )
    return loop
