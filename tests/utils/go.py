import os
import sys
import importlib
from kithon import Transpiler, analogs


class Go:
    def __init__(self):
        self.generator = Transpiler(lang='go')
        self.NAME = 'go'
        self.counter = 0
        sys.path.append(os.getcwd())

    def load_func(self, func: str):
        pass
        
    def call_func(self, name):
        pass

    def eval_many(self, exprs: list[str]):
        _exprs = list(map(self.gen_expr, exprs))
        with open(f'kithon_test{self.counter}.go', 'w') as f:
            f.write('''package main
            import (
                "C"
	        "unsafe"
	        "gitlab.com/pygolo/py"
            )
            ''')
            for mod in self.generator.used:
                if mod.startswith('mod_'):
                    print(f'import "{mod.removeprefix("mod_")}"', file=f)
            print('func ext(Py py.Py, m py.Object) error {', file=f)
            for n, expr in enumerate(_exprs):
                f.write(f'''
	            if err := Py.Object_SetAttr(m, "expr{n}", {expr}); err != nil {{
	                return err
	            }}
                ''')
            print('return nil\n}', file=f)
            f.write(f'//export PyInit_kithon_test{self.counter}\n')
            f.write(f'func PyInit_kithon_test{self.counter}() unsafe.Pointer {{ return py.GoExtend(ext) }}\n')
            f.write('func main() {}')
        os.system(f'go build -tags py_ext -buildmode=c-shared -o kithon_test{self.counter}.so kithon_test{self.counter}.go')
        res = []
        test_mod = importlib.import_module(f'kithon_test{self.counter}')
        for n, expr in enumerate(exprs):
            res.append(getattr(test_mod, f'expr{n}'))
        os.remove(f'kithon_test{self.counter}.go')
        os.remove(f'kithon_test{self.counter}.so')
        os.remove(f'kithon_test{self.counter}.h')
        self.counter += 1
        self.clear()
        return res

    def gen_func(self, src):
        return self.generator.generate(src, mode='block')

    def gen_expr(self, src):
        return self.generator.generate(src, mode='eval')

    def clear(self):
        self.generator.used.clear()
