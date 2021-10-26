import _ast


def is_const(node):
    ast = node.ast
    return isinstance(ast, _ast.Constant) or\
        isinstance(ast, _ast.UnaryOp) and\
        isinstance(ast.operand, _ast.Constant)

def tmin(node1, node2):
    type1 = node1.type
    type2 = node2.type
    if is_const(type1) and is_const(type2):
        val1 = node1.ast.value
        val2 = node2.ast.value
        return (node1() if val1 > val2 else node2())
    elif is_const(node1) and type2 == 'uint':
        val1 = node1.ast.value
        return (node2() if val1 < 0 else 'unknown')
    elif is_const(node2) and type1 == 'uint':
        val2 = node2.ast.value
        return (node1() if val2 < 0 else 'unknown')
    return 'unknown'
