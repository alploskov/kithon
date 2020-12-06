import ast
from transPYler import expressions, blocks

def dentification_signs(signs):
    finished = {}
    for i in signs:
        sign_type = type(ast.parse(f"a{i}b").body[0].value.op)
        finished.update({sign_type: signs.get(i)})
    return finished


def conf(b_handlers, e_handlers, signs, a_attr, a_func):
    expressions.expr_handlers = e_handlers
    expressions.signs = dentification_signs(signs)
    expressions.function_analog_method = a_attr 
    expressions.function_analog_func = a_func

    blocks.blocks_handlers = b_handlers

