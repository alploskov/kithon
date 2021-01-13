import ast
import _ast

def dentification_signs(signs):
    finished = {}
    for i in signs:
        if i == '+' or i == '-':
            op = ast.parse(f"a {i} b").body[0].value
            sign_type = type(op.op)
            finished.update({sign_type: signs.get(i)})
            op = ast.parse(f"{i} b").body[0].value
            sign_type = type(op.op)
            finished.update({sign_type: signs.get(i)})
        try:
            op = ast.parse(f"a {i} b").body[0].value
        except:
            op = ast.parse(f"{i} b").body[0].value
        op_type = type(op)
        if op_type == _ast.BinOp or op_type == _ast.BoolOp or op_type == _ast.UnaryOp:
            sign_type = type(op.op)
        else:
            sign_type = type(op.ops[0])    
        finished.update({sign_type: signs.get(i)})
    return finished


def conf(handlers, signs, a_func, operator_overloading, lib):
    core_data.core.handlers = handlers
    print(handlers)
    from transPYler import expressions
    expressions.signs = dentification_signs(signs)
    expressions.operator_overloading = operator_overloading
    expressions.function_analog_func = a_func
    expressions.lib = lib
