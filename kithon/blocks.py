import ast
import typing
import _ast
from .types import types
from .core import visitor


@visitor
def expr(self, tree: _ast.Expr):
    return self.node(
        tmp='expr',
        parts={'value': self.visit(tree.value)}
    )

def set_var(self, var, _type='any'):
    """
    returns True if var is new, otherwise returns False
    """
    if isinstance(var.ast, _ast.Name):
        var.own = f'{self.namespace}.{var.ast.id}'
    elif isinstance(var.ast, _ast.Subscript):
        own = var.own.removesuffix('.[]')
        if hasattr(self.variables.get(own, {}).get('type'), 'el_type'):
            self.variables[own]['type'].el_type = _type
        self.new_var(var.own, _type)
    if var.own in self.variables:
        self.variables[var.own]['immut'] = False
        if (
            self.variables[self.namespace]['type'] != 'type'
            and 'static' in self.variables[var.own]
        ):
            self.variables[var.own]['static'] = False
        return False
    self.new_var(var.own, _type)
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
        _ast.Subscript: 'key_assign',
        _ast.Attribute: 'set_attr'
    }.get(type(var.ast))
    if set_var(self, var, _type):
        if tmp == 'assign':
            tmp = 'new_var'
        elif tmp == 'set_attr':
            tmp = 'new_attr'
    if self.variables[self.namespace]['type'] == 'type':
        self.variables[var.own]['static'] = True
        tmp = 'static_attr'
    if not self.templates.get(tmp, {}).get('tmp'):
        tmp = 'assign'
    return self.node(
        tmp=tmp,
        name='assign',
        type=_type,
        parts={
            'var': var,
            'value': value,
            'own': var.own
        }
    )

@visitor
def var_prototype(self, tree: typing.Any):
    set_var(self, self.visit(ast.Name(id=tree, ctx=ast.Store)))
    return self.node(
        tmp='var_prototype',
        parts={'name': tree}
    )

def unpack(self, _vars, value):
    vars_names = _vars.parts['ls']
    is_new = 0
    _type = None
    if value.type == 'str':
        _type = 'str'
    elif isinstance(value.type, str):
        _type = 'any'
    elif isinstance(value.type, types['list']):
        _type = value.type.el_type
    elif isinstance(value.type, types['dict']):
        _type = value.type.key_type
    for pos, var in enumerate(vars_names):
        is_new += set_var(self,
            var, _type or value.type.els_types[pos]
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
        )
    ))

@visitor
def _if(self, tree: _ast.If, is_elif=False):
    return self.node(
        tmp = 'elif' if is_elif else 'if',
        parts={
            'condition': self.visit(tree.test),
            'body': expression_block(self, tree.body),
            'els': _else(self, tree.orelse)
        }
    )

@visitor
def _else(self, tree: typing.Any):
    if not tree:
        return ''
    if isinstance(tree[0], _ast.If):
        return _if(self, tree[0], is_elif=True)
    return self.node(
        tmp='else',
        parts={
            'body': expression_block(self, tree),
        }
    )

@visitor
def _while(self, tree: _ast.While):
    return self.node(
        tmp = 'while',
        parts={
            'condition': self.visit(tree.test),
            'body': expression_block(self, tree.body),
        }
    )

@visitor
def _for(self, tree: _ast.For):
    obj = self.visit(tree.iter)
    if (
        getattr(obj.parts.get('func'), 'parts', {}).get('name') == 'range'
        and 'c_like_for' in self.templates
    ):
        tmp = 'c_like_for'
        _type = 'int'
        if len(obj.parts['args']) < 3:
            obj.parts['args'].append(self.visit(
                ast.Constant(value=1)
            ))
        if len(obj.parts['args']) < 3:
            obj.parts['args'].insert(0, self.visit(
                ast.Constant(value=0)
            ))
        parts = {
            'start':  obj.parts['args'][0],
            'finish': obj.parts['args'][1],
            'step':   obj.parts['args'][2]
        }
    else:
        tmp = 'for'
        _type = getattr(obj.type, 'el_type', 'any')
        parts = {'obj': obj}
    var = self.visit(tree.target)
    self.new_var(var.own, _type)
    return self.node(
        tmp = tmp,
        parts={
            'var': var,
            'body': expression_block(self, tree.body)
        } | parts
    )

def decorating(self, decorators):
    if len(decorators) == 0:
        return {}
    return self.get_macro(
        decorators[0].own,
        decorators[0].type
    )[0]

@visitor
def args(self, tree: _ast.arg, in_class=False):
    _args = []
    for i, arg in enumerate(tree):
        full_name = f'{self.namespace}.{arg.arg}'
        if i == 0 and in_class:
            self.variables.update({
                full_name: self.variables[
                    self.previous_ns()
                ] | {'type': self.previous_ns()}
            })
        else:
            self.new_var(
                full_name,
                getattr(
                    self.visit(arg.annotation).type,
                    '__type__', 'any'
                )
            )
        _args.append(self.node(
            tmp='arg',
            type=self.variables[full_name]['type'],
            parts={'name': arg.arg}
        ))
    return _args

