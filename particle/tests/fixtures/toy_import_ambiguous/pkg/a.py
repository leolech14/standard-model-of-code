# Import that could be stdlib or local - ambiguous
import json  # This is stdlib, but if there was a local json.py, it would be ambiguous

def process():
    return json.dumps({})
