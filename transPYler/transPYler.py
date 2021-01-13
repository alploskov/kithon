import ast
import _ast
import re


########################################################################
#                           exprs                                      #
#                                                                      #
########################################################################

def get_val(i): #for macros and st func
    if type(i) == _ast.Constant:
        val = i.value
        if type(val) == str:
            val = '"'+val+'"'
        val = str(val)
    else:
        val = parser(i).get('val')
    return val

def operator_overloading(left, right, op):
    l_type = type_parse(left.get('type'))
    r_type = type_parse(right.get('type')) 
    handler = operator_overloading_data.get((l_type, r_type, op))
    return handler(left, right)

def auto_type(l_type, r_type, op):
    if (l_type, r_type, op) in type_by_op:
        return type_by_op.get((l_type, r_type, op))
    return 'None'

def type_parse(_type):
    _type = str(_type)
    if re.match(r'list\[.+\]', _type):
        return "list"
    return _type
        
def bin_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = get_sign(tree.op)
    
    l_type = type_parse(left.get('type'))
    r_type = type_parse(right.get('type'))
    if (l_type, r_type, op) in operator_overloading_data:
        return operator_overloading(left, right, op)
    
    _type = auto_type(left.get("type"), right.get("type"), op)
    if callable(op):
        val = op(left, right)
    else:
        handler = handlers.get("bin_op")
        val = handler(left.get("val"), right.get("val"), op)
    return {"type": _type, "val": val}

def bool_op(tree):
    """Logic operation(or, and)"""
    handler = handlers.get("bool_op")
    els = list(map(parser, tree.values))
    op = get_sign(tree.op)
    return handler(els, op)

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    handler = handlers.get("compare")
    els = [parser(tree.left).get('val')]
    els += list(map(lambda a: parser(a).get('val'), tree.comparators))
    ops = list(map(get_sign, tree.ops))
    return {"type": 'bool', 'val': handler(els, ops)}

def un_op(tree):
    """unary operations(not)"""
    handler = handlers.get("un_op")
    op = get_sign(tree.op)
    el = parser(tree.operand)
    return {'type': el.get('type'),
            'val': handler(op, el.get('val'))
            }

def arg(tree):
    handler = handlers.get("arg")
    name = tree.arg
    if tree.annotation:
        return handler(name, type=parser(tree.annotation))
    return handler(name)

def attribute(tree):
    handler = handlers.get("attr")
    obj = parser(tree.value)
    attr_name = tree.attr
    if obj.get('val') in lib:
        l = lib.get(obj.get('val'))
        obj = l.get("__name__")
        attr_name = l.get(attr_name)
    else:
        obj = obj.get('val')
    return {'type': 'None', 'val': handler(obj, attr_name)}

def function_call(tree):
    handler = handlers.get("call")
    if type(tree.func) == _ast.Attribute:
        name = attribute(tree.func).get('val')
    else:
        name = tree.func.id    
    if name in a_func:
        name = a_func.get(name)
        if callable(name):                
            param = str(tuple(map(get_val, tree.args)))
            return {'type': 'None', 'val': eval(f"name{param}")}
    args = list(map(lambda a: parser(a).get('val'), tree.args))
    ret_type = 'None'
    return {"type": ret_type, "val": handler(name, args)}


def _list(tree):
    handler = handlers.get("list")
    elements = list(map(parser, tree.elts))
    els = list(map(lambda a: a.get('val'), elements))
    if len(elements):
        _type = elements[0].get('type')
    else:
        _type = 'None'
    return {"type": f"list[{_type}]", "val": handler(els, _type)}

def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Index:
        index = parser(sl.value).get('val')
        handler = handlers.get("index")
        val = handler(arr.get('val'), index)
        if re.search(r'\[.+\]', arr.get('type')):
            _type = re.search(r'\[.+\]', arr.get('type')).string[1:-1]
        else:
            _type = arr.get('type')
        return {"type": _type, "val": val}
    elif type(sl) == _ast.Slice:
        handler = handlers.get("slice")
        lower = parser(sl.lower).get('val')
        upper = parser(sl.upper).get('val')
        step = parser(sl.step).get('val')
        val = handler(arr.get('val'), lower, upper, step)
        return {"type": arr.get('type'), "val": val}

