import _ast

signs = {                                                                                                                                                            
    _ast.Add: "+",                                                                                                                                                   
    _ast.Mult: "*",                                                                                                                                                  
    _ast.Sub: "-",                                                                                                                                                   
    _ast.Div: "/",                                                                                                                                                   
    _ast.Eq: "==",                                                                                                                                                   
    _ast.NotEq: "!=",                                                                                                                                                
    _ast.Gt: ">",                                                                                                                                                    
    _ast.Lt: "<",                                                                                                                                                    
    _ast.GtE: ">=",                                                                                                                                                  
    _ast.LtE: "<=",                                                                                                                                                  
    _ast.And: "&&",                                                                                                                                                  
    _ast.Or: "|",                                                                                                                                                    
    _ast.BitAnd: "&",                                                                                                                                                
    _ast.BitOr: "|"                                            
}

def bin_op(left, right, sign):
    return f"{left} {sign} {right}"

handle_expr={_ast.BinOp: bin_op}

func={
    "print":"alert",
    "input":"prompt"
}
method={
    "len":".length",
    "append":".push"
}
