Kithon is a cli tool for transpile python source code

Usage:

`kithon <command> [OPTIONS] [file/directory]`

The commands are: 
```
 gen       Transpile python program into target language
 run       Transpile and run python program
 repl      Start repl that sends translating python expression to repl of target language 
 new       Create new transpiler by template
```

Build options
-------------

The build options are shared by the gen, run and repl commands:

```
-t, --templ           Names of template file

-m, --macro TEXT      Macro in kithon-lanf

-l, --lang TEXT       Marking the entrance language (py, hy, coco)
	                  [default: (Determined by the filename)]

--to TEXT             Name of target language
```


Gen options
-----------

```
-o, --out FILENAME    Output file  by default: stdout for files and input directory for directories

-w, --watch           watch a file/directory and recompile on changes
```


Run options
-----------
```
--command      Template of run command by default get from meta
```

REPL options
------------

```
--repl        Name of repl by default get from meta

--prompt      Input prompt including spaces by default get from meta
```

Create new translator
---------------------

```
-g, --global      Make transpiler globally accessible

--base            Use template for new language (C, lisp, py...)
```

Meta
----

Meta is dictionary that use in kithon tools

```yaml
meta: 
  repl:
    name: "Command to run repl of target language"
    prompt: "Input prompt including spaces"
  ext: "Extension for create files in package compilation"
  run: "Template of run command"
```

Example, meta for JavaScript:

```yaml
meta: 
  repl:
    name: "node"
    prompt: "> "
  ext: "js"
  run: "node -e '{{code}}'"
```
