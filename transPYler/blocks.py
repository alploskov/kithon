import _ast
from transPYler.expressions import get_sign, parser


def expr(expression):
    handler = handlers.get("expr")
    value = parser(expression.value)
    return handler(value)

def assign(expression):
    value = parser(expression.value)
    var = parser(expression.targets[0])
    if not (var in created_variables.get(namespace)):
        created_variables.get(namespace).append(var)
        handler = handlers.get("new_var")
        return handler(var, value)
    handler = handlers.get("assign")
    return handler(var, value)

def aug_assign(expression):
    handler = handlers.get("aug_assign")
    var = parser(expression.target)
    op = get_sign(expression.op)
    value = parser(expression.value)
    return handler(var, op, value)

def _if(tree):
    handler = handlers.get("if")
    condition = parser(tree.test)
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
    handler = handlers.get("while")
    condition = parser(tree.test)
    body = statement_block(tree.body)
    els = ""
    if tree.orelse:
        els = _else(tree.orelse)
    return handler(condition, body, els)

def _for(tree):
    var = parser(tree.target)
    body = statement_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in handlers:
                param = list(map(parser, tree.iter.args))
                if len(param) < 3:
                    param.append("1")
                    if len(param) < 3:
                        param.insert(0, "0")
                handler = handlers.get("c_like_for")
                return handler(var, body, param[0], param[1], param[2])
    handler = handlers.get("for")
    obj = parser(tree.iter)
    return handler(var, obj, body)

def define_function(tree):
    handler = handlers.get("def")
    args = list(map(parser, tree.args.args))
    name = tree.name
    global namespace
    namespace += f".{name}"
    if not (namespace in created_variables.keys()):
        created_variables.update({namespace: []})
    body = statement_block(tree.body)
    ".".join(namespace.split(".")[:-1])
    return handler(name, args, body)

def ret(expression):
    handler = handlers.get("return")
    return handler(parser(expression.value))

def statement_block(body):
    handler = handlers.get("statement_block")
    parser = lambda el: elements.get(type(el))(el)
    global nesting_level
    nesting_level += 1
    body = handler(list(map(parser, body)), nesting_level)
    nesting_level -= 1
    return body

def scope_of_view(tree):
    created_variables.get(namespace).extend(tree.names)
    return ""

handlers = {}
namespace = "main"
created_variables = {"main": []}
nesting_level = 0

elements = {_ast.Assign: assign,
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

def crawler(body):
    parser = lambda el: elements.get(type(el))(el)
    strings = list(map(parser, body))
    return "\n".join(strings)
