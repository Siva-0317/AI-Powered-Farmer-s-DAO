def ok(data=None, **kwargs):
    base = {"ok": True}
    if data is not None:
        base["data"] = data
    base.update(kwargs)
    return base

def err(msg, code=400):
    return {"ok": False, "error": msg, "code": code}, code
