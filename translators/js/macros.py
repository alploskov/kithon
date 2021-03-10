from transPYler import macro


@macro('event')
def event(el, event_name, fun):
    val = f"{el}.addEventListener({event_name}, {fun})"
    return val

@macro('list_add')
def list_add(l, r):
    _type = l.get('type')
    val = f"{l.get('val')}.concat({r.get('val')})"
    return {'val': val}

@macro('div')
def div(l, r):
    val = f"Math.floor({l.get('val')}/{r.get('val')})"
    return {'val': val}

@macro('check')
def check(_id):
    return {'val': f"document.getElementById({_id}).checked", 'type': 'bool'}

macro({"print": "console.log",
          "input": "prompt",
          "len": lambda obj: f"{obj}.length",
          "get_by_id": {'type': 'dom',
                        'val': 'document.getElementById'
                        },
          "interval": "setInterval",
          "url_param": {'val': "new URL(window.location.href).searchParams.get",
                        'type': 'str'
                        },
          ('list', 'list', '+'): list_add,
          ('any', 'any', '//'): div,
          ('dom', 'any', '<='): lambda l, r: {'val': f"{l.get('val')}.innerHTML = {r.get('val')}"}
})
