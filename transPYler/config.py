import yaml
from jinja2 import Template 
from . import core


def add_templ(t):
    tmpls = yaml.load(open(t, 'r').read())
    for i in tmpls:
        if i not in ['operations', 'types']:
            tmpls[i] = Template(tmpls.get(i))
    core.tmpls |= tmpls

def add_macros(m):
    core.macros |= yaml.load(open(m, 'r').read())
    if 'classes' in core.macros:
        core.objects |= core.macros.get('classes')
