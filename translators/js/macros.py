def event(el, event_name, fun):
    val = f"{el}.addEventListener({event_name}, {fun})"
    return val

def list_add(l, r):
    _type = l.get('type')
    val = f"{l.get('val')}.concat({r.get('val')})"
    return val

def div(l, r):
    val = f"Math.floor({l}/{r})"
    return val


macros = {"print": "console.log",
          "input": "prompt",
          "len": lambda obj: f"{obj}.length",
          "get_by_id": "document.getElementById",
          "event": event,
          "list_add": list_add,
          "div": div,
          ('list', 'list', '+'): list_add,
          ('any', 'any', '//'): div
}
