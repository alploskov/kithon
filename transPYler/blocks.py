import _ast
from .core_data import handlers, namespace, created_variables, Parser
from .expressions import parser


def expr(expression):
    handler = handlers.get("expr")
    value = parser(expression.value).get("val")
    return handler(value)

def assign(expression):
    value = parser(expression.value)
    var = parser(expression.targets[0])
    if type(expression.targets[0]) == _ast.Name: # Могут быть изменения массивов (a[0] = 1)
        if not (var in created_variables.get(namespace)):
            created_variables.get(namespace).update({name: _type})
            handler = handlers.get("new_var")
            return handler(var, value)
    handler = handlers.get("assign")
    return handler(var, value)

def ann_assign(expression):
    handler = handlers.get("ann_assign")
    var = parser(expression.target)
    _type = parser(expression.annotation)
    created_variables.get(namespace).update({var: _type})
    if expression.value:
        val = parser(expression.value)
        return handler(var, _type, val=val)
    return handler(var, _type)

def aug_assign(expression):
    pass

def _if(tree):
    pass

def _else(tree):
    pass

def else_if(tree):
    pass

def _while(tree):
    pass

def _for(tree):
    pass

def define_function(tree):
    pass

def ret(expression):
    pass

def statement_block(body):
    pass

def scope_of_view(tree):
    created_variables.get(namespace).extend(tree.names)
    return None


nesting_level = 0

elements = {_ast.Assign: assign,
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
}
b_parser = Parser(elements).parser


def crawler(body):
    strings = []
    for i in body:
        i = b_parser(i)
        if i:
            strings.append(i)
    return "\n".join(strings)
