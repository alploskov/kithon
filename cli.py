import ast
import argparse
import importlib
import sys
from transPYler import tools, crawler

parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("-c", "--config", type=str, default="js", help="Name translator file in translators")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file default: stdout")
args = parser.parse_args()

translator = importlib.import_module(f"translators.{args.config}")
tools.conf(b_handlers=translator.blocks_handlers,
           e_handlers=translator.expr_handlers,
           signs=translator.signs,
           a_attr=translator.a_attr,
           a_func=translator.a_func,
           lib=translator.lib)

if args.output != sys.stdout:
    args.output = open(args.output, 'w')

set_up = ""
if "set_up" in dir(translator):
    set_up = translator.set_up()

code = open(args.file, 'r').read()
print(set_up+crawler(ast.parse(code).body), file=args.output)
