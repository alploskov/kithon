import argparse
import importlib
import sys
import transPYler
from transPYler import utils


parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("--macros", type=str, help="Name translator file in translators") 
parser.add_argument("-c", "--config", type=str, default="js", help="Name translator file in translators")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file default: stdout")
args = parser.parse_args()


if macros_file := args.macros:
    exec(open(macros_file, 'r').read())
    transPYler.macros.macros |= utils.op_overload_key(macros)

translator = importlib.import_module(f"translators.{args.config}")
transPYler.core.handlers |= translator.handlers
transPYler.expressions.signs |= utils.dentification_signs(translator.signs)
if 'attrs' in dir(translator):
    transPYler.objects = translator.attrs
if 'type_by_op' in dir(translator):
    transPYler.type_by_op = translator.type_by_op
if args.output != sys.stdout:
    args.output = open(args.output, 'w')

set_up = ""
if "setup" in dir(translator):
    setup = translator.setup()
if "end" in dir(translator):
    end = translator.end()

code = open(args.file, 'r').read()
print(setup+transPYler.core.crawler(code)+end, file=args.output)
