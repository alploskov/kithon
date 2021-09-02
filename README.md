transPYler
===========

transPYler is a project that provides the ability to translate python and python-family language such as [hy-lang](https://github.com/hylang/hy) and [coconut](https://github.com/evhub/coconut) into any other programming languages.


[Usage](#usage)
---------------
### CLI
tpy [OPTIONS] [FILE]

[Arguments:](#args)

  FILE  Name of file for transpilation  [default: index.py]

[Options:](#opt)

  -t, --templ FILENAME            Names of template file

  -m, --macros FILENAME           Names of macros file

  -o, --out FILENAME              Output file  [default: (stdout)]

  -l, --lang TEXT                 Marking the entrance language (py, hy)
                                  [default: Вetermined by the filename]

  --help                          Show this message and exit.


```bash
tpy -t expr.tp -t blocks.tp -m macros.tp -o hello.js hello_world.py
```
