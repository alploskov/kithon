import ast
from collections import defaultdict
import yaml
from hy.lex import hy_parse
from jinja2 import Template
from . import types, node as _node, transpiler_templates


def visitor(func):
    setattr(Transpiler, func.__name__, func)
    annotations = func.__annotations__['tree']
    if isinstance(annotations, tuple):
        for ann in annotations:
            Transpiler.elements[ann] = func
    else:
        Transpiler.elements[annotations] = func
    return func

class Transpiler:
    elements = {}

    def __init__(self, templates):
        self.templates = defaultdict(dict) | transpiler_templates.default
        self.nl = 0
        self.namespace = '__main__'
        self.variables = {
            '__main__': {'type': types.types['module']('__main__')}
        }
        self.strings = []
        self.temp_var_counts = defaultdict(int)
        self.used = set([])
        self.add_templ(templates)

    def new_var(self, full_name, _type):
        if str(_type) in self.variables:
            self.variables.update({
                full_name + name.removeprefix(_type): var
                for name, var in self.variables.items()
                if name.startswith(_type)
            })
        self.variables.update({
            full_name: {
                'own': full_name,
                'type': _type,
                'immut': True
            }
        })

    def use(self, name):
        self.used.add(name)
        return ''

    def get_temp_var(self, base_name='temp'):
        """Get a unique temporary variable name."""
        self.temp_var_counts[base_name] += 1
        return f'{base_name}_{self.temp_var_counts[base_name]}'

    def previous_ns(self):
        if self.namespace == '__main__':
            return '__main__'
        return self.namespace[:self.namespace.rfind('.')]

    def node(self, tmp=None, parts=None, type=None, own=None):
        return _node.node(
            env=self, tmp=tmp,
            parts=parts, type=type,
            nl=self.nl, own=own
        )

    def add_templ(self, templates):
        templates = yaml.load(
            templates.expandtabs(2),
            Loader=yaml.FullLoader
        )
        if not templates:
            return
        for name, template in templates.items():
            if not template:
                self.templates[name] = {}
            elif isinstance(template, str):
                self.templates[name].update({'tmp': Template(template)})
            elif isinstance(template, dict):
                self.templates[name].update(template)

    def visit(self, tree, **kw):
        if type(tree) not in self.elements:
            return self.node()
        node = self.elements.get(type(tree))(
            self, tree,
            **(kw or {})
        )
        node.ast = tree
        return node

    def generate(self, code, lang='py', mode='main'):
        if lang == 'py':
            tree = ast.parse(code).body
        elif lang == 'hy':
            tree = hy_parse(code)[1:]
        elif lang == 'coco':
            from coconut.convenience import parse, setup
            setup(target='sys')
            tree = ast.parse(parse(code, 'block')).body
        for block in map(self.visit, tree):
            if not block:
                continue
            self.strings.extend(block.render().split('\n'))
        if mode == 'main':
            code = self.templates['Main']['tmp'].render(
                _body=self.strings,
                body='\n'.join(self.strings),
                env=self
            )
            self.variables = {
                '__main__': {'type': types.types['module']('__main__')}
            }
            self.temp_var_counts = defaultdict(int)
        else:
            code = '\n'.join(self.strings)
        self.nl = 0
        self.namespace = '__main__'
        self.strings = []
        self.used = set([])
        return code
