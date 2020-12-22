import uuid


def expr(value):
    return value+";"

def assign(var, value):
    return f"{var} = {value};"

def aug_assign(var, op, value):
    return f"{var} {op}= {value};"

def _if(compare, body, els):
    return f"if({compare}){body}\n{els}"

def _while(compare, body, els):
    return f"while({compare}){body}"

def _else(body):
    return f"else{body}"

def else_if(_if):
    return "else "+_if

def def_f(name, args, body):
    return f"function {name}({args}){body}"

def ret(value):
    return f"return {value}"

def _for(var, obj, body):
    step = f"step{str(uuid.uuid4())[:8]}"
    return f"for(var {step}=0, {var}={obj}[0]; {step}<{obj}.length;{var}={obj}[++{step}]){body}"

def c_like_for(var, body, start, finish, step):
    return f"for(var {var} = {start}; {var} < {finish}; {var}+={step}){body}"

def statement_block(body, nesting_level):
    tab = '\n'+'    '*nesting_level
    last_tab = '\n'+'    '*(nesting_level-1)
    return "{"+tab + tab.join(body)+last_tab+"}"
