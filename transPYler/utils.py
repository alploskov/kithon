import ast
import _ast
import re
from . import core


def is_var_created(name):
    return name in core.variables.get(core.namespace)

def add_var(name, _type):
    core.variables.get(core.namespace).update({name: _type})

def element_type(el):
    _type = el.get('type')
    if type(_type) == dict:
        return _type.get('el_type')
    return _type

def transpyler_type(el):
    _type = el.get('type')
    if not(_type):
        return 'None'
    elif type(_type) == type:
        return re.search(r'\'.*\'', str(_type)).group()[1:-1]
    elif 'base_type' in _type:
        return transpyler_type({'type':_type.get('base_type')})
