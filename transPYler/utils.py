import ast
import _ast


def sign_to_type(sign):
    try:
        op = ast.parse(f"a {sign} b").body[0].value
    except:
        op = ast.parse(f"{sign} b").body[0].value
    op_type = type(op)
    if op_type == _ast.BinOp or op_type == _ast.BoolOp or op_type == _ast.UnaryOp:
        sign_type = type(op.op)
    else:
        sign_type = type(op.ops[0])    
    return sign_type

def dentification_signs(signs):
    finished = {}
    for i in signs:
        if i == '+' or i == '-':
            op = ast.parse(f"{i} b").body[0].value
            sign_type = type(op.op)
            finished.update({sign_type: signs.get(i)})
        sign_type = sign_to_type(i)
        finished.update({sign_type: signs.get(i)})
    return finished

def op_overload_key(macros):
    finished = {}
    for i in macros:
        if type(i) == tuple:
            sign_type = sign_to_type(i[2])
            finished.update({(i[0], i[1], sign_type): macros.get(i)})
        else:
            finished.update({i: macros.get(i)})
    return finished
