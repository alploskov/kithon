import ast
import _ast
import re


def element_type(el):
    _type = el.get('type')
    if _type.startswith('set') or _type.startswith('list') or _type.startswith('tuple'):
        return re.search(r'\<.*\>', _type).group()[1:-1]

def transpyler_type(el):
    _type = el.get('type')
    if _type.startswith('set') or _type.startswith('list') or _type.startswith('tuple') or _type.startswith('dict'):
        return _type[:_type.find('<')]
    return _type
