[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/alploskov/kithon/blob/master/LICENSE.txt) <a href="https://pypi.org/project/kithon" target="_blank"> <img src="https://img.shields.io/pypi/v/kithon?color=%2334D058&label=pypi%20package" alt="Package version"></a> ![lines of code](https://tokei.rs/b1/github/alploskov/kithon)

**Kithon** is universal python transpiler for speedup python programs and use python in other platform, such as browser or game engines, it focused on generating human readable code and integration with tools of target languages including cli and libraries

**[Try out the web demo](https://alploskov.github.io/kithon-site/demo/)**

Quick start
------------
First, you install it:

```text
$ pip install kithon[all]
```

Then, you translate your code to target language, in this example JavaSctipt

```text
$ kithon gen --to js hello_world.py
```

Or translate and run resulting code

```text
$ kithon run --to go hello_world.py
```
It should be clear what to do. If not, ask us in our [Telegram chat](https://t.me/kithon).

How to Contribute
-----------------

First, install `python>=3.9`, `poetry`
