from lupa import LuaRuntime
from kithon import Transpiler, analogs


class Py:
    def __init__(self):
        self.runtime = None
        self.generator = Transpiler()

    def load_func(self, func: str):
        exec(func, globals())
        
    def call_func(self, name):
        return eval(analogs.call(self.generator, name).render())

    def eval(self, expr: str):
        return eval(expr)

    def gen_func(self, src):
        return self.generator.generate(src, mode='block')

    def gen_expr(self, src):
        return self.generator.generate(src, mode='eval')

    def clear(self):
        self.generator.used.clear()
