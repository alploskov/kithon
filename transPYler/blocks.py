import _ast
import ast
from . import core, expressions
from .utils import add_var, is_var_created, element_type
from .core import parser, tmpls, node


get_val = lambda i: parser(i)()

nesting_level = 0

def expr(expr):
    tmp = tmpls.get("expr")
    value = parser(expr.value)
    return tmp.render(value=value)
    
def assign(expr):
    value = parser(expr.value)
    var = parser(expr.targets[0])
    _type = value.type
    if type(expr.targets[0]) == _ast.Name and not(is_var_created(var())):
        # May be changes array, etc (a[0] = 1)
        add_var(var(), _type)
        tmp = tmpls.get('new_var')
        return tmp.render(var=var, value=value)
    tmp = tmpls.get('assign')
    return tmp.render(
        var=var,
        value=value,
        type=tmpls.get('types').get(_type) or _type
    )

def ann_assign(expr):
    tmp = tmpls.get('ann_assign')
    var = parser(expr.target)
    _type = expr.annotation.id
    core.variables.get(namespace).update({var: _type})
    val = parser(expr.value)
    return tmp.render(
        var = var,
        _type = tmpls.get('types').get(_type) or _type,
        val = val
    )

def aug_assign(expr):
    targets = [expr.target]
    value = ast.BinOp(
        left = expr.target,
        op = expr.op,
        right = expr.value
    )
    return assign(ast.Assign(targets=targets, value=value))

def _if(tree):
    tmp = tmpls.get("if")
    condition = parser(tree.test)
    body = expression_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return tmp.render(
        condition=condition,
        body=body,
        els=els
    )

def _else(tree):
    if type(tree[0]) == _ast.If:
        return else_if(tree[0])
    tmp = tmpls.get('else')
    body = expression_block(tree)
    return tmp.render(body=body, nl=nesting_level)

def else_if(tree):
    tmp = tmpls.get("else_if")
    return tmp.render(_if=_if(tree))

def _while(tree):
    tmp = tmpls.get("while")
    condition = parser(tree.test)
    body = expression_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return tmp.render(
        condition = condition,
        body = body,
        els = els
    )

def _for(tree):
    var = parser(tree.target)
    body = expression_block(tree.body)
    if type(tree.iter) == _ast.Call and tree.iter.func.id == 'range':
        if 'c_like_for' in tmpls:
            if not(is_var_created(var())):
                add_var(var(), 'int')
            param = [parser(i)() for i in tree.iter.args]
            if len(param) < 3:
                param.append('1')
            if len(param) < 3:
                param.insert(0, '0')
            tmp = tmpls.get('c_like_for')
            return tmp.render(
                var = var,
                body = body,
                start = param[0],
                finish = param[1],
                step = param[2]
            )
    tmp = tmpls.get('for')
    obj = parser(tree.iter)
    if not(is_var_created(var())):
        add_var(var(), element_type(obj))
    return tmp.render(var=var, obj=obj, body=body)

def define_function(tree):
    tmp = tmpls.get('def')
    args = list(map(get_val, tree.args.args))
    name = tree.name
    ret_t = ''
    global_vars = core.variables.get('main')
    core.namespace += f'.{name}'
    core.variables.update({core.namespace: {}})
    core.variables.get(core.namespace).update(global_vars)
    body = expression_block(tree.body)
    core.namespace = ".".join(core.namespace.split(".")[:-1])
    if tree.returns:
        add_var(name, {
            'base_type': 'func',
            'ret_type': tree.returns.id
        })
        ret_t = tmpls.get('types').get(t) or t
    return tmp.render(name=name, args=args, body=body, ret_t=ret_t)

def ret(expr):
    tmp = tmpls.get("return")
    return tmp.render(value=parser(expr.value))

def scope_of_view(tree):
    for i in tree.names:
        _type = core.variables.get(".".join(core.namespace.split(".")[:-1])).get(i)
        core.variables.get(core.namespace).update({i: _type})
    return ''

def expression_block(body):
    global nesting_level
    nesting_level += 1
    body = list(map(parser, body))
    body = tmpls.get('body').render(body=body, nl=nesting_level)
    nesting_level -= 1
    return body

core.elements |= {
    _ast.Assign: assign,
    _ast.AnnAssign: ann_assign,
    _ast.Expr: expr,
    _ast.AugAssign: aug_assign,
    _ast.If: _if,
    _ast.While: _while,
    _ast.For: _for,
    _ast.FunctionDef: define_function,
    _ast.Return: ret,
    _ast.Global: scope_of_view,
    _ast.Nonlocal: scope_of_view,
    _ast.Break: lambda t: tmpls.get('break').render(),
    _ast.Continue: lambda t: tmpls.get('continue').render(),
}
