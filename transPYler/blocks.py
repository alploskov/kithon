import _ast
import ast
from . import core, expressions
from .core import parser, namespace, variables, handlers


def expr(expr):
    handler = handlers.get("expr")
    value = parser(expr.value).get("val")
    return handler(value)

def assign(expr):
    value = parser(expr.value)
    var = parser(expr.targets[0])
    _type = value.get("type")
    if type(expr.targets[0]) == _ast.Name: # Могут быть изменения массивов (a[0] = 1)
        if not (var.get('val') in variables.get(namespace).keys()):
            variables.get(namespace).update({var.get('val'): _type})
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
    pass

def _for(tree):
    var = parser(tree.target)
    body = statement_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in handlers:
                get_val = lambda i: i.get('val')
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
        if vars.get(i) != type(parser(vars.get(i))):
            global_vars.update({i: vars.get(i)})
        core.namespace += '.'+name
    variables.update({core.namespace: {}})
    variables.get(core.namespace).update(global_vars)
    body = statement_block(tree.body)
    namespace = ".".join(core.namespace.split(".")[:-1])
    if tree.returns:
        ret_t = parser(tree.returns)
        return handler(name, args, body, ret_t=ret_t)
    return handler(name, args, body)

def ret(expr):
    handler = handlers.get("return")
    return handler(parser(expr.value).get('val'))

def scope_of_view(tree):
    for i in tree.names:
        _type = variables.get(".".join(namespace.split(".")[:-1])).get(i)
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

def statement_block(body):
    handler = handlers.get("statement_block")
    body = handler(list(map(parser, body)))
    return body

def crawler(body):
    strings = []
    for i in body:
        i = parser(i)
        if i:
            strings.append(i)
    return '\n'.join(strings)
