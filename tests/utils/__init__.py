from inspect import getsource
from .type_conversion import type_conversion
from .js import JS
from .lua import Lua
from .py import Py
from .go import Go


langs = [Py(), Go(), JS(), Lua()]

def check_exprs(exprs):
    expected_results = list(map(eval, exprs))
    for lang in langs:
        if hasattr(lang, 'eval_many'):
            assert expected_results == lang.eval_many(exprs), ''
            continue
        for i, e in enumerate(exprs):
            checked_expr = lang.gen_expr(e)
            fact_result = type_conversion(lang.eval(checked_expr))
            lang.clear()
            assert expected_results[i] == fact_result, (e, lang.NAME)

def check_func(func):
    expected_results = func()
    src = getsource(func)
    for lang in langs:
        target_src = lang.gen_func(src)
        lang.load_func(target_src)
        fact_result = type_conversion(lang.call_func(func.__name__))
        lang.clear()
        assert expected_results == fact_result, (func.__name__, lang.NAME)
