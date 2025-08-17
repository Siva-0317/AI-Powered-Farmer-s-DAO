# backend/utils.py
from flask import jsonify

def ok(data=None, **kwargs):
    base = {"ok": True}
    if data is not None:
        base["data"] = data
    base.update(kwargs)
    return base

def err(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code
