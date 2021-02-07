from . import core, expressions, blocks
from .core import parser


def crawler(body):
    strings = []
    for i in body:
        i = parser(i)
        if i:
            strings.append(i)
    return '\n'.join(strings)
