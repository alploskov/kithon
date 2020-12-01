import ast


def dentification_signs(signs):
    finished = {}
    for i in signs:
        sign_type = type(ast.parse(f"a{i}b").body[0].value.op)
        finished.update({sign_type: signs.get(i)})
    return finished
