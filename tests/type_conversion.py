import lupa


lua_table = type(lupa.LuaRuntime().table())

def type_conversion(data, lang=''):
    if isinstance(data, lua_table):
        return list(map(type_conversion, data.values()))
    return data
