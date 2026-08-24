def sanitize(name: str) -> str:
    mappings = str.maketrans({"(": "_", ")": None, "/": "__", ".": "__", "#": None})
    return name.translate(mappings)
