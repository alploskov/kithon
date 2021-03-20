import argparse
import sys
import transPYler
import expr, blocks, macros


parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, default=None, help="Python file")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file. default: stdout")
parser.add_argument("-e")
args = parser.parse_args()
if args.output != sys.stdout:
    out_file = open(args.output, 'w')
else:
    out_file = args.output
out = ''
type_to_type = {"int": "Integer",
                "str": "String",
                "float": "Real"
                }

if args.file:
    code = open(args.file, 'r').read()
    out += 'Program main;\nUses CRT;\n\n'
    body = transPYler.core.compiler(code).split('\n')
    var = transPYler.core.variables.get('main')
    if var:
        variables = ""
        for i in var:
            _type = type_to_type.get(var.get(i))
            variables += f'    {i}: {_type};\n'
        out += 'Var\n'+variables+'\n'
    transPYler.blocks.nesting_level += 1
    tab = '\n'+'    '*transPYler.blocks.nesting_level
    end = ('\n'+'    '*(transPYler.blocks.nesting_level-1))+'End.'
    out += 'Begin'+tab+tab.join(body)+end
    print(out, file=out_file)
