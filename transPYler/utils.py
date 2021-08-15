import ast
import _ast


def add_var(core, name, _type):
    core.variables.get(core.namespace).update({name: _type})

def is_var_created(core,name):
    return name in core.variables.get(core.namespace)

def element_type(el):
    _type = el.type
    if type(_type) == dict:
        return _type.get('el_type')
    return _type

def transpyler_type(el):
    _type = el.type
    if not(_type):
        return 'None'
    elif 'base_type' in _type:
        return _type.get('base_type')
    return _type
