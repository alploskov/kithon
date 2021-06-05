import _ast
import re
from . import core
from .utils import element_type, add_var, transpyler_type
from .core import parser, tmpls, objects, op_to_str, macros
from jinja2 import Template


def math_op(tree):
    """Math operation(+, -, *, /...)"""
    left = parser(tree.left)
    right = parser(tree.right)
    op = op_to_str(tree.op)
    return bin_op(left, right, op)     

def bool_op(tree):
    """Boolean logic operation(or, and)"""
    els = list(map(parser, tree.values))
    op = op_to_str(tree.op)
    expr = bin_op(els[0], els[1], op)
    for i in els[2:]:
        expr = bin_op(expr, i, op)
    return expr

def compare(tree):
    """Compare operation(==, !=, >, <, >=, <=...)"""
    f_el = parser(tree.left)
    els = list(map(parser, tree.comparators))
    ops = list(map(op_to_str, tree.ops))
    expr = bin_op(f_el, els[0], ops[0])
    for i in zip(els[:-1], els[1:], ops[1:]):
        expr = bin_op(expr, bin_op(i[0], i[1], i[2]), 'and')
    return expr

def bin_op(left, right, op):
    def auto_type(left, right, op):
        expr = (transpyler_type(left), transpyler_type(right), op)
        ex_data = [(expr[0], expr[1], expr[2]),
                   (expr[0], expr[1], 'any'),
                   (expr[0], 'any', expr[2]),
                   ('any', expr[1], expr[2]),
                   ('any', expr[1], 'any'),
                   ('any', 'any', expr[2]),
                   (expr[0], 'any', 'any'),
                   ('any', 'any', 'any'),
                   ]
        for i in ex_data:
            if i in core.type_facts:
                return core.type_facts.get(i)
        if op in ['and', 'or', '==', '!=', '>', '<', '>=', '<=', 'in', 'is']:
            return 'bool'
        return 'None'
    
    expr = (transpyler_type(left), transpyler_type(right), op)
    ex_data = [(expr[0], expr[1], expr[2]),
               (expr[0], expr[1], 'any'),
               (expr[0], 'any', expr[2]),
               ('any', expr[1], expr[2]),
               ('any', expr[1], 'any'),
               ('any', 'any', expr[2]),
               (expr[0], 'any', 'any'),
               ('any', 'any', 'any'),
               ]
    for i in ex_data:
        if ex := macros.get(i):
            if 'type' in ex:
                _type = Template(ex.get('type')).render(
                    l=left.get('val'),
                    r=right.get('val'),
                    l_type=left.get('type'),
                    r_type=right.get('type')
                )
            else:
                _type = auto_type(left, right, op)
            return {'val': Template(ex.get('code')).render(
                l=left.get('val'),
                r=right.get('val'),
                l_type=left.get('type'),
                r_type=right.get('type')
            ),
                    'type': _type
            }
    tmp = tmpls.get("bin_op")
    return {'type': auto_type(left, right, op),
            'val': tmp.render(left=left.get('val'),
                              right=right.get('val'),
                              op=tmpls.get('operations').get(op)
                              )
            }

def un_op(tree):
    """Unary operations(not...)"""
    tmp = tmpls.get("un_op")
    op = tmpls.get('operations').get(tree.op)
    el = parser(tree.operand)
    return {'type': el.get('type'), 'val': tmp.render(op=op, el=el.get('val'))}

def arg(tree):
    tmp = tmpls.get("arg")
    name = tree.arg
    if tree.annotation:
        t = tree.annotation.id
        add_var(name, t)
        _type = tmpls.get('types').get(t) if t in tmpls.get('types') else t
    else:
        t = ''
        _type = ''
        add_var(name, '')
    return {'type': t,
            'val': tmp.render(arg=name, _type=_type)}

def attribute(tree):
    obj = parser(tree.value)
    attr = tree.attr
    if (transpyler_type(obj) in objects) or (obj.get('val') in objects):
        if obj.get('val') in objects:
            object = obj.get('val')
        else:
            object = transpyler_type(obj)
        attrs = objects.get(object)
        if '__name__' in attrs.keys():
            obj = {'val': attrs.get('__name__')}
        attr = attrs.get(attr)
        if callable(attr):
            return {'type': 'None',
                    'obj': obj,
                    'macros': attr
                    }
        attr = attr.get('val')
    val = tmpls.get("attr").render(obj=obj.get('val'),
                                   attr_name=attr)
    return {'type': 'None', 'val': val}

def function_call(tree):
    tmp = tmpls.get("call")
    args = list(map(lambda a: parser(a).get('val'), tree.args))
    ret_type = 'None'
    if type(tree.func) == _ast.Attribute:
        attr = attribute(tree.func)
        if 'macros' in attr.keys():
            args.insert(0, attr.get('obj'))
            name = attr.get('macros')
            args = args[:1]+list(map(parser, args[1:]))
            args = str(tuple(args))
            return macro(name, args)
        else:
            name = attr.get('val')
    else:
        name = tree.func.id
        if name in macros:
            macro = macros.get(name)
            if 'type' in macro:
                ret_type = macro.get('type')
            if 'args' in macro:
                _args = macro.get('args')
            else:
                _args = [f'_{i}' for i in range(len(args))] 
            args = dict(zip(_args, args))
            if 'code' in macro:
                name = Template(macro.get('code'))
                return {"type": ret_type, "val": name.render(args=args)}
#    elif name in objects:
#        name = objects.get('__name__')
#        tmp = tmpls.get('init')
    return {"type": ret_type, "val": tmp.render(name=name, args=args)}

def _list(tree):
    tmp = tmpls.get("list")
    elements = list(map(parser, tree.elts))
    ls = list(map(lambda a: a.get('val'), elements))
    if len(elements) and 'types' in tmpls:
        t = elements[0].get('type')
        _type = str(tmpls.get('types').get(t))
    else:
        _type = 'None'
    return {"type": f'list<{_type}>', "val": tmp.render(ls=ls, _type=_type)}

def _dict(tree):
    pass

def slice(tree):
    arr = parser(tree.value)
    sl = tree.slice
    if type(sl) == _ast.Slice:
        tmp = tmpls.get("slice")
        lower = parser(sl.lower).get('val')
        upper = parser(sl.upper).get('val')
        step = parser(sl.step).get('val')
        val = tmp.render(arr=arr.get('val'), lower=lower, upper=upper, step=step)
        return {"type": arr.get('type'), "val": val}
    else:
        tmp = tmpls.get("index")
        index = parser(sl).get('val')
        val = tmp.render(arr=arr.get('val'), val=index)
        _type = element_type(arr)
        return {"type": _type, "val": val}

def name(tree):
    tmp = tmpls.get("name")
    name = tree.id
    _type = str(core.variables.get(core.namespace).get(name))
    return {"type": _type, "val": tmp.render(name=name)}

def const(tree):
    val = tree.value
    if type(val) == str:
        tmp = tmpls.get("string")
        return {"type": 'str', "val": tmp.render(val=val)}
    tmp = tmpls.get("const")
    _type = re.search(r'\'.*\'', str(type(val))).group()[1:-1]
    return {"type": _type, "val": tmp.render(val=str(val))}

core.elements |= {_ast.Call: function_call,
                  _ast.BinOp: math_op,
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
                                         'val': ''
                                         }
}
