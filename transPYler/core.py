import re
import ast


elements = {}
handlers = {}

def parser(el):
    el_f = elements.get(type(el))
    if el_f:
        return el_f(el)

namespace = "main"
variables = {"main": {}}

def crawler(code):
    strings = []
    body = ast.parse(code).body
    for i in body:
        i = parser(i)
        if i:
            strings.append(i)
    return '\n'.join(strings)
