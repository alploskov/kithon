import _ast


def is_const(node):
    ast = node.ast
    return (
        isinstance(ast, _ast.Constant)
        or isinstance(ast, _ast.UnaryOp)
        and isinstance(ast.operand, _ast.Constant)
    )
