# transPYler
transPYler is a project that provides the ability to translate Python into any programming language.

# Usage
### CLI
tpy [OPTIONS] [_FILE]

**Arguments:**

  [_FILE]  Name of file for transpilation  [default: index.py]

**Options:**

  --tmpl Names of template file (templates for js translators/js)

  --macr Names of macros file (macros for js translators/js/macros.tp)

  --out Output file  [default: stdout]

**Example:**

tpy --tmpl expr.tp --tmpl blocks.tp --macr macros.tp --out hi.js hello_world.py

### Build system
in development