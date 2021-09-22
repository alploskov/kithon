import ast
import _ast
from .types import List


def getvar(self, name: str):
    return self.variables.get(
        f'{self.namespace}.{name}',
        self.variables.get(
            f'{self.namespace[:self.namespace.rfind(".")]}.{name}',
            self.variables.get(
                f'main.{name}'
            )
        )
    )

def types_to_id(types):
    _id = ''
    for i in types:
        _id += f'_{str(i)}'
    return _id

def is_var_created(core,name):
    return name in core.variables.get(core.namespace)

def element_type(el):
    _type = el.type
    if type(_type) == List:
        return _type.el_type
    return _type

def transpyler_type(el):
    if el == 'any':
        return el
    return {List: 'List'}.get(type(el.type), el.type)
