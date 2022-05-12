Generate
--------

```
kithon gen [--help] [-t] [-m]
	       [-l] [--to] [-o]
           [source]
```
**Arguments**

```
source                Path to the python or coconut/hy file to compile
```

**Options**

```bash
--help                Show help message and exit

-t, --templ           Names of template file

-m, --macro TEXT      Macro in yaml format

-o, --out FILENAME    Output file  [default: (stdout)]

-l, --lang TEXT       Marking the entrance language (py, hy, coco)
	                  [default: (Determined by the filename)]

--to TEXT             Dirrectory with templates file or name of target language

-w, --watch           Regeneration when changing
```

Create new translator
---------------------

```
kithon new [--help] [-g] [--base] [name]
```

**Arguments**

```
name                Name of new language, name must be unique
```

**Options**

```bash
--help                Show help message and exit

-g, --global          Make transpiler globally accessible

--base                Use template for new language (C, lisp, py)
```

REPL
----

Kithon has repl, it translates python expressions and sends resulting code to repl of choosen language

```
kithon repl [--help] [-t] [-m] [--to] [--sep] [--repl]
```

```bash
--help                Show help message and exit

-t, --templ           Names of template file

-m, --macro TEXT      Macro in yaml format

--to TEXT             Dirrectory with templates file or name of target language

--repl TEXT           Name of repl

--sep TEXT            Input prompt including spaces

--help                Show this message and exit.
```
