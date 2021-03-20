import _ast
import ast
from . import core, expressions
from .core import parser, namespace, variables, handlers
from .macros import what_macro


def add_var(name, _type):
    variables.get(namespace).update({name: _type})

def expr(expr):
    handler = handlers.get("expr")
    value = parser(expr.value).get("val")
    return handler(value)

def assign(expr):
    value = parser(expr.value)
    var = parser(expr.targets[0])
    if macro := what_macro((var, value, '=')):
        return macro(var, value)
    _type = value.get("type")
    if type(expr.targets[0]) == _ast.Name: # Могут быть изменения массивов (a[0] = 1)
        if not(var.get('val') in variables.get(namespace).keys()):
            add_var(var.get('val'), _type)
            handler = handlers.get("new_var")
            return handler(var.get('val'), value.get('val'))
    handler = handlers.get("assign")
    return handler(var.get('val'), value.get('val'))

def ann_assign(expr):
    handler = handlers.get("ann_assign")
    var = parser(expr.target)
    _type = expr.annotation.id
    variables.get(namespace).update({var: _type})
    if expr.value:
        val = parser(expr.value)
        return handler(var, _type, val=val)
    return handler(var, _type)

def aug_assign(expr):
    targets = [expr.target]
    value = ast.BinOp(left=expr.target, op=expr.op, right=expr.value) 
    return assign(ast.Assign(targets=targets, value=value))

def _if(tree):
    handler = handlers.get("if")
    condition = parser(tree.test).get('val')
    body = statement_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return handler(condition, body, els)

def _else(tree):
    if type(tree[0]) == _ast.If:
        body = else_if(tree[0])
    else:
        handler = handlers.get("else")
        body = handler(statement_block(tree))
    return body

def else_if(tree):
    handler = handlers.get("else_if")
    return handler(_if(tree))

def _while(tree):
    handler = handlers.get("while")
    condition = parser(tree.test).get('val')
    body = statement_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return handler(condition, body, els)

def _for(tree):
    var = parser(tree.target)
    body = statement_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in handlers:
                get_val = lambda i: parser(i).get('val')
                param = list(map(get_val, tree.iter.args))
                if len(param) < 3:
                    param.append("1")
                if len(param) < 3:
                    param.insert(0, "0")
                handler = handlers.get("c_like_for")
                return handler(var.get('val'), body, param)
    handler = handlers.get("for")
    obj = parser(tree.iter)
    return handler(var.get('val'), obj.get('val'), body)

def define_function(tree):
    handler = handlers.get("def")
    args = list(map(parser, tree.args.args))
    name = tree.name
    vars = variables.get(core.namespace)
    global_vars = {}
    for i in vars:
        global_vars.update({i: vars.get(i)})
    core.namespace += f'.{name}'
    variables.update({core.namespace: {}})
    variables.get(core.namespace).update(global_vars)
    body = statement_block(tree.body)
    core.namespace = ".".join(core.namespace.split(".")[:-1])
    if tree.returns:
        ret_t = parser(tree.returns)
        return handler(name, args, body, ret_t=ret_t)
    return handler(name, args, body)

def ret(expr):
    handler = handlers.get("return")
    return handler(parser(expr.value).get('val'))

def scope_of_view(tree):
    for i in tree.names:
        _type = variables.get(".".join(core.namespace.split(".")[:-1])).get(i)
        variables.get(namespace).update({i: _type})
    return ''

core.elements |= {_ast.Assign: assign,
                  _ast.AnnAssign: ann_assign,
                  _ast.Expr: expr,
                  _ast.AugAssign: aug_assign,
                  _ast.If: _if,
                  _ast.While: _while,
                  _ast.For: _for,
                  _ast.FunctionDef: define_function,
                  _ast.Return: ret,
                  _ast.Global: scope_of_view,
                  _ast.Nonlocal: scope_of_view
}

nesting_level = 0
def statement_block(body):
    global nesting_level
    handler = handlers.get("statement_block")
    nesting_level += 1
    body = handler(list(map(parser, body)))
    nesting_level -= 1
#    _body = []
#    for i in body:
#        print(parser(i))
#        _body.append(parser(i))
    return body