def name(tree):
    handler = handlers.get("name")
    name = tree.id
    _type = str(created_variables.get(namespace).get(name))
    return {"type": _type, "val": handler(name)}

def const(tree):
    val = tree.value
    if type(val) == str:
        handler = handlers.get("string")
        return {"type": 'str', "val": handler(val)}
    handler = handlers.get("const")
    _type = str(type(val)).replace("<class '", "").replace("'>", "")
    return {"type": _type, "val": handler(str(val))}


function_analog_func = {}
lib = {}
signs = {}
get_sign = lambda op: signs.get(type(op))
operator_overloading_data = {} 
type_by_op = {}

########################################################################
#                           blocks                                     #
#                                                                      #
########################################################################

def expr(expression):
    handler = handlers.get("expr")
    value = parser(expression.value).get("val")
    return handler(value)

def assign(expression):
    value = parser(expression.value)
    var = parser(expression.targets[0])
    _type = value.get("type")
    if type(expression.targets[0]) == _ast.Name: # Могут быть изменения массивов (a[0] = 1)
        if not (var.get('val') in created_variables.get(namespace).keys()):
            created_variables.get(namespace).update({var.get('val'): _type})
            handler = handlers.get("new_var")
            return handler(var.get('val'), value.get('val'))
    handler = handlers.get("assign")
    return handler(var.get('val'), value.get('val'))

def ann_assign(expression):
    handler = handlers.get("ann_assign")
    var = parser(expression.target)
    _type = expression.annotation.id
    created_variables.get(namespace).update({var: _type})
    if expression.value:
        val = parser(expression.value)
        return handler(var, _type, val=val)
    return handler(var, _type)

def aug_assign(expr):
    targets = [expr.target]
    value = ast.BinOp(left=expr.target, op=expr.op, right=expr.value) 
    return assign(ast.Assign(targets=targets, value=value))

def _if(tree):
    handler = handlers.get("if")
    condition = parser(tree.test).get('val')
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
    pass

def _for(tree):
    var = parser(tree.target)
    body = statement_block(tree.body)
    if type(tree.iter) == _ast.Call:
        if tree.iter.func.id == "range":
            if "c_like_for" in handlers:
                param = list(map(get_val, tree.iter.args))
                if len(param) < 3:
                    param.append("1")
                if len(param) < 3:
                    param.insert(0, "0")
                handler = handlers.get("c_like_for")
                return handler(var.get('val'), body, param)
    handler = handlers.get("for")
    obj = parser(tree.iter)
    return handler(var.get('val'), obj.get('val'), body)

def define_function(tree):
    handler = handlers.get("def")
    args = list(map(parser, tree.args.args))
    name = tree.name
    global namespace
    namespace += f".{name}"
    if not (namespace in created_variables.keys()):
        created_variables.update({namespace: {}})
    body = statement_block(tree.body)
    ".".join(namespace.split(".")[:-1])
    if tree.returns:
        ret_t = parser(tree.returns)
        return handler(name, args, body, ret_t=ret_t)
    return handler(name, args, body)

def ret(expression):
    handler = handlers.get("return")
    return handler(parser(expression.value).get('val'))

def statement_block(body):
    handler = handlers.get("statement_block")
    global nesting_level
    nesting_level += 1
    body = handler(list(map(parser, body)), nesting_level)
    nesting_level -= 1
    return body

def scope_of_view(tree):
    created_variables.get(namespace).update(tree.names)
    return None


nesting_level = 0

elements = {_ast.Call: function_call,
            _ast.BinOp: bin_op,
            _ast.BoolOp: bool_op,
            _ast.Compare: compare,
            _ast.List: _list,
            _ast.Attribute: attribute,
            _ast.Name: name,
            _ast.Subscript: slice,
            _ast.Constant: const,
            _ast.arg: arg,
            _ast.UnaryOp: un_op,
            type(None): lambda t: {'type': 'None',
                                   'val': 'None'
                                   },
            _ast.Assign: assign,
            _ast.AnnAssign: ann_assign,
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

parser = lambda el: elements.get(type(el))(el)
namespace = "main"
created_variables = {"main": {}}
handlers = {}

def crawler(body):
    strings = []
    for i in body:
        i = parser(i)
        print(i)
        if i:
            strings.append(i)
    return "\n".join(strings)