@visitor
def define_function(self, tree: _ast.FunctionDef):
    parts = {}
    in_class = self.variables[self.namespace]['type'] == 'type'
    if in_class:
        parts = {'class_name': self.namespace.split('.')[-1]}
        if tree.name == '__init__':
            tmp = 'init'
        else:
            tmp =  'method'
    else:
        tmp = 'func'
    self.namespace += f'.{tree.name}'
    _args = self.args(tree.args.args, in_class=in_class)
    decorators = list(map(self.visit, tree.decorator_list))
    macro = decorating(self, decorators)
    self.new_var(
        self.namespace,
        types['func'](
            tuple(map(lambda a: a.type, _args)),
            getattr(tree.returns, 'id', 'None')
        )
    )
    func = self.node(
        tmp=macro.get('decorate', tmp),
        name=tmp,
        own=self.namespace,
        parts={
            'name': tree.name,
            'args': _args,
            'body': expression_block(self, tree.body),
            'decorators': decorators,
            'ret_type': self.variables[self.namespace]['type'].ret_type
        } | parts
    )
    self.namespace = self.previous_ns()
    return func

@visitor
def ret(self, tree: _ast.Return):
    val = self.visit(tree.value)
    self.variables[self.namespace]['type'].ret_type = val.type
    return self.node(
        tmp='return',
        parts={'value': val}
    )

@visitor
def define_class(self, tree: _ast.ClassDef):
    self.namespace += f'.{tree.name}'
    self.new_var(self.namespace, 'type')
    body = expression_block(self, tree.body)
    attrs = {}
    for attr in body.parts['vars']:
        _var = self.variables[attr]
        if ('.' not in _var['own'].removeprefix(self.namespace + '.')
            and not isinstance(_var['type'], types['func'])
        ):
            attrs |= {
                _var['own'].split('.')[-1]: str(_var['type'])
            }
    decorators = list(map(self.visit, tree.decorator_list))
    macro = decorating(self, decorators)
    node = self.node(
        tmp=macro.get('decorate', 'class'),
        name='class',
        parts={
            'name': tree.name,
            'body': body,
            'init': next(filter(
                lambda m: m.name == 'init',
                body.parts['body']
            ), ''),
            'attrs': attrs,
            'methods': list(filter(
                lambda m: m.name == 'method',
                body.parts['body']
            )),
            'decorators': decorators
        }
    )
    self.namespace = self.previous_ns()
    return node

@visitor
def expression_block(self, tree: typing.Any):
    self.nl += 1
    vars = set(self.variables.keys())
    body = self.node(
        tmp='body',
        parts={
            'body': list(map(self.visit, tree)),
            'vars': list(set(self.variables.keys()) - vars)
        }
    )
    self.nl -= 1
    return body

@visitor
def _import(self, tree: _ast.Import):
    name = tree.names[0].name
    alias = tree.names[0].asname
    macro = self.templates.get(name, {})
    self.variables.update({
        (self.namespace + '.' + (alias or name)): {
            'own': name,
            'type': types['module'](name)
        }
    })
    return self.node(
        tmp=macro.get('import_code', 'import'),
        name='import',
        parts={
            'name': macro.get('alt_name', name),
            'alias': alias or macro.get('alt_name', name)
        }
    )

@visitor
def import_from(self, tree: _ast.ImportFrom):
    name = tree.names[0].name
    alias = tree.names[0].asname
    macro = self.templates.get(f'{tree.module}.{name}', {})
    own = tree.module + '.' + name
    self.variables.update({
        (self.namespace + '.' + (alias or name)): {
            'own': own,
            'type': macro.get('type', 'any')
        }
    })
    return self.node(
        tmp=macro.get('import_code', 'import_from'),
        name='import_from',
        parts={
            'module': tree.module,
            'name': macro.get('alt_name', name),
            'alias': alias or macro.get('alt_name', name)
        }
    )

@visitor
def _nonlocal(self, tree: _ast.Nonlocal):
    vars = []
    for name in tree.names:
        full_name = f'{self.namespace}.{name}'
        self.variables.update({
            full_name: self.variables[
                f'{self.previous_ns()}.{name}'
            ]
        })
        vars.append(self.visit(ast.Name(
            id=name, ctx=ast.Load
        )))
    return self.node(
        tmp='nonlocal',
        parts={'vars': vars}
    )

@visitor
def _global(self, tree: _ast.Global):
    vars = []
    for name in tree.names:
        full_name = f'{self.namespace}.{name}'
        self.variables.update({
            full_name: self.variables[f'__main__.{name}']
        })
        vars.append(self.visit(ast.Name(
            id=name, ctx=ast.Load
        )))
    return self.node(
        tmp='global',
        parts={'vars': vars}
    )

@visitor
def _break(self, tree: _ast.Break):
    return self.node(tmp='break')

@visitor
def _continue(self, tree: _ast.Continue):
    return self.node(tmp='continue')
