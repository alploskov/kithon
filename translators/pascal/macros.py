import _ast
from transPYler import macro, blocks


@macro('list_add')
def list_add(l, r):
    val = f"append({l.get('val')},{r.get('val')}...)"
    return {'val': val}

def is_read(tree):
    if type(tree) == _ast.Assign:
        if type(tree.value) == _ast.Call:
            types = ['str', 'int']
            if tree.value.func.id in types:
                if type(tree.value.args[0]) == _ast.Call:
                    if tree.value.args[0].func.id == 'input':
                        return 1
            if tree.value.func.id == 'input':
                return 1

@macro(is_read)
def read(tree):
    if tree.value.func.id == 'input':
        _type = 'str'
    else:
        _type = tree.value.func.id
    blocks.add_var(tree.targets[0].id, _type)
    msg = ""
    if type(tree.value.args[0]) == _ast.Call:
        msg = f"Write('{tree.value.args[0].args[0].value}');\n"
    elif type(tree.value.args[0]) == _ast.Constant:
        msg = f"Write('{tree.value.args[0].value}');\n"
    return f"{msg}Readln({tree.targets[0].id});"

macro({"print": "Writeln",
       ('list', 'list', '+'): list_add,
})
