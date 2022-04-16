Kithon
======

About
-----

**Kithon** is a project that provides the ability to translate python and python-family language such as
[hy-lang](https://github.com/hylang/hy) and [coconut](https://github.com/evhub/coconut)
into human-readable code in any other programming languages.

[Try out the web demo](https://alploskov.github.io/kithon/demo/)

or 

```bash
pip install kithon
echo "print('Hello World')" > test.py
kithon gen --js test.py
```

Output:

```js
console.log("Hello World");
```

---

Differences form Brython, IronPython, etc.
------------------------------------------

Kithon it is translator, it generate code in target language and Brython, Ironpython etc. are implementations of python, they run python program in target platform.

Kithon may have better integration with target platform, but this may affect differences with python.

---

Differences form Nuitka, Transcrypt, etc.
-----------------------------------------

Kithon have multiple backends trying to generate cleaner and idiomatic code.

---

Differences form Python
-----------------------

Kithon depends on the target language for example this python code.

```python
'1' + 1
```

compiles to following js code 

```js
"1" + 1; // "11"
```

but in CPython it is error

```python
'1' + 1 # TypeError: can only concatenate str (not "int") to str
```
