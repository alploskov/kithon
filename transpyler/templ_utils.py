import ast
import _ast


def is_const(node):
    tree = node.ast
    return (
        isinstance(tree, _ast.Constant)
        or isinstance(tree, _ast.UnaryOp)
        and isinstance(tree.operand, _ast.Constant)
    )

def get_val(node):
    if not is_const(node):
        return 'unknown'
    return ast.literal_eval(node.ast)

class cmp:
    def __init__(self, first, second):
        if not(is_const(first) and is_const(second)):
            self.max = 'unknown'
            self.min = 'unknown'
            return
        self.max = max(get_val(first), get_val(second))
        self.min = min(get_val(first), get_val(second))

utils = {'cmp': cmp, 'get_val': get_val, 'is_const': is_const}
