import _ast
from Basic import basic_element
from Basic.conf import configurator


config=configurator.conf_get("Basic/conf/js.cc")

def expr(expression):
    return basic_element.parser(expression.value)+";"

def assign(expression):
    source=basic_element.parser(expression.value)
    to=basic_element.parser(expression.targets[0])
    return eval(config.get("assign"))

def _if(tree):
    condition=basic_element.parser(tree.test)
    body=statement_block(tree.body)
    els=""
    if tree.orelse != []:
        els=_else(tree.orelse)
    return eval(config.get("if"))

def _while(tree):
    condition=basic_element.parser(tree.test)
    body=statement_block(tree.body)
    els=""
    if tree.orelse != []:
        els=_else(tree.orelse)
    return eval(config.get("while"))

def _for(tree):
    print(basic_element.data_struct(tree.iter)+".forEach(function("+basic_element.parser(tree.target)+"){")
    crawler(tree.body)
    print("});", end="")

def _else(tree):
    return eval(config.get("els"))

def define_function(tree):
    param=basic_element.args(tree.args.args)
    name=tree.name
    body=statement_block(tree.body)
    return eval(config.get("def_func"))

def ret(expression):
    print("return "+basic_element.parser(expression.value))

def statement_block(body):
    return "{\n" + "".join(list(map(block_parser, body))) + "}"

blocks={_ast.Assign:assign,
    _ast.Expr:expr,
    _ast.If:_if,
    _ast.While:_while,
    _ast.For:_for,
    _ast.FunctionDef:define_function,
    _ast.Return:ret
}

def block_parser(st):
    return blocks.get(type(st))(st)+"\n"

def crawler(body):
    for i in body:
        print(block_parser(i), end="")