from .types import List


side_effects = {}
def side_effect(func):
    side_effects.update({
        func.__name__: func
    })
    return func

@side_effect
def set_el_type(obj, _type='None'):
    obj_type = obj.env.variables[obj.parts['own']]
    if isinstance(obj_type, List) and el_type(obj_type) == 'generic':
        obj.env.variables[obj.parts['own']].el_type = _type
    obj.type = _type

@side_effect
def set_as_mut(obj):
    obj.env.variables[obj.parts['own']]['mut'] = True

