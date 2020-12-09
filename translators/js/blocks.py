def expr(value):
    return value+";"

def assign(var, value):
    return f"{var} = {value};"

def _if(compare, body, els):
    return f"if({compare}){body}\n{els}"

def _while():
    return f"if({compare}){body}{els}"

def _else(body):
    return f"else{body}"

def else_if(_if):
    return "else "+_if

def statement_block(body, nesting_level):
    tab = '\n'+'    '*nesting_level
    last_tab = '\n'+'    '*(nesting_level-1)
    return "{"+tab + tab.join(body)+last_tab+"}"
