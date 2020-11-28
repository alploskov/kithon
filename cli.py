import ast
import argparse
import os


parser = argparse.ArgumentParser(description='Python to other language')
parser.add_argument("file", type=str, help="Python file")
parser.add_argument("-c", "--config", type=str, help="Name translator file in transPYler/translators (file type not needed)")
parser.add_argument("-o", "--output", type=str, default=f"1.{os.getenv('translator_name')}", help=f"Output file default: 1.{os.getenv('translator_name')}")
args = parser.parse_args()

if args.config:
    os.environ['translator_name'] = args.config

from transPYler import blocks 
code=open(args.file, 'r').read()

blocks.crawler(ast.parse(code).body)
