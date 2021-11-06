def getvar(self, name):
    path = self.namespace
    var = self.variables.get(f'{path}.{name}')
    while not var and path != 'main':
        path = path[:path.rfind('.')]
        var = self.variables.get(f'{path}.{name}')
    return var or {}

def get_ctx(self):
    path = self.namespace
    while path != 'main':
        var = self.variables.get(path, {})
        if var.get('type') == 'class':
            return path
        path = path[:path.rfind('.')]
    return ''
