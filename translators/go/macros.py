import ast
import _ast
import re
import uuid
from transPYler import macro, objects, blocks
from transPYler.core import parser, variables, ttype
from transPYler.ast_decompiler import decompile
from utils import type_to_type


def is_route(node):
    try:
        if decompile(node.decorator_list[0].func) == 'app.route':
            return 1
    except:
        return 0

@macro(is_route)
def route(node):
    url = node.decorator_list[0].args[0].value
    for i in url.split('/'):
        if i:
            if i[0] == '<' and i[-1] == '>':
                pass
                #print(i[1:-1])
    node.decorator_list = []
    node.args.args = [ast.arg(arg='w', annotation=ast.Name(id='http.ResponseWriter')),
                      ast.arg(arg='request', annotation=ast.Name(id='*http.Request'))
                      ]
    node.name = ''
    node.body[-1] = ast.parse(f"fmt.Fprintf(w, {decompile(node.body[-1].value)})").body[0]
    handler = parser(node)
    return f'http.HandleFunc("{url}", {handler})'

@macro('list_add')
def list_add(l, r):
    val = f"append({l.get('val')},{r.get('val')}...)"
    return {'val': val, 'type': l.get('type')}

def is_read(tree):
    try:
        name = tree.value.func.id
        types = ['str', 'int']
        if name in types:
            if type(tree.value.args[0]) == _ast.Call:
                if tree.value.args[0].func.id == 'input':
                    return 1
        elif name == 'input':
            return 1
    except:
        return 0

@macro(is_read)
def read(tree):
    out = ''
    if tree.value.func.id == 'input':
        _type = 'str'
    else:
        _type = tree.value.func.id
    if tree.targets[0].id not in variables:
        blocks.add_var(tree.targets[0].id, _type)
        out += f'var {tree.targets[0].id} {type_to_type(_type)}\n'
    type_ann = {'int': '%d', 'str': '%s', 'fload': '%f'}.get(_type)
    if type(tree.value.args[0]) == _ast.Call:
        out += f"fmt.Print(\"{tree.value.args[0].args[0].value}\")\n"
    elif type(tree.value.args[0]) == _ast.Constant:
        out += f"fmt.Print(\"{tree.value.args[0].value}\")\n" 
    out += f'fmt.Scanf(\"{type_ann}\", &{tree.targets[0].id})'
    return out

def append(_list, el):
    return {'val': f'{_list.get("val")} = append({_list.get("val")}, {el.get("val")})'}

def index(_list, el):
    return {'val': f'SearchString({_list.get("val")}, {el.get("val")})', 'type':'int'}

def find(_str, sub_str):
    return {'val': f'strings.Index({_str}, {sub_str})', 'type':'int'}

def create_list(_list, _type):
    if _list.get('val') == '[]None{}':
        return {'val': f"[]{type_to_type(_type.get('val'))}{{}}", 'type': f"list<{_type.get('val')}>"}
    return {'val': _list.get('val'), 'type': f"list<{_type.get('val')}>"}

@macro("len")
def ln(obj):
    if obj.get('type') == 'str':
        return {'val': f'len({obj.get("val")})/2', 'type': 'int'}
    return {'type': 'int', 'val': f'len({obj.get("val")})'}

macro({"print": "fmt.Println",
       "input": "prompt",
       ('list', 'type', '*'): create_list,
       ('list', 'list', '+'): list_add
})
objects({"list": {"index": index,
                  "append": append
                  },
         "str": {"index": find}
})
