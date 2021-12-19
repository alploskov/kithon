def side_effect(macro, parts):
    if 'side_effect' in macro:
        exec(
            macro['side_effect'],
            side_effects | parts
        )

def set_el_type(obj, _type='None'):
    if 'own' in obj.parts:
        obj.env.variables[obj.parts['own']]['type'].el_type = _type
    obj.type.el_type = _type

def set_type(obj, _type='None'):
    if 'own' in obj.parts:
        obj.env.variables[obj.parts['own']] = _type
    obj.type = _type


def set_as_mut(obj):
    obj.env.variables[obj.own]['immut'] = False

side_effects = {
    'set_el_type': set_el_type,
    'set_as_mut': set_as_mut,
    'set_type': set_type
}
