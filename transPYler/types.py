from jinja2 import Template


class List():
    def __init__(self, el_type):
        self.el_type = el_type
        self.to_str = f'list[{to_string(el_type)}]'

class Func():
    def __init__(self, ret_type):
        self.ret_type = ret_type
        self.to_str = f'func->{to_string(ret_type)}'

class Dict():
    pass

class Module():
    def __init__(self, name):
        self.name = name

def to_string(_type):
    return getattr(_type, 'to_str', _type)

def type_render(self, _type):
    if isinstance(_type, List):
        tmp = self.tmpls['types'].get('list')
        if tmp:
            return Template(tmp).render(
                el_type=type_render(
                    self,
                    _type.el_type
                )
            )
        return to_string(_type)
    return self.tmpls['types'].get(_type, _type)
    
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


def element_type(el):
    _type = el.type
    if isinstance(_type, List):
        return _type.el_type
    return _type
