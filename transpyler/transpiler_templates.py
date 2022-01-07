from jinja2 import Template


conf = {
    'name': '{{name}}',
    'Int': '{{val}}',
    'Float': '{{val}}',
    'Bool': '{{val}}',
    'Str': "\"{{val}}\"",

    'bin_op': '''{%-if parent.name == "bin_op"-%}
({{left}} {{op}} {{right}})
{%-else-%}
{{left}} {{op}} {{right}}
{%-endif-%}''',
    'un_op': '{{op}}({{el}})',

    'callfunc': "{{func}}({{args|join(', ')}}{%if kwargs%}, {{kwargs|join(', ')}}{%endif%})",
    'getattr': "{{obj}}.{{attr}}",
    'callmethod': "{{obj}}.{{attr}}({{args|join(', ')}}{%if kwargs%}, {{kwargs|join(', ')}}{%endif%})",
    'arg': '{{name}}',
    'kwarg': '{{name}}={{value}}',
    'List': "[{{ls|join(', ')}}]",
    'Tuple': "({{ls|join(', ')}})",
    'Dict': "{{'{'}}{%for item in keys_val%}{{item[0]}}: {{item[1]}},{%endfor%}}",

    'index': '{{obj}}[{{key}}]',
    'slice': '{% if step == 1 %}{{obj}}[{{low}}:{{up}}]{% else %}{{obj}}[{{low}}:{{up}}:{{step}}]{%endif%}',

    'expr': '{{value}}',

    'assign': '{{var}} = {{value}}',
    'unpack': '{{vars|join(", ")}} = {{value}}',
    'unpack_to_new': '{{vars|join(", ")}} = {{value}}',    
    'set_attr': '{{var}} = {{value}}',
    'new_attr': '{{var}} = {{value}}',
    'assignment_by_key': '{{var}} = {{value}}',
    'new_key': '{{var}} = {{value}}',
    'new_var': '{{var}} = {{value}}',

    'if': "if {{condition}}{{body}}{%if els%}{{'\n'}}{{els}}{%endif%}",
    'elif': "{{'    '*nl}}elif {{condition}}{{body}}{{'\n'}}{{els}}",
    'else': "{{'    '*nl}}else{{body}}",

    'func': "{{'\n'}}def {{name}}({{args|join(', ')}}){{body}}{{'\n'}}",
    'lambda': 'lambda {{args|join(", ")}}: {{body}}',
    'return': "return {{value}}",

    'while': "while {{condition}} {{body}}",

    'for': 'for {{var}} in {{obj}}{{body}}',

    'break': 'break',
    'continue': 'continue',

    'class': '''class {{name}}:
{{'    '*nl}}{{attrs|join('\n'+'    '*(nl))}}
{{'    '*nl}}{{init}}
{{'    '*nl}}{{methods|join('\n'+'    '*(nl))}}''',

    'init': "def __init__({{args|join(', ')}}){{body}}",
    'method': "def {{name}}({{args|join(', ')}}){{body}}",
    'static_attr': '{{var}} = {{value}}',
    'new': "{{func}}({{args|join(', ')}})",

    'body': ''':{%for st in body%}
{{'    '*nl}}{{st}}{%endfor%}''',
    'global': 'global {{vars|join(", ")}}',
    'nonlocal': 'nonlocal {{vars|join(", ")}}',
    'import': '',
    'Main': '{{_body|join("\n")}}'
}

macros = {
    'int': {
        'type': 'type',
        'ret_type': 'int'
    },
    'str': {
        'type': 'type',
        'ret_type': 'str'
    },
    'float': {
        'type': 'type',
        'ret_type': 'float'
    },
    'bool': {
        'type': 'type',
        'ret_type': 'bool'
    }
}

type_inference_rules = {rule: {'type': res} for rule, res in {
    'int.+.int':   'int',
    'int.-.int':   'int',
    'int./.int':   'float',
    'int.*.int':   'int',
    'int.//.int':  'int',
    'int.%.int':   'int',
    'int.<<.int': 'int',
    'int.>>.int': 'int',
    'int.|.int': 'int'
}.items()}

default = (
    {name: Template(code) for name, code in conf.items()}
    | {'types': {},'operators': {}}
    | macros
    | type_inference_rules
)
