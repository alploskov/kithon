from lupa import LuaRuntime
from kithon import Transpiler, analogs


class Lua:
    def __init__(self):
        self.runtime = LuaRuntime(unpack_returned_tuples=True)
        self.generator = Transpiler(lang='lua')

    def load_func(self, func: str):
        self.runtime.execute(func)
    
    def call_func(self, name):
        return self.eval(analogs.call(self.generator, name).render())

    def eval(self, expr: str):
        return self.runtime.eval(expr)

    def gen_func(self, src):
        return self.generator.generate(src, mode='block')

    def gen_expr(self, src):
        return self.generator.generate(src, mode='eval')

    def clear(self):
        self.generator.used.clear()
