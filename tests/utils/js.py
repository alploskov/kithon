import execjs
from kithon import Transpiler, analogs


class JS:
    def __init__(self):
        self.runtime = execjs.get()
        self.generator = Transpiler(lang='js')
        self.NAME = 'js'

    def load_func(self, func: str):
        self.runtime = execjs.compile(func)

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
