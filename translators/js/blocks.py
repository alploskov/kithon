from transPYler import handler
from transPYler import blocks


@handler("expr")
def expr(value):
    return value+";"

@handler("assign")
def assign(var, value):
    return f"{var} = {value};"

@handler("new_var")
def new_var(var, value):
    return f"var {var} = {value};"

@handler("ann_assign")
def ann_assign(var, _type, value=""):
    return new_var(var, value)

@handler("if")
def _if(compare, body, els):
    return f"if({compare}){body}{els}"

@handler("while")
def _while(compare, body, els):
    return f"while({compare}){body}"

@handler("else")
def _else(body):
    return f"else{body}"

@handler("else_if")
def else_if(_if):
    return "else "+_if

@handler("def")
def _def(name, args, body, ret_t=""):
    args = ', '.join(args)
    return f"function {name}({args}){body}"

@handler("return")
def ret(value):
    return f"return {value}"

@handler("for")
def _for(var, obj, body):
    step = var*2
    return f"for(var {step}=0, {var}={obj}[0]; {step}<{obj}.length;{var}={obj}[++{step}]){body}"

@handler("c_like_for")
def c_like_for(var, body, param):
    start, finish, step = param
    return f"for(var {var} = {start}; {var} < {finish}; {var}+={step}){body}"

@handler("statement_block")
def statement_block(body):
    tab = '\n'+'    '*blocks.nesting_level
    end = ('\n'+'    '*(blocks.nesting_level-1))+'}'
    return "{"+tab + tab.join(body)+end
