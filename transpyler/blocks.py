import ast
import _ast
from .types import element_type
from .core import visitor
from .utils import get_ctx


@visitor
def expr(self, tree: _ast.Expr):
    return self.node(
        parts={'value': self.visit(tree.value)},
        tmp='expr'
    )

@visitor
def assign(self, tree: _ast.Assign, _type=None):
    variable = tree.targets[0]
    var = self.visit(variable)
    value = self.visit(tree.value)
    _type = _type or value.type
    tmp = 'new_var'
    if isinstance(variable, _ast.Name):
        full_name = f'{self.namespace}.{variable.id}'
    elif isinstance(variable, _ast.Subscript):
        full_name = f'{self.namespace}.{variable.value.id}'
        self.variables[full_name]['type'].el_type = _type
    elif isinstance(variable, _ast.Attribute):
        obj_name = variable.value.id
        if obj_name == 'self':
            full_name = f'{get_ctx(self)}.{variable.attr}'
        else:
            full_name = f'{self.namespace}.{obj_name}'
    if full_name not in self.variables:
        if get_ctx(self):
            tmp = 'attr'
        var.parts['own'] = full_name
        self.variables.update({full_name: {
            'type': _type,
            'own': full_name,
            'immut': True
        }})
    else:
        tmp = 'assign'
        self.variables[full_name]['immut'] = False
        self.variables[full_name]['type'] = _type
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
def ann_assign(self, tree: _ast.AnnAssign):
    pass

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
    obj = self.visit(tree.iter)
    parts = {}
    if (isinstance(tree.iter, _ast.Call)
        and isinstance(tree.iter.func, _ast.Name)
        and tree.iter.func.id == 'range'
        and 'c_like_for' in self.templates):
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
        tmp = 'for'
        _type = element_type(obj)
        parts |= {'obj': obj}
    var = self.visit(tree.target)
    var_name = f'{self.namespace}.{tree.target.id}'
    if var_name not in self.variables:
        self.variables.update({var_name: {
            'type': _type,
            'own': var_name
        }})
    else:
        self.variables[var_name]['type'] = _type
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
    parts = {}
    if get_ctx(self):
        attrs = []
        for attr in self.variables:
            if (attr.startswith(self.namespace)
                and self.variables[attr]['type'] != 'func'):
                attrs.append(attr[len(self.namespace)+1:])
        parts = {
            'attrs': attrs,
            'class_name': self.namespace.split('.')[-1]
        }
        if name == '__init__':
            tmp = 'init'
        else:
            tmp =  'method'
    else:
        tmp = 'func'
    self.namespace += f'.{name}'
    args = list(map(self.visit, tree.args.args))
    ret_t = getattr(tree.returns, 'id', '')
    self.variables.update({self.namespace: {
        'type': 'func',
        'ret_type': ret_t
    }})
    func = self.node(
        tmp=tmp,
        type='func',
        parts={
            'name': name,
            'args': args,
            'ret_type': ret_t,
            'body': expression_block(self, tree.body),
            'nl': self.nl
        } | parts
    )
    self.namespace = self.namespace[:-len(name)-1]
    return func

@visitor
def arg(self, tree: _ast.arg):
    name = tree.arg
    _type = getattr(tree.annotation, 'id', 'any')
    if name != 'self':
        full_name = f'{self.namespace}.{name}'
        self.variables.update({full_name: {
            'type': _type,
            'own': full_name
        }})
    return self.node(
        tmp='arg',
        type=_type,
        parts={'name': name}
    )

@visitor
def define_class(self, tree: _ast.ClassDef):
    name = tree.name
    self.namespace += f'.{name}'
    self.variables.update({self.namespace: {
        'type': 'class'
    }})
    self.nl += 1
    node = self.node(
        tmp='class',
        type='class',
        parts={
            'name': name,
            'attrs': [],
            'methods': [],
            'init': None,
            'nl': self.nl
        }
    )
    self.ctx = node
    for field in map(self.visit, tree.body):
        if isinstance(field.ast, _ast.Assign):
            node.parts['attrs'].append(field)
        elif isinstance(field.ast, _ast.FunctionDef):
            if field.ast.name == '__init__':
                node.parts['init'] = field
            else:
                node.parts['methods'].append(field)
    self.nl -= 1
    self.namespace = self.namespace[:-len(name)-1]
    return node

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
            'nl': self.nl
        }
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
            'vars': list(map(
                lambda n: self.visit(
                    ast.Name(id=n, ctx=ast.Load)
                ),
                tree.names
            ))
        }
    )

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
