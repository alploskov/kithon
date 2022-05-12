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

Kithon-lang have three kinds macros

* Functions

* Attributes

* Operator overloads
  
  * Binary operators
  
  * Unary operators

Modules
-------

Types
-----

### Declaration

### Using

Node object
-----------
