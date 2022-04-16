CLI
===

Generate
--------

```
kithon gen [--help] [-t] [-m] [-l]
           [--target] [--js] [--go] [-o]
           [source]
```

### Positional Arguments

```
source                Path to the python or coconut/hy file to compile
```

### Optional Arguments

```
--help                Show help message and exit
-t, --templ           Names of template file
-o, --out FILENAME    Output file  [default: (stdout)]
--js                  Used for chose javascript as target language
--go                  Used for chose golang as target language
-l, --lang TEXT       Marking the entrance language (py, hy, coco)
	                  [default: (Determined by the filename)]
--target TEXT         Dirrectory with templates file

```

Create new translator
---------------------
