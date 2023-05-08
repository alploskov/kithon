`if` Statements
---------------
for implementation `if` Statements the following templates are used:

`if` and `elif` with parametrs:

  * `condition` - is node with any python expression
  * `body` - array of nodes with any python block
  * `els` - node with `elif` or `else` block

`else` with parametr `body`

for example `js` implementation:
```yaml
if: "if ({{condition}}) {{body}} {{els}}"

elif: "else if ({{condition}}) {{body}} {{els}}"

else: "else {{body}}"
```

`for` Statements
----------------


The `range()` Function
--------------------


`while` Statements
----------------


