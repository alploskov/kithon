from dataclasses import dataclass
import typing
from typing import Union
from jinja2 import Template


@dataclass
class List:
    el_type: Union[typing.Any, str] = 'any'
    def __str__(self):
        return f'list[{to_string(self.el_type)}]'

@dataclass
class Func:
    ret_type: Union[typing.Any, str] = 'any'
    def __str__(self):
        return f'func[{to_string(self.ret_type)}]'

class Dict():
    pass

@dataclass
class Module:
    name: str = ''

def to_string(_type):
    return getattr(_type, 'to_str', _type)

def type_render(self, _type):
    types = self.templates['types']
    if isinstance(_type, List):
        tmp = types.get('list')
        if tmp:
            return Template(tmp).render(
                el_type=type_render(
                    self,
                    _type.el_type
                )
            )
        return to_string(_type)
    return types.get(_type, _type)

def to_any(_type):
    if isinstance(_type, List):
        if _type.el_type == 'any':
            return 'any'
        return List(to_any(_type.el_type))
    return 'any'

def type_translation(_type):
    if _type.startswith('list[') and _type[-1] == ']':
        return List(type_translation(_type[5:-1]))
    return _type


def element_type(element):
    _type = element.type
    if isinstance(_type, List):
        return _type.el_type
    return _type
