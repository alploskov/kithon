import ast
from .core import visitor, is_hy_supported
from .blocks import expression_block, _else


if is_hy_supported:
    from hy.models import Expression
    from hy.compiler import hy_compile, mkexpr
    @visitor
    def hy_expr(self, tree: Expression):
        if str(tree[0]) in contorols:
            return contorols[str(tree[0])](self, tree[1:])
        return self.visit(get_ast(tree))

def unless(self, tree):
    cond, body, *els = tree
    if 'unless' in self.templates:
        return self.node(
            tmp='unless',
            parts={
                'condition': self.visit(get_ast(cond).value),
                'body': expression_block(self, [body]),
                'els': _else(self, els)
            }
        )
    cond = invert_cond(cond)
    return self.visit(ast.If(
        test=get_ast(cond).value,
        body=[body],
        orelse=els
    ))

def until(self, tree):
    cond, body = tree
    if 'until' in self.templates:
        return self.node(
            tmp='until',
            parts={
                'condition': self.visit(get_ast(cond).value),
                'body': expression_block(self, [body]),
            }
        )
    cond = invert_cond(cond)
    return self.visit(ast.While(
        test=get_ast(cond).value,
        body=[body],
    ))

def do_while(self, tree):
    cond, body = tree
    if 'do_while' in self.templates:
        return self.node(
            tmp='do_while',
            parts={
                'condition': self.visit(get_ast(cond).value),
                'body': expression_block(self, [body]),
            }
        )
    _node = self.visit(ast.While(
        test=get_ast(cond).value,
        body=[body],
    ))
    _node.code_before += list(map(self.visit, [body]))
    return _node

def loop(self, tree):
    if 'loop' in self.templates:
        return self.node(
            tmp='loop',
            parts={
                'body': expression_block(self, tree),
            }
        )
    return self.visit(ast.While(
        test=ast.Constant(value=True),
        body=tree
    ))


def invert_cond(cond):
    invert_sign = {
        '==': '!=',     '!=': '==',
        '<': '>=',      '>=': '<',
        '>': '<=',      '<=': '>',
        'in': 'not_in', 'not_in': 'in'
    }
    if str(cond[0]) in invert_sign:
        return mkexpr(invert_sign[str(cond[0])]) + cond[1:]
    if str(cond[0]) == 'not':
        return cond[1:]
    return mkexpr('not', cond)

def get_ast(hy_obj):
    return hy_compile(
        hy_obj,
        '__main__',
        import_stdlib=False
    ).body[0]

contorols = {
    'unless':   unless,
    'until':    until,
    'do-while': do_while,
    'do_while': do_while,
    'loop':     loop,
}
