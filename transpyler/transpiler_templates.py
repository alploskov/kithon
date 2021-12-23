from jinja2 import Template


conf = {
    'name': '{{name}}',
    'Int': '{{val}}',
    'Float': '{{val}}',
    'Bool': '{{val}}',
    'Str': "'{{val}}'",

    'bin_op': '({{left}} {{op}} {{right}})',
    'un_op': '{{op}}({{el}})',

    'callfunc': "{{func}}({{args|join(', ')}})",
    'getattr': "{{obj}}.{{attr}}",
    'callmethod': "{{obj}}.{{attr}}({{args|join(', ')}})",
    'arg': '{{name}}: {{_type}}',

    'List': "[{{ls|join(', ')}}]",
    'Tuple': "({{ls|join(', ')}})",
    'Dict': "{{'{'}}{%-set _dict = []-%}{%-for kw in keys_val-%}{{_dict.append(+kw|join(', ')+']') or ''}}{%-endfor-%}{{_dict|join(', ')}}])",

    'index': '{{obj}}[{{key}}]',
    'slice': '{% if step == 1 %}{{obj}}[{{low}}:{{up}}]{% else %}{{obj}}[{{low}}:{{up}}:{{step}}]{%endif%}',

    'expr': '{{value}}',

    'assign': '{{var}} = {{value}}',
    'set_attr': '{{var}} = {{value}}',
    'new_attr': '{{var}} = {{value}}',
    'assignment_by_key': '{{var}} = {{value}}',
    'new_key': '{{var}} = {{value}}',
    'new_var': '{{var}} = {{value}}',

    'if': "if {{condition}}{{body}}{%if els%}{{'\n'}}{{els}}{%endif%}",
    'elif': "elif {{condition}}{{body}}{{'\n'}}{{els}}",
    'else': "else{{body}}",

    'func': "{{'\n'}}def {{name}}({{args|join(', ')}}){{body}}{{'\n'}}",

    'return': "return {{value}}",

    'while': "while {{condition}} {{body}}",

    'for': 'for {{var}} in {{obj}}{{body}}',

    'break': 'break',
    'continue': 'continue',

    'class': '''class {{name}}:
{{'    '*nl}}{{attrs|join('\n'+'    '*(nl))}}
{{'    '*nl}}{{init}}
{{'    '*nl}}{{methods|join('\n'+'    '*(nl))}}''',

    'init': "def __init__({{args|join(', ')}}) {{body}}",
    'method': "def {{name}}({{args|join(', ')}}) {{body}}",
    'attr': '{{var}} = {{value}}',
    'new': "{{func}}({{args|join(', ')}})",

    'body': ''':{%for st in body%}
{{'    '*nl}}{{st}}{%endfor%}''',

    'global': 'global {{vars|join(", ")}}',
    'nonlocal': 'nonlocal {{vars|join(", ")}}',
    'import': '',
    'Main': '{{_body|join("\n")}}'
}

default = {name: Template(code) for name, code in conf.items()} | {
    'types': {},
    'operators': {},
}

