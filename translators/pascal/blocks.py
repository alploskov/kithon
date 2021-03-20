from transPYler import handler
from transPYler import blocks


@handler("expr")
def expr(value):
    return value+';'

@handler("assign")
def assign(var, value):
    return f"{var} := {value};"

@handler("new_var")
def new_var(var, value):
    return f"{var} := {value};"

@handler("if")
def _if(compare, body, els):
    if els:
        return f"if {compare} then {body}\n{els}"
    else:
        return f"if {compare} then {body};"

@handler("else")
def _else(body):
    return f"else{body};"

@handler("else_if")
def else_if(_if):
    return "else "+_if

@handler("statement_block")
def statement_block(body):
    tab = '\n'+'    '*blocks.nesting_level
    end = ('\n'+'    '*(blocks.nesting_level-1))+'end'
    return "\nbegin"+tab + tab.join(body)+end
