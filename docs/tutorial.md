The aim of this tutorial is to build python -> [wren](https://wren.io) transpiler using [kithon](https://github.com/alploskov/kithon).

First, install kithon. if you haven’t done this already.

```
pip install kithon
```

By default, kithon uses templates that generate python code. When you create a new translator, you should create a template for constructs that is different from python

### Base

Wren is c-like scripting language, on it we can use template for c-like languages with this command

```
kithon new --base C wren
```

Now we have dirrectory wren with the folowing content:

```
wren
├── core.tp
├── macros.tp
├── libs/
└── objects/
```

If you don't change any `core.tp`, you will receive code in c-like language

### Wren-specifc constructions

If statements in C and Wren have same syntax and we don't need change templates `if`, `elif`, `else` and other matching with C.

Some templates match with python for example `expr`, `break`, `continue` on it we must delete they from `core.tp`. 

Variables and functions defenition don't match with C or python than we must rewrite they template:

```yaml
# var defenition

new_var: &new-assign "var {{var}} = {{value}}"
new_attr: *new-assign
```

```yaml
# functions defenition
func: |-
  var {{name}} = Fn.new {{'('}}|{{args|join(', ')}}|{% for st in body.parts.body %}
  {{'    '*nl}}{{st}}{% endfor %}
  {{'    '*(nl-1)}}}
```

Some constructions undefined in C and has different from python for example `for`:

```yaml
for: "for ({{var}} in {{obj}}) {{body}}"
```

Full code with other core elements may be found in this [file](https://github.com/alploskov/kithon/blob/master/translators/wren/core.tp) 

### Macros

Next step is add macros for example `print` has following macro:

```yaml
print:
  code: "System.printAll([{{args|join(', \" \", ')}}])"
```

It use wren standart function `System.printAll` and if we transpile following code:

```python
print('Hello, Kithon', 123)
System.printAll([1, 2, 3])
```

We get this:

```python
System.printAll(["Hello, Kithon", 123])
System.printAll([1, 2, 3])
```

Because we can use we can use python functions as macros or built-in functions of the target language

### Libs and embedded objects

Last step is add libraries, most often, kithon-libraries are a projection onto similar libraries of the target language.

In this tutorial we create set of macros for binding subset of python library `random` to [wren-random](https://wren.io/modules/random/random.html)

First in `libs/` create file `random.tp` and write next code

```yaml
random:
  alt_name: "Random.new()"
  import_code: "import \"random\" for Random"
  type: {module: ['random']}
```

We create prototype of our module and we can write following code:

```python
import random

random.int()
```

that compiles to:

```
import "random" for Random
Random.new().int()
```

But we wanna use python names. Python analog for wren `int` method int is `randint`, on it modifying our code:

```yaml
random:
  alt_name: "Random.new()"
  import_code: "import \"random\" for Random"
  type: {module: ['random']}

```
