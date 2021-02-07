def what_macro(name):
    if type(name) == tuple:
        if (name[0], name[1], name[2]) in macros:
            return macros.get((name[0], name[1], name[2]))
        elif (name[0], name[1], 'any') in macros:
            return macros.get((name[0], name[1], 'any'))
        if ('any', 'any', name[2]) in macros:
            return macros.get(('any', 'any', name[2]))
        if ('any', 'any', 'any') in macros:
            return macros.get(('any', 'any', 'any'))
    elif name in macros:
        name = macros.get(name)
        return name

def get_val(val):
    val = val.value
    if type(val) == str:
        val = '"'+val+'"'
    val = str(val)
    return val

def macro(name, args, keywords):
    kw = str(tuple(map(get_val, args)))
    return {'type': 'None', 'val': eval(f"name{args}")}

macros = {}
