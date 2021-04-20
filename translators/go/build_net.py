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

if args.file:
    code = open(args.file, 'r').read()
    out += 'package main\n\nimport(\n    "net/http"\n    "fmt"\n)\n\n'
    body = transPYler.core.compiler(code).split('\n')
    transPYler.blocks.nesting_level += 1
    tab = '\n'+'    '*transPYler.blocks.nesting_level
    end = ('\n'+'    '*(transPYler.blocks.nesting_level-1))+'    http.ListenAndServe("localhost:8080", nil)\n}'
    out += 'func main(){'+tab+tab.join(body)+end
    print(out, file=out_file)
