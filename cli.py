import ast
import argparse
import importlib
import sys
from transPYler import transPYler, tools

parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("-c", "--config", type=str, default="js", help="Name translator file in translators")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file default: stdout")
args = parser.parse_args()

translator = importlib.import_module(f"translators.{args.config}")
transPYler.handlers = translator.handlers
transPYler.signs = tools.dentification_signs(translator.signs)
transPYler.a_func = translator.a_func
transPYler.operator_overloading_data = translator.operator_overloading 
transPYler.lib = translator.lib
transPYler.attrs = translator.attrs
if args.output != sys.stdout:
    args.output = open(args.output, 'w')

set_up = ""
if "set_up" in dir(translator):
    set_up = translator.set_up()

code = open(args.file, 'r').read()
print(set_up+transPYler.crawler(ast.parse(code).body), file=args.output)

