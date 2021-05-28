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
    if _type.startswith('set') or _type.startswith('list') or _type.startswith('tuple'):
        return re.search(r'\<.*\>', _type).group()[1:-1]
    return _type

def transpyler_type(el):
    _type = el.get('type')
    if not(_type):
        return 'None'
    if _type.startswith('set') or _type.startswith('list') or _type.startswith('tuple') or _type.startswith('dict'):
        return _type[:_type.find('<')]
    return _type
