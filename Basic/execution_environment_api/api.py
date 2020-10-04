def get_id(id):
    if id!="":
        return f"document.getElementById(\"{id}\")"

def event(obj, event, func):
    return f"{obj}.addEventListener(\"{event}\", {func})"
