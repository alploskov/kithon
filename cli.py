import ast
import argparse
import importlib
import sys
import transPYler
from transPYler import tools

parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("-c", "--config", type=str, default="js", help="Name translator file in translators")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file default: stdout")
args = parser.parse_args()

translator = importlib.import_module(f"translators.{args.config}")
transPYler.core.handlers |= translator.handlers
transPYler.expressions.signs |= tools.dentification_signs(translator.signs)
if 'macros' in dir(translator):
    transPYler.macros = translator.macros
if 'attrs' in dir(translator):
    transPYler.objects = translator.attrs
if 'type_by_op' in dir(translator):
    transPYler.type_by_op = translator.type_by_op
if args.output != sys.stdout:
    args.output = open(args.output, 'w')

set_up = ""
if "set_up" in dir(translator):
    set_up = translator.set_up()

code = open(args.file, 'r').read()
print(set_up+transPYler.crawler(ast.parse(code).body), file=args.output)
