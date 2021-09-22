import ast
import _ast
from collections import namedtuple
from os import listdir
from .utils import element_type, transpyler_type


def expr(self, expr):
    tmp = self.tmpls.get('expr')
    value = self.visit(expr.value)
    return tmp.render(value=value)
    
def assign(self, expr):
    value = self.visit(expr.value)
    var = self.visit(expr.targets[0])
    _type = value.type
    if type(expr.targets[0]) == _ast.Name:            # May be changes array or attributes, etc (a[0] = 1)
        var_name = f'{self.namespace}.{expr.targets[0].id}'
        if var_name not in self.variables:
            self.variables.update({var_name: {
                'type': [_type],
                'own': var_name
            }})
            tmp = self.tmpls.get('new_var')
            return tmp.render(var=var, value=value, _type=_type)
        self.variables[var_name]['type'].append(_type)
    tmp = self.tmpls.get('assign')
    return tmp.render(
        var=var,
        value=value,
        _type=_type
    )

def ann_assign(self, expr):
    tmp = self.tmpls.get('ann_assign')
    var = self.visit(expr.target)
    _type = expr.annotation.id
    self.variables.get(namespace).update({var: _type})
    val = self.visit(expr.value)
    return tmp.render(
        var = var,
        _type = self.tmpls.get('types').get(_type, _type),
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

def _if(self, tree, is_elif=False):
    tmp = self.tmpls.get('elif' if is_elif else 'if')
    condition = self.visit(tree.test)
    _body, body = expression_block(self, tree.body)
    els = ""
    if tree.orelse:
        els = _else(self, tree.orelse)
    return tmp.render(
        condition=condition,
        body=body,
        _body=_body,
        els=els,
        ctx=self
    )

def _else(self, tree):
    if type(tree[0]) == _ast.If:
        return _if(self, tree[0], is_elif=True)
    tmp = self.tmpls.get('else')
    _body, body = expression_block(self, tree)
    return tmp.render(body=body, nl=self.nl+1, _body=_body)

def _while(self, tree):
    tmp = self.tmpls.get('while')
    condition = self.visit(tree.test)
    _body, body = expression_block(self, tree.body)
    els_body = cmpl_els_body = ''
    if tree.orelse:
        els_body, cmpl_els_body = expression_block(self, tree.orelse)
    return tmp.render(
        condition = condition,
        body = body, _body = _body,
        els_body=els_body, cmpl_els_body=cmpl_els_body)

def _for(self, tree):
    var = self.visit(tree.target)
    _body, body = expression_block(self, tree.body)
    iter = tree.iter
    els_body = cmpl_els_body = ''
    if tree.orelse:
        els_body, cmpl_els_body = expression_block(self, tree.orelse)
    if type(iter) == _ast.Call and iter.func.id == 'range' and 'c_like_for' in self.tmpls:
        var_name = f'{self.namespace}.{tree.target.id}'
        if var_name not in self.variables:
            self.variables.update({var_name: {
                'type': ['int'],
                'own': var_name
            }})
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
            step = param[2])
    tmp = self.tmpls.get('for')
    obj = self.visit(tree.iter)
    var_name = f'{self.namespace}.{tree.target.id}'
    if var_name not in self.variables:
        self.variables.update({var_name: {
            'type': [element_type(obj)],
            'own': var_name
        }})
    return tmp.render(
        var=var, obj=obj, body=body, ctx=self,
        els_body=els_body, cmpl_els_body=cmpl_els_body)

def define_function(self, tree, new_impl=False):
    tmp = self.tmpls.get('func')
    name = tree.name
    self.namespace += f'.{name}'
    args = list(map(self.visit, tree.args.args))
    args_types = tuple([a.type for a in args])
    ret_t = getattr(tree.returns, 'id', [])
    self.variables.update({self.namespace: {
        'base_type': 'func',
        'ret_type': ret_t
    }})
    _body, body = expression_block(self, tree.body)
    ret_t = self.variables[self.namespace]['ret_type']
    if ret_t == []:
        rt = 'None'
    else:
        rt = ret_t[-1]
    ret_t = self.tmpls.get('types').get(rt, rt)
    code = tmp.render(name=name, args=args, ret_t=ret_t, body=body)
    self.namespace = self.namespace.replace('.'+name, '')
    return code

def overload(function, args_types):
    pass

def ret(self, expr):
    tmp = self.tmpls.get('return')
    val = self.visit(expr.value)
    self.variables[self.namespace]['ret_type'] = val.type
    return tmp.render(value=val)

def expression_block(self, body):
    tmp = self.tmpls.get('body')
    self.nl += 1
    _body = list(map(self.visit, body))
    body = tmp.render(body=_body, nl=self.nl)
    self.nl -= 1
    return _body, body

def _nonlocal(self, tree):
    for i in tree.names:
        var_name = f'{self.namespace}.{i}'
        previous_ns = self.namespace[:self.namespace.rfind('.')]
        self.variables.update({var_name: {
                'type': self.variables[f'{previous_ns}.{i}']['type'],
                'own': f'{previous_ns}.{i}'
        }})
    if 'nonlocal' not in self.tmpls:
        return ''
    return self.tmpls['nonlocal'].render(
        vars=list(map(visit, tree.names))
    )

def _global(self, tree):
    for i in tree.names:
        var_name = f'{self.namespace}.{i}'
        self.variables.update({var_name: {
                'type': self.variables[f'main.{i}']['type'],
                'own': f'main.{i}'
        }})
    if 'global' not in self.tmpls:
        return ''
    return self.tmpls['global'].render(
        vars=list(map(visit, tree.names))
    )
    
def _break(self, t):
    tmp = self.tmpls.get('break')
    return tmp.render(nl=self.nl)

def _continue(self, t):
    tmp = self.tmpls.get('continue')
    return tmp.render(nl=self.nl)
