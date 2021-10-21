var pyodide = null;
async function main(){
    tpy_config = `
name: "{{name}}"
const: &const "{{val}}"
Int: *const
Float: *const
Bool: "{{val|lower}}"
Str: "'{{val}}'"

operators:
  "+": "+"
  "-": "-"
  "*": "*"
  "/": "/"
  "**": "**"
  "==": "=="
  "!=": "!="
  ">": ">"
  "<": "<"
  ">=": ">="
  "<=": "<="
  "or": "||"
  "and": "&&"
  "|": "|"
  "&": "&"
  "%": "%"
  "not": "!"
  "is": "==="

bin_op: "({{left()}} {{op}} {{right()}})"
un_op: "{{op}}{{el()}}"

callfunc: "{{func()}}({{args|map(attribute='val')|join(', ')}})"
attr: "{{obj()}}.{{attr}}"
callmethod: "{{obj()}}.{{attr}}({{args|map(attribute='val')|join(', ')}})"
arg: "{{arg}}"

List: "[{{ls|map(attribute='val')|join(', ')}}]"
Tuple: "[{{ls|map(attribute='val')|join(', ')}}]"
Dict: "{{'{'}}{%for i in key_val%}{{i.key()}}: {{i.val()}},{%endfor%}}"

index: "{{obj()}}[{{key()}}<0?{{obj()}}.length+{{key()}}:{{key()}}]"
slice: |-
  {%-if step() == '1'-%}
    {{obj()}}.slice({{low()}}, {{up()}})
  {%-elif step() != '0'-%}
    ({{step()}}<0?Array.from({{obj()}}).reverse():{{obj()}})
    {%-if low() != '' or up() != ''-%}
      .slice(...({{step()}}<0?[{{up()}}, {{low()}}]:[{{low()}}, {{up()}}]))
    {%-endif-%}
    {%-if step() != '1' and step() != '-1'-%}
      .filter((_,i)=>(i%{{step()}})==0)
    {%-endif-%}
  {%-endif-%}

expr: "{{value()}};"
assign: "{{var()}} = {{value()}};"
new_var: "let {{var()}} = {{value()}};"

if: "if ({{condition()}}) {{body()}} {{els()}}"
elif: "else if ({{condition()}}) {{body()}} {{els()}}"
else: "else {{body()}}"

func: "function {{name}} ({{args|map(attribute='val')|join(', ')}}) {{body()}}"

return: "return {{value()}};"

while: "while ({{condition()}}) {{body}}"

for: >-
  for (let {{var()}}
  {{'in' if isinstance(obj.type, Dict) else 'of'}}
  {{obj()}})
  {{body()}}

c_like_for: >-
  for (let {{var()}} = {{start()}};
  ({{step()}}<0?{{var()}}>{{finish()}}:{{var()}}<{{finish()}});
  {{var()}} += {{step()}})
  {{body()}}

break: "break;"
continue: "continue;"

import: "const {{alias}} = require('{{module}}');"

body: |-
  {{'{'}}{%for st in body%}
  {{'    '*nl}}{{st()}}{%endfor%}
  {{'    '*(nl-1)}}}

main: |-
  {{';(function(){'}}{%for st in body%}
  {{st}}{%endfor%}
  })();
event:
  args: [el, event_name, fun]
  code: "{{el()}}.addEventListener({{event_name()}}, {{fun()}})"
  rettype: 'None'

check:
  args: [id]
  code: "document.getElementById({{id()}}).checked"
  rettype: bool

min:
  alt_name: "Math.min"
  type: float

max:
  alt_name: "Math.max"
  type: float

round:
  args: [num, ndigits]
  code: "+{{num()}}.toFixed({{ndigits()}})"

print:
  alt_name: "console.log"
  ret_type: "None"

input:
  alt_name: "prompt"
  type: "Func"
  rettype: "str"

len:
  code: "{{args[0]()}}.length"
  rettype: int

interval:
  alt_name: "setInterval"
  type: "Func"
  ret_type: "None"

url_param:
  alt_name: "new URL(window.location.href).searchParams.get"
  type: str

get_by_id:
  alt_name: "document.getElementById"
  type: dom

any.//.any:
  code: "Math.floor({{left()}}/{{right()}})"
  type: "int"
json:
  type: module
  alt_name: "JSON"
  dumps:
    alt_name: "stringify"
    ret_type: "any"
  loads:
    alt_name: "parse"
    ret_type: "str"
event:
  args: [el, event_name, fun]
  code: "{{el()}}.addEventListener({{event_name()}}, {{fun()}})"
  rettype: 'None'

check:
  args: [id]
  code: "document.getElementById({{id()}}).checked"
  rettype: bool

url_param:
  alt_name: "new URL(window.location.href).searchParams.get"
  type: str

get_by_id:
  alt_name: "document.getElementById"
  rettype: dom

get_by_class:
  alt_name: "document.getElementsByClassName"
  rettype: "list[dom]"

get_by_tagname:
  alt_name: "document.getElementsByTagName"
  rettype: "list[dom]"

dom.<=.any:
  code: "{{left()}}.innerHTML = {{right()}}"
  type: "None"

dom.<<.any:
  code: "{{left()}}.innerHTML += {{right()}}"
  type: "None"
list[any].append:
  side_effect: |-
    set_el_type(obj, args[0].type)
    set_as_mut(obj)
  alt_name: 'push'
  ret_type: "None"

list[None].*.type:
  side_effect: |-
    set_el_type(obj, as=args[0])
    set_as_mut(obj)
  code: "{{left()}}"
  type: "List[{{right.type}}]"

list[any].*.int:
  code: 'Array({{right()}}).fill({{left()}}).flat()'
  type: 'left.type'

list[any].==.list[any]:
  code: |-
    {%- if left() == right()-%}
      true
    {%- else -%}
      (JSON.stringify({{left()}})==JSON.stringify({{right()}}))
    {%- endif -%}
  type: 'bool'

list[any].index:
  alt_name: 'indexOf'
  type: 'int'

list[any].+.list[any]:
  code: "{{left()}}.concat({{right()}})"
  type: "left.type"

any.in.list[any]:
  code: "{{right()}}.includes({{left()}})"
  type: "bool"

str.*.int:
  code: "{{left()}}.repeat({{right()}})"
  type: "str"
`

    pyodide = await loadPyodide({
        indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.0/full/"
    });
    await pyodide.loadPackage("micropip");
    await pyodide.runPythonAsync(`
import micropip
await micropip.install('src/transpyler-0.0.1-py3-none-any.whl')
`);
    await pyodide.runPythonAsync(`
import transPYler
transpiler = transPYler.transpiler('''${tpy_config}''')
`);
}
main();
var saved_code = 'error';
function generate(code){
    try{
	code = pyodide.runPython(`transpiler.generate('''${code}''')`);
	saved_code = code;
    }catch{
	code = saved_code;
    }
    return code;
}
