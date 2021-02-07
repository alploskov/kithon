elements = {}
handlers = {}
parser = lambda el: elements.get(type(el))(el)

namespace = "main"
variables = {"main": {}}
