#    This file is part of Python-Universal-Trnslator.
#
#    Python-Universal-Trnslator is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Python-Universal-Trnslator is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Python-Universal-Trnslator.  If not, see <https://www.gnu.org/licenses/>.

import ast                                                                                                                                                            
import argparse                                                                                                                                                       
import os                                                                                                                                                             
from transPYler import blocks                                                                                                                                         
                                                                                                                                                                      
parser = argparse.ArgumentParser(description='Python to other language')                                                                                              
parser.add_argument("file", type=str, help="Python file")                                                                                                             
parser.add_argument("-c", "--config", type=str, help="Name translator file in transPYler/translators (file type not needed)")                                         
parser.add_argument("-o", "--output", type=str, default=f"1.{os.getenv('translator_name')}", help=f"Output file default: 1.{os.getenv('translator_name')}")           
args = parser.parse_args()                                                                                                                                            
                                                                                                                                                                      
if args.config:                                                                                                                                                       
    os.environ["translator_name"]=args.config                                                                                                                         
                                                                                                                                                                      
code=open(args.file, 'r').read()                                                                                                                                      
                                                                                                                                                                      
blocks.crawler(ast.parse(code).body)      
