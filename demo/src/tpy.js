var pyodide = null;
var lang = document.getElementById('chose-lang').value;
document.getElementById('chose-lang').addEventListener('change', (event) => {
    lang = event.target.value;
    if(lang == 'js'){
	output.getSession().setMode("ace/mode/javascript");
    } else if(lang == 'go'){
	output.getSession().setMode("ace/mode/golang");
    }
    output.setValue(generate(editor.getValue()));
    output.clearSelection();
    output.setHighlightActiveLine(false);
});
async function main(){
    pyodide = await loadPyodide({
        indexURL : "https://cdn.jsdelivr.net/pyodide/v0.18.0/full/"
    });
    await pyodide.loadPackage("micropip");
    await pyodide.runPythonAsync(`
import micropip
await micropip.install('src/transPYler-0.0.1-py-none-any.whl')
`);
    await pyodide.runPythonAsync(`
import transpyler
transpiler_js = transpyler.Transpiler('''
name: "{{name}}"
const: &const "{{val}}"
Int: *const
Float: *const
Bool: "{{val|lower}}"
Str: "'{{val}}'"

operators:
  "or": "||"
  "and": "&&"
  "not": "!"
  "is": "==="

bin_op: "({{left}} {{op}} {{right}})"
un_op: "{{op}}{{el}}"

callfunc: "{{func}}({{args|join(', ')}})"
getattr: "{{obj}}.{{attr}}"
callmethod: "{{obj}}.{{attr}}({{args|join(', ')}})"
arg: "{{name}}"

List: "[{{ls|join(', ')}}]"
Tuple: "[{{ls|join(', ')}}]"
Dict: >-
  new Map([
  {%-set _dict = []-%}
  {%-for kw in keys_val-%}
    {{_dict.append('['+kw|join(', ')+']') or ''}}
  {%-endfor-%}
  {{_dict|join(', ')}}])

index: >-
  {{obj}}
  {%- if isinstance(obj.type, list) -%}[
    {%- if get_val(key) != 'unknown' -%}
      {%- if get_val(key) < 0 -%}
        {{obj}}.length+{{key}}
      {%-else-%}
        {{key}}
      {%- endif -%}
    {%- else -%}
      ({{key}}<0)?({{obj}}.length+{{key}}):({{key}})
    {%-endif-%}]
  {%- elif isinstance(obj.type, dict) -%}
    {%- if ctx == 'load' -%}
    .get({{key}})|| (()=>{throw "key error"})()
    {%-else-%}
    [{{key}}]
    {%-endif-%}
  {%- endif -%}

slice: |-
  {%- if step() == '1' -%}
    {{obj}}.slice({{low}}, {{up}})
  {%-elif step() != '0'-%}
    {%- if get_val(step) != 'unknown' -%}
      {%- if get_val(step) < 0 -%}
        [...{{obj}}].reverse()
      {%- else -%}
        {{obj}}
      {%- endif -%}
    {%- else -%}
      ({{step}}<0?[...{{obj}}].reverse():{{obj}})
    {%- endif -%}
    {%-if low() != '' or up() != ''-%}
      .slice(...({{step}}<0?[{{up}}, {{low}}]:[{{low}}, {{up}}]))
    {%-endif-%}
    {%-if step() != '-1'-%}
      .filter((_,i)=>(i%{{step}})==0)
    {%-endif-%}
  {%-endif-%}

expr: "{{value}};"
assign: &assign "{{var}} = {{value}};"
set_attr: *assign
assignment_by_key: *assign
new_var: "let {{var}} = {{value}};"

if: "if ({{condition}}) {{body}} {{els}}"
elif: "else if ({{condition}}) {{body}} {{els}}"
else: "else {{body}}"

func: "function {{name}}({{args|join(', ')}}) {{body}}"

return: "return {{value}};"

while: "while ({{condition}}) {{body}}"

for: >-
  for (let {{var}}
  {{'in' if isinstance(obj.type, dict) else 'of'}}
  {{obj}})
  {{body}}

c_like_for: >-
  for (let {{var}} = {{start}};
  ({{step}}<0?{{var}}>{{finish}}:{{var}}<{{finish}});
  {{var}} += {{step}})
  {{body}}

break: "break;"
continue: "continue;"

body: |-
  {{'{'}}{%for st in body%}
  {{'    '*nl}}{{st}}{%endfor%}
  {{'    '*(nl-1)}}}
class: |-
  class {{name}} {{'{'}}
  {{'    '*nl}}{{attrs|join("\\\n"+'    '*nl)}}
  {{'    '*nl}}{{init}}
  {{'    '*nl}}{{methods|join("\\\n"+'    '*(nl))}}
  {{'    '*(nl-1)}}}

init: "constructor({{(args[1:])|join(', ')}}) {{body}}"
method: "{{name}}({{(args[1:])|join(', ')}}) {{body}}"
self: "this"
attr: "{{var}} = {{value}};"
new: "new {{func}}({{args|join(', ')}})"

min:
  alt_name: "Math.min"
  type: float

max:
  alt_name: "Math.max"
  type: float

round:
  args: [num, ndigits]
  code: "+{{num}}.toFixed({{ndigits}})"

print:
  alt_name: "console.log"
  rettype: "None"

input:
  alt_name: "prompt"
  type: "func"
  rettype: "str"

len:
  code: "{{args[0]}}.length"
  rettype: int

interval:
  alt_name: "setInterval"
  type: "Func"
  ret_type: "None"

any.//.any:
  code: "Math.floor({{left}}/{{right}})"
  type: "int"

setattr:
  args: ["obj", "name", "val"]
  code: |-
    {%-if parent.name == 'expr'-%}
      {{obj}}[{{name}}] = {{val}}
    {%-else-%}
      (()=>{{obj}}[{{name}}] = {{val}})
    {%-endif-%}
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
  code: "{{left}}"
  type: "List[{{right.type}}]"

list[any].*.int:
  code: 'Array({{right}}).fill({{left}}).flat()'
  type: 'left.type'

list[any].==.list[any]:
  code: |-
    {%- if left() == right()-%}
      true
    {%- else -%}
      (JSON.stringify({{left}})==JSON.stringify({{right}}))
    {%- endif -%}
  type: 'bool'

list[any].index:
  alt_name: 'indexOf'
  type: 'int'

list[any].+.list[any]:
  code: "{{left}}.concat({{right}})"
  type: "left.type"

any.in.list[any]:
  code: "{{right}}.includes({{left}})"
  type: "bool"
''')
`);
await pyodide.runPythonAsync(`
import transpyler
transpiler_go = transpyler.Transpiler('''
name: "{{name}}"
const: &const "{{val}}"
Int: *const
Float: *const
Bool: "{{val|lower}}"

operators:
  "or": "||"
  "and": "&&"
  "not": "!"
  "is": "=="

bin_op: |-
  {%- if parent.name == 'bin_op' -%}
    ({{left}} {{op}} {{right}})
  {%- else -%}
    {{left}} {{op}} {{right}}
  {%- endif -%}

un_op: "{{op}}{{el()}}"

callfunc: "{{func()}}({{args|join(', ')}})"
getattr: "{{obj()}}.{{attr}}"
callmethod: "{{obj()}}.{{attr}}({{args|join(', ')}})"
arg: "{{name}} {{_type}}"

List: "{{_type}}{{'{'}}{{ls|join(', ')}}}"
Dict: "{{_type}}{{'{'}}{%for item in keys_val%}{{item[0]}}: {{item[1]}},{%endfor%}}"

index: |-
  {%- if isinstance(obj.type, list) -%}
    {{- env.use('Index') -}}
    {{obj}}[Index({{key}}, len({{obj}}))]
  {%- else -%}
    {{obj}}[{{key}}]
  {%- endif -%}

slice: |-
  {%- if step() == '1' -%}
    {{-env.use('Index')-}}
    {{obj}}[{{low}}:Index({{up}}, len({{obj}}))]
  {%-endif-%}

expr: "{{value}}"
assign: &assign "{{var}} = {{value}}"
set_attr: *assign
assignment_by_key: *assign
new_var: "{{var}} := {{value}}"

if: "if ({{condition}}) {{body}} {{els}}"
elif: "else if ({{condition}}) {{body}} {{els}}"
else: "else {{body}}"

func: "func {{name}}({{args|map(attribute='val')|join(', ')}}) {{ret_type}} {{body()}}"

return: "return {{value}}"

while: "for {{condition()}} {{body()}}"

for: |-
  {%- if obj.type == 'str' -%}
    {{- env.use('mod_strings') -}}
    for _, {{var}} := range strings.Split({{obj}}, "")
  {%- elif isinstance(obj.type, dict) -%}
    for {{var}}, _ := range {{obj}}
  {%- else -%}
    for _, {{var}} := range {{obj}}
  {%- endif -%} {{body}}

c_like_for: >-
  for {{var()}} := {{start()}};{{' '}}
  {%- if get_val(step) < 0 -%}
    {{var}} > {{finish}};
  {%- elif get_val(step) >= 0 -%}
    {{var}} < {{finish}};
  {%- else -%}
    ({{step}} < 0 && {{var}} > {{finish}}) || ({{var}} < {{finish}});
  {%- endif -%}
  {{' '}}{{var()}} += {{step()}}
  {{body()}}

break: "break;"
continue: "continue;"

types:
  list: "[]{{el_type}}"
  str: string
  float: float64
  dict: "map[{{key_type}}]{{el_type}}"

body: |-
  {{'{'}}{%for st in body%}
  {{'    '*nl}}{{st()}}{%endfor%}
  {{'    '*(nl-1)}}}

class: |-
  type {{name}} struct {{'{'}}
  {{' '*4*(nl)}}{{attrs|join('\\\n'+' '*4*(nl))}}
  }
  {{init}}
  {{methods|join('\\\n')}}

init: |-
  func init_{{class_name}}({{(args[1:])|join(', ')}}) {{class_name}}{{'{'}}
  {{' '*4*nl}}self := {{class_name+'{}'}}
  {{' '*4*(nl)}}{{body.parts.body|join('\\\n'+' '*4*(nl-1))}}
  {{' '*4*(nl)}}return self
  }
method: |-
  func (self {{class_name}}) {{name}}({{(args[1:])|join(', ')}}) {{ret_type}} {{'{'}}
  {{' '*4*(nl)}}{{body.parts.body|join('\\\n'+' '*4*(nl-1))}}
  }
attr: "{{var}} {{_type}}"
new: "init_{{func}}({{args|join(', ')}})"

Main: |-
  package main
  {% if env.used %}  
  import ({%- for used in env.used -%}
  {% if used.startswith('mod_')%}{{'\\\n'+'    '}}"{{used[4:]}}"{%endif%}
  {%- endfor -%}
  )
  {% if 'Index' in env.used %}
  func Index(index, ln int) int {{'{'}}
      if index < 0 {{'{'}}
          return ln + index
      }
      return index
  }
  {% endif %}
  {% endif %}
  {{body|join('\\\n')}}

print:
  code: |-
    {{-env.use('mod_fmt')-}}
    fmt.Println({{args|join(', ')}})
  ret_type: "None"

str:
  code: |-
    {{-env.use('mod_fmt')-}}
    fmt.Sprintf("%v", {{args[0]}})
  ret_type: "str"

main:
  code: ""

len:
  ret_type: int

list[any].append:
  side_effect: |-
    set_el_type(obj, args[0].type)
    set_as_mut(obj)
  code: |-
    {%-if parent.name != 'expr'-%}
      {{'func()error{'}}{{obj}} = append({{obj}}, {{args[0]}}){{';return nil}()'}}
    {%-else-%}
      {{obj}} = append({{obj}}, {{args[0]}})
    {%-endif-%}
  ret_type: "None"

list[generic].*.type:
  side_effect: |-
    set_el_type(left, right.type)
  code: "{{left}}"
  type: "left.type"

list[any].+.list[any]:
  side_effect: |-
    if left.type.el_type != 'generic':
      set_el_type(right, left.type.el_type)
    else:
      set_el_type(left, right.type.el_type)
  code: "append({{left}}, {{right}}...)"
  type: "left.type"

list[any].index:
  code: |-
    {{- env.use('mod_errors') -}}
    func() int {{'{'}}
    {{'    '*nl}}    for i, el := range {{obj}} {{'{'}}
    {{'    '*nl}}        if el == {{args[0]}} {{'{'}}
    {{'    '*nl}}            return i
    {{'    '*nl}}        {{'}'}}
    {{'    '*nl}}    {{'}'}}
    {{'    '*nl}}    {{'panic(errors.New("ValueError: "+fmt.Sprintf("%v",'}}{{args[0]}}){{'+" is not in list"))'}}
    {{'    '*nl}}{{'}()'}}
  ret_type: int
''')
`);
}
main();
var saved_code = 'error';
function generate(code){
    try{
	out_code = pyodide.runPython(`transpiler_${lang}.generate('''${code}''')`);
	saved_code = out_code;
    }catch{
	out_code = saved_code;
    }
    return out_code;
}
