from dataclasses import dataclass
import typing
from typing import Union
from jinja2 import Template


@dataclass
class List:
    el_type: Union[typing.Any, str] = 'any'
    def __str__(self):
        return f'list[{self.el_type}]'

@dataclass
class Func:
    ret_type: Union[typing.Any, str] = 'any'
    def __str__(self):
        return f'func[{to_string(self.ret_type)}]'

@dataclass
class Dict():
    pass

@dataclass
class Module:
    name: str = ''

@dataclass
class Type:
    name: str = ''
    def __str__(self):
        return 'type'

def to_string(_type):
    return getattr(_type, 'to_str', _type)

def type_render(self, _type):
    types_tmp = self.templates['types']
    if isinstance(_type, List):
        tmp = types_tmp.get('list')
        if tmp:
            return Template(tmp).render(
                el_type=type_render(
                    self,
                    _type.el_type
                )
            )
        return to_string(_type)
    elif isinstance(_type, Module):
        return _type.name
    elif isinstance(_type, Type):
        return types_tmp.get(_type.name, _type.name)
    return types_tmp.get(_type, _type)

def to_any(_type):
    if isinstance(_type, List):
        if _type.el_type == 'any':
            return 'any'
        return List(to_any(_type.el_type))
    return 'any'


def type_eval(type_code, parts):
    """
    Generate type by dict form config
    """
    _type = eval(
        type_code,
        types | parts | {'int': 'int'}
    ) or 'None'
    if isinstance(_type, type):
        _type = str(_type)[8:-2]
    return _type


def element_type(element):
    _type = element.type
    if isinstance(_type, List):
        return _type.el_type
    return _type

types = {'list': List, 'dict': Dict}
