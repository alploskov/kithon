import _ast
import ast
from .utils import element_type, add_var, is_var_created


get_val = lambda i: visit(i)()

def expr(self, expr):
    tmp = self.tmpls.get('expr')
    value = self.visit(expr.value)
    return tmp.render(value=value)
    
def assign(self, expr):
    value = self.visit(expr.value)
    var = self.visit(expr.targets[0])
    _type = value.type
    if type(expr.targets[0]) == _ast.Name and not(is_var_created(self, var())):
        # May be changes array or attributes, etc (a[0] = 1)
        add_var(self, expr.targets[0].id, _type)
        tmp = self.tmpls.get('new_var')
        return tmp.render(var=var, value=value)
    tmp = self.tmpls.get('assign')
    return tmp.render(
        var=var,
        value=value,
        type=_type
    )

def ann_assign(self, expr):
    tmp = self.tmpls.get('ann_assign')
    var = self.visit(expr.target)
    _type = expr.annotation.id
    self.variables.get(namespace).update({var: _type})
    val = self.visit(expr.value)
    return tmp.render(
        var = var,
        _type = self.tmpls.get('types').get(_type) or _type,
        val = val
    )

def aug_assign(self, expr):
    targets = [expr.target]
    value = ast.BinOp(
        left = expr.target,
        op = expr.op,
        right = expr.value
    )
    return assign(self,
        ast.Assign(targets=targets, value=value)
    )

def _if(self, tree):
    tmp = self.tmpls.get("if")
    condition = self.visit(tree.test)
    body = expression_block(self, tree.body)
    els = ""
    if tree.orelse:
        els = _else(self, tree.orelse)
    return tmp.render(
        condition=condition,
        body=body,
        els=els
    )

def _else(self, tree):
    if type(tree[0]) == _ast.If:
        return else_if(self, tree[0])
    tmp = self.tmpls.get('else')
    body = expression_block(self, tree)
    return tmp.render(body=body, nl=self.nl)

def else_if(self, tree):
    tmp = self.tmpls.get('else_if')
    return tmp.render(_if=_if(self, tree))

def _while(self, tree):
    tmp = self.tmpls.get('while')
    condition = self.visit(tree.test)
    body = expression_block(self, tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return tmp.render(
        condition = condition,
        body = body,
        els = els
    )

def _for(self, tree):
    var = self.visit(tree.target)
    body = expression_block(self, tree.body)
    if type(tree.iter) == _ast.Call and tree.iter.func.id == 'range':
        if 'c_like_for' in self.tmpls:
            if not(is_var_created(self, var())):
                add_var(self, var(), 'int')
            param = [self.visit(i) for i in tree.iter.args]
            if len(param) < 3:
                param.append(self.visit(ast.Constant(value=1)))
            if len(param) < 3:
                param.insert(0, self.visit(ast.Constant(value=0)))
            tmp = self.tmpls.get('c_like_for')
            return tmp.render(
                var = var,
                body = body,
                start = param[0],
                finish = param[1],
                step = param[2],
            )
    tmp = self.tmpls.get('for')
    obj = self.visit(tree.iter)
    if not(is_var_created(self, var())):
        add_var(self, var(), element_type(obj))
    return tmp.render(var=var, obj=obj, body=body)

def define_function(self, tree):
    tmp = self.tmpls.get('def')
    args = list(map(get_val, tree.args.args))
    name = tree.name
    ret_t = ''
    global_vars = self.variables.get('main')
    self.namespace += f'.{name}'
    self.variables.update({
        self.namespace: {}
    })
    self.variables.get(self.namespace).update(global_vars)
    body = expression_block(self, tree.body)
    self.namespace = '.'.join(self.namespace.split('.')[:-1])
    if tree.returns:
        add_var(name, {
            'base_type': 'func',
            'ret_type': tree.returns.id
        })
        ret_t = self.tmpls.get('types').get(t, t)
    return tmp.render(name=name, args=args, body=body, ret_t=ret_t)

def ret(expr):
    tmp = self.tmpls.get('return')
    return tmp.render(value=self.visit(expr.value))

def scope_of_view(self, tree):
    for i in tree.names:
        _type = self.variables.get(".".join(self.namespace.split(".")[:-1])).get(i)
        self.variables.get(self.namespace).update({i: _type})
    return ''

def expression_block(self, body):
    self.nl += 1
    body = list(map(self.visit, body))
    body = self.tmpls.get('body').render(body=body, nl=self.nl)
    self.nl -= 1
    return body

def _break(self, t):
    tmp = self.tmpls.get('break')
    return tmp.render(nl=self.nl)

def _continue(self, t):
    tmp = self.tmpls.get('continue')
    return tmp.render(nl=self.nl)
