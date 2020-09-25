import _ast
from Basic import basic_element


def expr(expression):
    print(basic_element.parser(expression.value)+";")

def assign(expression):
    print(f"{basic_element.parser(expression.targets[0])} = {basic_element.parser(expression.value)};")

def _if(tree):
    print("if("+str(basic_element.parser(tree.test))+"){")
    crawler(tree.body)
    print("}")
    if tree.orelse!=[]:
        _else(tree.orelse)

def _while(tree):
    print("while("+str(basic_element.parser(tree.test))+"){")
    crawler(tree.body)
    print("}")

def _for(tree):
    print(basic_element.data_struct(tree.iter)+".forEach(function("+basic_element.parser(tree.target)+"){")
    crawler(tree.body)

    print("});", end="")

def _else(tree):
    print("else", end="")
    if type(tree[0])==_ast.If:
        print(" ", end="")
        _if(tree[0])
    else:
        print("{")
        crawler(tree)
        print("}")

blocks={_ast.Assign:assign,
    _ast.Expr:expr,
    _ast.If:_if,
    _ast.While:_while,
    _ast.For:_for
}

def crawler(body):
    for i in body:
        blocks.get(type(i))(i)