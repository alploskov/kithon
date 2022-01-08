import ast
import _ast
from .types import element_type, type_render, Func, List, Dict, Tuple
from .core import visitor


@visitor
def expr(self, tree: _ast.Expr):
    return self.node(
        parts={'value': self.visit(tree.value)},
        tmp='expr'
    )

def create_var(self, var, _type):
    """
    returns True if var is new, otherwise returns False
    """
    if isinstance(var.ast, _ast.Name):
        var.own = f'{self.namespace}.{var.ast.id}'
    elif isinstance(var.ast, _ast.Subscript):
        self.variables[var.own]['type'].el_type = _type
    if var.own in self.variables:
        self.variables[var.own]['immut'] = False
        return False
    self.variables.update({var.own: {
        'type': _type,
        'own': var.own,
        'immut': True
    }})
    return True

@visitor
def assign(self, tree: _ast.Assign, _type=None):
    var = self.visit(tree.targets[0])
    value = self.visit(tree.value)
    if isinstance(var.ast, _ast.Tuple):
        return unpack(self, var, value)
    _type = _type or value.type
    tmp = {
        _ast.Name: 'assign',
        _ast.Subscript: 'assignment_by_key',
        _ast.Attribute: 'set_attr'
    }.get(type(var.ast))
    if create_var(self, var, _type):
        if tmp == 'assign':
            tmp = 'new_var'
        elif tmp == 'set_attr':
            tmp = 'new_attr'
    if self.variables[self.namespace]['type'] == 'class':
        tmp = 'static_attr'
    return self.node(
        parts={
            'var': var,
            'value': value,
            'own': var.own
        },
        type=_type,
        tmp=tmp
    )

def unpack(self, _vars, value):
    vars_names = _vars.parts['ls']
    is_new = 0
    _type = None
    if isinstance(value.type, List):
        _type = value.type.el_type
    elif isinstance(value.type, Dict):
        _type = value.type.key_type
    for pos, var in enumerate(vars_names):
        is_new += create_var(
            self, var,
            _type or value.type.els_types[pos]
        )
    if 0 < is_new < len(vars_names):
        print(f'\033[32mWarning:\033[38m possible declaring error in line {_vars.ast.lineno}')
    return self.node(
        tmp='unpack_to_new' if is_new else 'unpack',
        parts={'vars': vars_names, 'value': value}
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
            'els': _else(self, tree.orelse)
        },
        tmp = 'elif' if is_elif else 'if'
    )

def _else(self, body):
    if not body:
        return ''
    if isinstance(body[0], _ast.If):
        return _if(self, body[0], is_elif=True)
    return self.node(
        parts={
            'body': expression_block(self, body),
        },
        tmp='else'
    )

@visitor
def _while(self, tree: _ast.While):
    return self.node(
        parts={
            'condition': self.visit(tree.test),
            'body': expression_block(self, tree.body),
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
    if self.variables[self.namespace]['type'] == 'class':
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
        'type': Func(name, args, ret_t),
        'own': self.namespace,
    }})
    _body = expression_block(self, tree.body)
    ret_t = ret_t or self.variables[self.namespace]['type'].ret_type
    func = self.node(
        tmp=tmp,
        type=Func(name, args, ret_t),
        own=self.namespace,
        parts={
            'name': name,
            'args': args,
            'ret_type': type_render(self, ret_t),
            'body': _body,
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
        'type': 'class',
        'own': self.namespace
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
    self.namespace = self.namespace[:-len(name) - 1]
    return node

def overload(function, args_types):
    pass

@visitor
def ret(self, tree: _ast.Return):
    val = self.visit(tree.value)
    self.variables[self.namespace]['type'].ret_type = val.type
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
        }
    )
    self.nl -= 1
    return body

@visitor
def _nonlocal(self, tree: _ast.Nonlocal):
    for name in tree.names:
        full_name = f'{self.namespace}.{name}'
        self.variables.update({
            full_name: self.variables[f'{self.previous_ns()}.{name}']
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
    for _name in tree.names:
        full_name = f'{self.namespace}.{_name}'
        self.variables.update({
            full_name: self.variables[f'__main__.{_name}']
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
