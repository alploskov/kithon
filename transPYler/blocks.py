import _ast
import ast
from . import core, expressions
from .utils import add_var, is_var_created, element_type
from .core import parser, tmpls


get_val = lambda i: parser(i).get('val')

nesting_level = 0

def expr(expr):
    tmp = tmpls.get("expr")
    value = parser(expr.value).get("val")
    return tmp.render(value=value)

def assign(expr):
    value = parser(expr.value)
    var = parser(expr.targets[0])
    _type = value.get("type")
    if type(expr.targets[0]) == _ast.Name: # May be changes array, etc (a[0] = 1)
        if not(is_var_created(var.get('val'))):
            add_var(var.get('val'), _type)
            tmp = tmpls.get("new_var")
            return tmp.render(var=var.get('val'), value=value.get('val'))
    tmp = tmpls.get("assign")
    return tmp.render(var=var.get('val'), value=value.get('val'))

def ann_assign(expr):
    tmp = tmpls.get("ann_assign")
    var = parser(expr.target)
    _type = expr.annotation.id
    core.variables.get(namespace).update({var: _type})
    if expr.value:
        val = parser(expr.value)
        return tmp.render(var, _type, val=val)
    return tmp.render(var, _type)

def aug_assign(expr):
    targets = [expr.target]
    value = ast.BinOp(left=expr.target, op=expr.op, right=expr.value) 
    return assign(ast.Assign(targets=targets, value=value))

def _if(tree):
    tmp = tmpls.get("if")
    condition = parser(tree.test).get('val')
    body = expression_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    ret = tmp.render(condition=condition, body=body, els=els, nl=nesting_level)
    return ret

def _else(tree):
    if type(tree[0]) == _ast.If:
        body = else_if(tree[0])
    else:
        tmp = tmpls.get("else")
        body = expression_block(tree)
        body = tmp.render(body=body, nl=nesting_level)
    return body

def else_if(tree):
    tmp = tmpls.get("else_if")
    return tmp.render(_if=_if(tree))

def _while(tree):
    tmp = tmpls.get("while")
    condition = parser(tree.test).get('val')
    body = expression_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return tmp.render(condition, body, els)

def _for(tree):
    var = parser(tree.target)
    body = expression_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in tmpls:
                if not(is_var_created(var.get('val'))):
                    add_var(var.get('val'), 'int')
                param = list(map(get_val, tree.iter.args))
                if len(param) < 3:
                    param.append("1")
                if len(param) < 3:
                    param.insert(0, "0")
                tmp = tmpls.get("c_like_for")
                return tmp.render(var=var.get('val'), body=body,
                                  start=param[0], finish=param[1], step=param[2])
    tmp = tmpls.get("for")
    obj = parser(tree.iter)
    if not(is_var_created(var.get('val'))):
        add_var(var.get('val'), element_type(obj))
    return tmp.render(var=var.get('val'), obj=obj.get('val'), body=body)

def define_function(tree):
    tmp = tmpls.get("def")
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
        t = tree.returns.id
        add_var(name, t)
        ret_t = tmpls.get('types').get(t) if t in tmpls.get('types') else t
    return tmp.render(name=name, args=args, body=body, ret_t=ret_t)

def ret(expr):
    tmp = tmpls.get("return")
    return tmp.render(value=parser(expr.value).get('val'))

def scope_of_view(tree):
    for i in tree.names:
        _type = core.variables.get(".".join(core.namespace.split(".")[:-1])).get(i)
        core.variables.get(core.namespace).update({i: _type})
    return ''

def expression_block(body):
    global nesting_level
    nesting_level += 1
    body = list(map(parser, body))
    body = tmpls.get("body").render(body=body, nl=nesting_level)
    nesting_level -= 1
    return body

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
