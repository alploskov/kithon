from dataclasses import dataclass
import typing
from typing import Union
from jinja2 import Template


@dataclass
class List:
    el_type: Union[typing.Any, str] = 'any'

    def __str__(self):
        return f'list[{self.el_type}]'

    def render(self, env):
        tmp = env.templates['types'].get('list')
        if tmp:
            return Template(tmp).render(
                el_type=type_render(env, self.el_type)
            )
        return str(self)
    def to_any(self):
        if self.el_type == 'any':
            return 'any'
        return List(to_any(self.el_type))

@dataclass
class Func:
    args: tuple[Union[typing.Any, str]] = ()
    ret_type: Union[typing.Any, str] = 'any'

    def __str__(self):
        return f'func[{self.args}]{self.ret_type}'

    def render(self, env):
        tmp = env.templates['types'].get('func')
        if tmp:
            return Template(tmp).render(
                args=tuple(map(lambda a: type_render(env, a), self.args)),
                ret_type=type_render(env, self.ret_type)
            )
        return str(self)

@dataclass
class Dict:
    key_type: Union[typing.Any, str] = 'generic'
    val_type: Union[typing.Any, str] = 'generic'

    def __str__(self):
        return f'dict[{self.key_type}]{self.val_type}'

    def render(self, env):
        tmp = env.templates['types'].get('dict')
        if tmp:
            return Template(tmp).render(
                key_type=type_render(env, self.key_type),
                val_type=type_render(env, self.val_type)
            )
        return str(self)

    def to_any(self):
        if self.key_type == self.val_type == 'any':
            return 'any'
        if self.val_type == 'any':
            return Dict(to_any(self.key_type), 'any')
        if self.key_type == 'any':
            return Dict('any', to_any(self.val_type))
        return Dict(self.key_type, to_any(self.val_type))

@dataclass
class Module:
    name: str = ''

    def __str__(self):
        return f'mod_{self.name}'

    def render(self, env):
        tmp = env.templates['types'].get('module')
        if tmp:
            return Template(tmp).render(
                name=self.name
            )
        return str(self)

@dataclass
class Type:
    name: str = ''

    def __str__(self):
        return 'type'

    def render(self, env):
        return env.templates['types'].get(self.name, self.name)

def type_render(self, _type):
    if hasattr(_type, 'render'):
        return _type.render(self)
    return self.templates['types'].get(_type, _type)

def to_any(_type):
    if hasattr(_type, 'to_any'):
        return _type.to_any()
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
