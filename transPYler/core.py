elements = {}
handlers = {}

def parser(el):
    el_f = elements.get(type(el))
    if el_f:
        return el_f(el)

namespace = "main"
variables = {"main": {}}
