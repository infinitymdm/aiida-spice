def sanitize(name: str) -> str:
    """Convert input strings to database-compatible keys.

    :param name: an input string to sanitize.
    :returns: a sanitized version of the input string."""
    mappings = {"(": "_", ")": None, "/": "__", ".": "__", "#": None}
    return name.translate(str.maketrans(mappings))
