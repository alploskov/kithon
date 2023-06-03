import os
import sys
import json
import subprocess
from inspect import getsource
import execjs
from lupa import LuaRuntime
from kithon import Transpiler, analogs
from type_conversion import type_conversion


transpilers = {
    'python': Transpiler(),
    'lua': Transpiler(lang='lua'),
    'js': Transpiler(lang='js'),
#    'go': Transpiler(lang='go'),
}

lua = LuaRuntime(unpack_returned_tuples=True)
js = execjs.get()


def load_js_func(func: str):
    global js
    js = execjs.compile(func)

executors = {
    'python': eval,
    'lua': lua.eval,
    'js': lambda e: js.eval(e),
}

func_loaders = {
    'python': exec,
    'js': load_js_func,
    'lua': lua.execute,
 }

def check_exprs(exprs):
    expected_results = list(map(eval, exprs))
    for lang, T in transpilers.items():
        for i, e in enumerate(exprs):
            checked_expr = T.generate(e, mode='eval')
            fact_result = type_conversion(executors[lang](checked_expr), lang)
            assert expected_results[i] == fact_result, f'\n\tpython: {e} -> {expected_results[i]}\n\t{lang}: {checked_expr} -> {fact_result}'
            T.used.clear()

def check_func(func):
    expected_results = func()
    src = getsource(func)
    for lang, T in transpilers.items():
        target_src = T.generate(src, mode='block')
        func_loaders[lang](target_src)
        fact_result = type_conversion(executors[lang](analogs.call(T, func.__name__).render()), lang)
        assert expected_results == fact_result, f'\n\tpython:\n{src}\n\t\t--> {expected_results}\n\t{lang}:\n{target_src} \n\t\t--> {fact_result}'
        T.used.clear()
