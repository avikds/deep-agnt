import json

def parse_model_json(reply):
    """Return the JSON object in a model's reply, or None if there isn't one."""
    if not isinstance(reply, str):
        return None

    decoder = json.JSONDecoder()

    for i, char in enumerate(reply):
        if char != "{":
            continue

        try:
            obj, _ = decoder.raw_decode(reply, i)
            if isinstance(obj, dict):
                return obj
        except json.JSONDecodeError:
            continue

    return None
