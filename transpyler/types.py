from dataclasses import dataclass
import typing
from typing import Union, Any
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
class Tuple:
    el_type: tuple[Any] = ()
    els_types: Any = None

    def __str__(self):
        return f'tuple[{", ".join(self.els_types)}]'

    def render(self, env):
        tmp = env.templates['types'].get('tuple')
        if tmp:
            return Template(tmp).render(
                els_types=type_render(env, self.els_types)
            )
        return str(self)

@dataclass
class Func:
    def __init__(self, name, args, ret_type):
        self.name = name
        self.args = tuple(a.type for a in args)
        self.ret_type = ret_type

    def __str__(self):
        return f'func[{", ".join(self.args)}]{self.ret_type}'

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
    el_type: Union[typing.Any, str] = 'generic'

    def __str__(self):
        return f'dict[{self.key_type}]{self.el_type}'

    def render(self, env):
        tmp = env.templates['types'].get('dict')
        if tmp:
            return Template(tmp).render(
                key_type=type_render(env, self.key_type),
                el_type=type_render(env, self.el_type)
            )
        return str(self)

    def to_any(self):
        if self.key_type == self.el_type == 'any':
            return 'any'
        if self.el_type == 'any':
            return Dict(to_any(self.key_type), 'any')
        if self.key_type == 'any':
            return Dict('any', to_any(self.el_type))
        return Dict(self.key_type, to_any(self.el_type))

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

def element_type(element):
    _type = element.type
    if isinstance(_type, List):
        return _type.el_type
    return _type

types = {'list': List, 'dict': Dict, 'tuple': Tuple}

def type_eval(type_code, parts={}):
    """
    Generate type from macros
    """
    if isinstance(type_code, list):
        _types = tuple(map(type_eval, type_code))
        return Tuple(tuple(set(_types)), _types)
    if type_code.startswith('class_'):
        return type_code[6:]
    if type_code == 'module':
        return 'module'
    try:
        _type = eval(
            type_code,
            types | parts | {'int': 'int'}
        ) or 'None'
    except:
        return type_code
    if isinstance(_type, type):
        _type = str(_type)[8:-2]
    return _type

# creating new types in config
# matrix:
#   attrs:
#     el_type: generic
#   str:
#     matrix[{{el_type}}]
#
