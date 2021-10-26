import ast
import _ast
from .types import element_type
from .core import visitor


@visitor
def expr(self, tree: _ast.Expr):
    return self.node(
        parts={'value': self.visit(tree.value)},
        tmp='expr'
    )

@visitor
def assign(self, tree: _ast.Assign, _type=None):
    var = self.visit(tree.targets[0])
    value = self.visit(tree.value)
    _type = value.type
    tmp = 'assign'
    # May be changes array or attributes, etc
    if isinstance(tree.targets[0], _ast.Name):
        full_name = f'{self.namespace}.{tree.targets[0].id}'
        if full_name not in self.variables:
            self.variables.update({full_name: {
                'type': [_type],
                'own': full_name,
                'immut': True
            }})
            tmp = 'new_var'
        else:
            self.variables[full_name]['type'].append(_type)
    elif isinstance(tree.targets[0], _ast.Subscript):
        full_name = f'{self.namespace}.{tree.targets[0].value.id}'
    elif isinstance(tree.targets[0], _ast.Attribute): ...
    return self.node(
        parts={
            'var': var,
            'value': value,
            'own': self.variables[full_name]['own'],
        },
        type=_type,
        tmp=tmp
    )

@visitor
def aug_assign(self, tree: _ast.AugAssign):
    return self.assign(ast.Assign(
        targets=[tree.target],
        value=ast.BinOp(
            left = tree.target,
            op = tree.op,
            right = tree.value
    )))

@visitor
def _if(self, tree: _ast.If, is_elif=False):
    return self.node(
        parts={
            'condition': self.visit(tree.test),
            'body': expression_block(self, tree.body),
            'nl': self.nl + 1,
            'els': _else(self, tree.orelse)
        },
        tmp = 'elif' if is_elif else 'if'
    )

def _else(self, body):
    if not body:
        return ''
    elif isinstance(body[0], _ast.If):
        return _if(self, body[0], is_elif=True)
    return self.node(
        parts={
            'body': expression_block(self, body),
            'nl': self.nl + 1,
        },
        tmp='else'
    )

@visitor
def _while(self, tree: _ast.While):
    return self.node(
        parts={
            'condition': self.visit(tree.test),
            'body': expression_block(self, tree.body),
            'nl': self.nl + 1,
        },
        tmp = 'while'
    )

@visitor
def _for(self, tree: _ast.For):
    iter = tree.iter
    parts = {}
    if isinstance(iter, _ast.Call) and iter.func.id == 'range' and 'c_like_for' in self.templates:
        tmp = 'c_like_for'
        _type = 'int'
        param = [self.visit(a) for a in tree.iter.args]
        if len(param) < 3:
            param.append(self.visit(ast.Constant(value=1)))
        if len(param) < 3:
            param.insert(0, self.visit(ast.Constant(value=0)))
        parts |= {
            'start': param[0],
            'finish': param[1],
            'step': param[2]
        }
    else:
        obj = self.visit(iter)
        tmp = 'for'
        _type = element_type(obj)
        parts |= {'obj': obj}
    var = self.visit(tree.target)
    var_name = f'{self.namespace}.{tree.target.id}'
    if var_name not in self.variables:
        self.variables.update({var_name: {
            'type': [_type],
            'own': var_name
        }})
    else:
        self.variables[var_name]['type'].append(_type)
    return self.node(
        parts = parts | {
            'var': var,
            'body': expression_block(self, tree.body)
        },
        tmp = tmp
    )

@visitor
def define_function(self, tree: _ast.FunctionDef):
    name = tree.name
    self.namespace += f'.{name}'
    args = list(map(self.visit, tree.args.args))
    ret_t = getattr(tree.returns, 'id', [])
    self.variables.update({self.namespace: {
        'type': 'func',
        'ret_type': ret_t
    }})
    func = self.node(
        tmp='func',
        parts={
            'name': name,
            'args': args,
            'ret_type': ret_t,
            'body': expression_block(self, tree.body)
        }
    )
    self.namespace = self.namespace.replace('.'+name, '')
    return func

@visitor
def arg(self, tree: _ast.arg):
    name = tree.arg
    _type = getattr(tree.annotation, 'id', 'any')
    full_name = f'{self.namespace}.{name}'
    self.variables.update({full_name: {
        'type': [_type],
        'own': full_name
    }})
    return self.node(
        tmp='arg',
        type=_type,
        parts={'name': name}
    )

def overload(function, args_types):
    pass

@visitor
def ret(self, tree: _ast.Return):
    val = self.visit(tree.value)
    self.variables[self.namespace]['ret_type'] = val.type
    return self.node(
        tmp='return',
        parts={'value': val}
    )

def expression_block(self, body):
    self.nl += 1
    body = self.node(
        tmp='body',
        parts={
            'body': list(map(self.visit, body)),
            'nl': self.nl}
    )
    self.nl -= 1
    return body

@visitor
def _nonlocal(self, tree: _ast.Nonlocal):
    for i in tree.names:
        full_name = f'{self.namespace}.{i}'
        previous_ns = self.namespace[:self.namespace.rfind('.')]
        self.variables.update({
            full_name: self.variables[f'{previous_ns}.{i}']
        })
    return self.node(
        tmp='nonlocal',
        parts={
            'vars': list(map(self.visit, tree.names))
    })

@visitor
def _global(self, tree: _ast.Global):
    for i in tree.names:
        full_name = f'{self.namespace}.{i}'
        self.variables.update({
            full_name: self.variables[f'main.{i}']
        })
    return self.node(
        tmp='global',
        parts={
            'vars': list(map(
                lambda n: self.visit(
                    ast.Name(id=n, ctx=ast.Load)
                ),
                tree.names
            ))
        }
    )

@visitor
def _break(self, tree: _ast.Break):
    return self.node(tmp='break')

@visitor
def _continue(self, tree: _ast.Continue):
    return self.node(tmp='continue')
