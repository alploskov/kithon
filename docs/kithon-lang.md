Kithon-lang
===========

**Kithon-lang** is DSL based on yaml and jinja2 used to create syntax translation rules and macros.

The Kithon-lang syntax reflects this goal and its basic building blocks are:

* The **property** which is an identifier, that is a human-readable name, that defines which feature is considered.

* The **value** which describe how the feature must be handled by the engine.

Core elements
-------------

If name of **core element** doesn't match with name of any macro then using following construction

```yaml
name_of_element: "Jinja2 code"
```

else using next construction or write macro and core element in different files

```yaml
name_of_element:
  tmp: "Jinja2 code"
  macro_field: ...
```

For disable element use "no" as value in generated code of this element will be empty string

```yaml
name_of_element: no
```

Macros
------

**Macro** is functions(or attributes, operators) which change self name or put generated code in compile time, 
also they used to types definition.

Kithon-lang have three kinds macros this macros different by selector and set of valid fields.

### Names

Selector for this macros is just name in python

Valid fields:

**alt_name**: "name"

Replace selector by name example, for replace `prtin` to `console.log` using following code:

```yaml
print:
  alt_name: "console.log"
```
---

**code**: "Jinja2 code"

Template that using instead of `call` example, `len` macro: 

```yaml
len:
  code: "{{args[0]}}.length"
```

**args**: ["arg_name1", ...]

Used for naming arguments in macros:

```yaml
len:
  args: ["object"]
  code: "{{object}}.length"
```

**type**: [type](#type-using)

Type for name in this [format](#type-using)

```yaml
a:
  type: int
```
```python
b = a # now b has int type
```

**ret_type**: [type](#type-using)

Returned type for name in this [format](#type-using)
```yaml
a:
  ret_type: int
```
```python
b = a() # now b has int type
```

**decorate**: "Jinja2 code"

Template that using instead of `func`, `method` or `class` only for top level decorator other decorators can only change name

### Attributes

### Operator overloads
  
Binary operators
  
Unary operators

Types
-----

### Declaration

### <a name="type-using"></a>Using

Node object
-----------
