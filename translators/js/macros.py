from transPYler import macro, objects


@macro('event')
def event(el, event_name, fun):
    val = f"{el}.addEventListener({event_name}, {fun})"
    return val

@macro('list_add')
def list_add(l, r):
    _type = l.get('type')
    val = f"{l.get('val')}.concat({r.get('val')})"
    return {'val': val, 'type': l.get('type')}

@macro('div')
def div(l, r):
    val = f"Math.floor({l.get('val')}/{r.get('val')})"
    return {'val': val, 'type': 'int'}

@macro('check')
def check(_id):
    return {'val': f"document.getElementById({_id.get('val')}).checked", 'type': 'bool'}

def create_list(_list, _type):
    return {'val': _list.get('val'), 'type': f"list<{_type.get('val')}>"}

macro({"print": "console.log",
       "input": "prompt",
       "request": "await r",
       "len": lambda obj: {'val': f"{obj.get('val')}.length", 'type': 'int'},
       "get_by_id": {'type': 'dom',
                     'val': 'document.getElementById'
                     },
       "interval": "setInterval",
       "url_param": {'val': "new URL(window.location.href).searchParams.get",
                     'type': 'str'
                     },
       ('list', 'list', '+'): list_add,
       ('any', 'any', '//'): div,
       ('list', 'type', '*'): create_list,
       ('dom', 'any', '<='): lambda l, r: {'val': f"{l.get('val')}.innerHTML = {r.get('val')}"}
})

objects({"list": {"index": {"val": "indexOf"},
                  "append": {"val": "push"}
                  },
         "math": {"__name__": "Math",
                  "pi": {'val': 'PI',
                         'type': 'float'
                         }
                  },
         "json": {"__name__": "JSON",
                  "dumps": {'val': 'stringify'},
                  "loads": {'val': 'parse'}
                  }
})
