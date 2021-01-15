def list_add(l, r):
    val = f"{l.get('val')}.concat({r.get('val')})"
    return {"type": 'list', "val": val}

operator_overloading = {('list', 'list', "+"): list_add,
}
