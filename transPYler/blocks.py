import _ast
from transPYler.expressions import parser

def expr(expression, handler):
    value = parser(expression.value)
    return handler(value)


def assign(expression, handler):
    value = parser(expression.value)
    var = parser(expression.targets[0])
    return handler(var, value) 


def _if(tree, handler):
    condition = parser(tree.test)
    body = statement_block(tree.body, blocks_handlers.get("statement_block"))
    els = ""
    if tree.orelse != []:
        els = _else(tree.orelse, blocks_handlers.get("else"))
    return handler(condition, body, els)


def _while(tree):
    condition = parser(tree.test)
    body = statement_block(tree.body)
    els = ""
    if tree.orelse != []:
        els = _else(tree.orelse)
    return handler(condition, body, els)


def _for(tree):
    print(basic_element.data_struct(tree.iter) + ".forEach(function(" + basic_element.parser(tree.target) + "){")
    crawler(tree.body)
    print("});", end="")


def _else(tree, handler): 
    if type(tree[0]) == _ast.If:
        body = else_if(tree[0], blocks_handlers.get("else_if")) 
    else:
        body = handler(statement_block(tree, blocks_handlers.get("statement_block")))
        
    return body

def else_if(tree, handler):
    return handler(_if(tree, blocks_handlers.get(_ast.If)))

def define_function(tree, handler):
    param = basic_element.args(tree.args.args)
    name = tree.name
    
    body = statement_block(tree.body)
    return handler(name, param, body)


def ret(expression):
    print("return " + basic_element.parser(expression.value))

nesting_level = 0
def statement_block(body, handler):
    global nesting_level
    nesting_level += 1
    body =  handler(list(map(block_parser, body)), nesting_level)
    nesting_level -= 1
    return body

blocks = {_ast.Assign: assign,
          _ast.Expr: expr,
          _ast.If: _if,
          _ast.While: _while,
          _ast.For: _for,
          _ast.FunctionDef: define_function,
          _ast.Return: ret
}

blocks_handlers = {}

def block_parser(st):
    _type = type(st)
    return blocks.get(_type)(st, blocks_handlers.get(_type))


def crawler(body):
    for i in body:
        print(block_parser(i))
