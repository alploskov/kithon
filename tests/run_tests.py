from kithon import Transpiler
from subprocess import getoutput
from jinja2 import Template
from os import listdir


transpilers = {
    'js': {
        'code': Transpiler(lang='js'),
        'out': Transpiler(templs= '''
list: >-
  {%- if ls|length == 0 -%}
    []
  {%- else -%}
    [ {{ls|join(\', \')}} ]
  {%- endif -%}
bool: "{{val|lower}}"
float: |-
  {%- if parts[0] == 0 -%}
   {{val|int}}
  {%- else -%}
   {{val}}
  {%- endif -%}
un_op: "{{op}}{{el}}"
''')
    },
    'go': {
        'code': Transpiler(lang='go'),
        'out': Transpiler(templs= '''
list: "[{{ls|join(\' \')}}]"
bool: "{{val|lower}}"
float: |-
  {%- if parts[0] == 0 -%}
   {{val|int}}
  {%- else -%}
   {{val}}
  {%- endif -%}
un_op: "{{op}}{{el}}"
''')
    }
}

def test(test_name):
    print('--- test', test_name, '---')
    code = open(f'cases/{test_name}.py', 'r').read()
    result = getoutput(f'python -c "{code}"')
    for name, T in transpilers.items():
        out_code = T['code'].generate(code)
        expected_result = getoutput(
            Template(T['code'].templates['meta']['run']).render(code=out_code)
        )
        is_passed = T['out'].generate(result) == expected_result
        print(
            f'{name} test is',
            '\033[32mpassed ✔\033[38m' if is_passed else '\033[31mfailed ×\033[38m'
        )
for _file in listdir('cases'):
    test(_file.split('.')[0])
