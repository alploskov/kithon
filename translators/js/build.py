import argparse
import sys
import transPYler
import expr, blocks, macros


parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, default=None, help="Python file")
parser.add_argument("-o", "--output", default=sys.stdout, help="Output file. default: stdout")
parser.add_argument("-e")
args = parser.parse_args()
#if args.e:
#    print(transPYler.core.compiler(args.e), file=args.output)
if args.output != sys.stdout:
    args.output = open(args.output, 'w')
    
if args.file:
    code = open(args.file, 'r').read()
    print(transPYler.core.compiler(code), file=args.output)
