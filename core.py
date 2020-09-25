import ast
import sys
from Basic import blocks


code=open(sys.argv[1], 'r').read()
blocks.crawler(ast.parse(code).body)
