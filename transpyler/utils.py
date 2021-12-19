def getvar(self, name):
    path = self.namespace
    var = self.variables.get(f'{path}.{name}')
    while not var and path != '__main__':
        path = path[:path.rfind('.')]
        var = self.variables.get(f'{path}.{name}')
    return var or {}

def get_ctx(self):
    path = self.namespace
    while path != '__main__':
        var = self.variables.get(path, {})
        if var.get('type') == 'class':
            return path
        path = path[:path.rfind('.')]
    return ''

def previous_ns(self):
    if self.namespace == '__main__':
        return '__main__'
    return self.namespace[:self.namespace.rfind('.')]
