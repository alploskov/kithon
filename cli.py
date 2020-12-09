import ast
import argparse
import importlib
from transPYler import blocks, tools 


parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("-c", "--config", type = str, default="js", help="Name translator file in translators")
parser.add_argument("-o", "--output", type = str, default="1.js", help="Output file default: 1.js")
parser.add_argument("-co", "--console", type = bool, default="1.js", help="Output/not output in console")
args = parser.parse_args()

translator = importlib.import_module(f"translators.{args.config}")

tools.conf(b_handlers = translator.blocks_handlers,
     e_handlers = translator.expr_handlers,
     signs = translator.signs,
     a_attr = translator.a_attr,
     a_func = translator.a_func)

code=open(args.file, 'r').read()
blocks.crawler(ast.parse(code).body)
