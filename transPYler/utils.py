import ast
import _ast
from . import core


def is_var_created(name):
    return name in core.variables.get(core.namespace)

def add_var(name, _type):
    core.variables.get(core.namespace).update({name: _type})

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
