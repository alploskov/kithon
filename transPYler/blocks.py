import ast
import _ast
from transPYler import expressions as ex
from transPYler.expressions import parser 


def expr(expression):
    handler = blocks_handlers.get("expr")
    value = parser(expression.value)
    return handler(value)

def assign(expression):
    handler = blocks_handlers.get("assign")
    value = parser(expression.value)
    var = parser(expression.targets[0])
    return handler(var, value) 

def aug_assign(expression):
    handler = blocks_handlers.get("aug_assign")
    var = parser(expression.target)
    op = ex.get_sign(expression.op)
    value = parser(expression.value)
    return handler(var, op, value)
    
def _if(tree):
    handler = blocks_handlers.get("if")
    condition = parser(tree.test)
    body = statement_block(tree.body)
    els = ""
    if tree.orelse != []:
        els = _else(tree.orelse)
    return handler(condition, body, els)

def _else(tree): 
    if type(tree[0]) == _ast.If:
        body = else_if(tree[0]) 
    else:
        handler = blocks_handlers.get("else")
        body = handler(statement_block(tree))
        
    return body

def else_if(tree):
    handler = blocks_handlers.get("else_if")
    return handler(_if(tree))

def _while(tree):
    handler = blocks_handlers.get("while")
    condition = parser(tree.test)
    body = statement_block(tree.body)
    els = ""
    if tree.orelse != []:
        els = _else(tree.orelse)
    return handler(condition, body, els)

def _for(tree):
    var = parser(tree.target)
    body = statement_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in blocks_handlers:
                param = list(map(parser, tree.iter.args))
                if len(param) < 3:
                    param.append("1")
                    if len(param)<3:
                        param.insert(0, "0")
                handler = blocks_handlers.get("c_like_for")
                return handler(var, body, param[0], param[1], param[2])
    handler = blocks_handlers.get("for")
    obj = parser(tree.iter)
    return handler(var, obj, body)
    
def define_function(tree):
    handler = blocks_handlers.get("def")
    args = ex.args(tree.args.args)
    name = tree.name    
    body = statement_block(tree.body)
    return handler(name, args, body)


def ret(expression):
    handler = blocks_handlers.get("return")
    return handler(parser(expression.value))

nesting_level = 0
def statement_block(body):
    handler = blocks_handlers.get("statement_block")
    global nesting_level
    nesting_level += 1
    body =  handler(list(map(block_parser, body)), nesting_level)
    nesting_level -= 1
    return body

blocks = {_ast.Assign: assign,
          _ast.Expr: expr,
          _ast.AugAssign: aug_assign,
          _ast.If: _if,
          _ast.While: _while,
          _ast.For: _for,
          _ast.FunctionDef: define_function,
          _ast.Return: ret
}

blocks_handlers = {}

def block_parser(st):
    _type = type(st)
    return blocks.get(_type)(st)


def crawler(body, out_file):
    for i in body:
        print(block_parser(i), file=out_file)
