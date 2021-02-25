from . utils import transpyler_type


def what_macro(name):
    if type(name) == tuple:
        name = (transpyler_type(name[0]), transpyler_type(name[1]), name[2])
        print(name)
        ol_data = [(name[0], name[1], name[2]),
                   (name[0], name[1], 'any'),
                   (name[0], 'any', name[2]),
                   ('any', 'any', name[2]),
                   ('any', 'any', 'any')
                   ]
        for i in ol_data:
            if ol := macros.get(i):
                return ol
    elif name in macros:
        name = macros.get(name)
        return name

def macro(name, args):
    def get_val(val):
        val = val.value
        if type(val) == str:
            val = '"'+val+'"'
        val = str(val)
        return val
    args = str(tuple(map(get_val, args)))
    return {'val': eval(f"name{args}")}

macros = {}
