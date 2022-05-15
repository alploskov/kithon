**Kithon** is a project that provides the ability to translate python and python-family language such as
[hy-lang](https://github.com/hylang/hy) and [coconut](https://github.com/evhub/coconut)
into human-readable code in any other programming languages.

**[Try out the web demo](https://alploskov.github.io/kithon-site/demo/)** or install locally: `pip install kithon`. Then you can use generation to `js` or `go` or create custom transpiler.

**Example**

```python
# main.py

def main():
    print('Hello, Kithon')

main()
```
---
`kithon gen --to js main.py`, output:
```js
function main() {
    console.log("Hello, Kithon");
}
main();
```
---
`kithon gen --to go main.py`, output:
```go
package main
import (
	"fmt"
)

func main() {
    fmt.Println("Hello, Kithon")
}
```

For what?
---------

For use python where we can't. For example in browser(js), embedded scripting(mostly lua).
Or make python program faster by translating to go, c++, rust, nim or julia.
Also for supporting program written on in unpopular programming languages (very new or vice versa)

How it works?
-------------

Kithon uses a dsl based on yaml and jinja to apply the rules described on it to the nodes of the ast tree. 
Using this dsl you can add new languages or extensions to those already added.

Status
------

The project is under active development.
Now the ability to add translation of basic python constructs into any other language(in this repo js and go only) is supported.

There are plans to develop a number of supported languages and expand support for python syntax

Similar projects
----------------

* [py2many](https://github.com/adsharma/py2many)
* [pseudo](https://github.com/pseudo-lang/pseudo)
