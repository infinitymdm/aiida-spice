"""
aiida_spice.utils

Utilities and helper functions for aiida-spice.
"""

import re
from pathlib import Path


def sanitize(name: str) -> str:
    """Convert input strings to database-compatible keys.

    :param name: an input string to sanitize.
    :returns: a sanitized version of the input string."""
    mappings = {"(": "_", ")": None, "/": "__", ".": "__", "#": None}
    return name.translate(str.maketrans(mappings))


_include_pattern = re.compile(r'^\s*\.(?:include|lib)\s+["\']?(.*?)["\']?(?:\s|$)', re.IGNORECASE)


def get_include_paths(netlist: str, include_root: Path, included_files: set[Path] | None = None) -> set[Path]:
    """Return parent folders of .include and .lib arguments from the input netlist

    :param netlist: the string content of a netlist
    :param include_root: a common root folder that all includes must be located under
    :param included_files: a set of previously-parsed include files (prevents duplicate parsing during recursion)
    :raises ValueError: if a parsed include is not in include_root
    :returns: A complete set of paths to files referenced in the input netlist.
    """
    if included_files is None:
        included_files = set()

    if not include_root.is_absolute():
        include_root = include_root.resolve()

    for line in netlist.split("\n"):
        pattern_match = _include_pattern.search(line)
        if pattern_match:
            # Extract path
            include_path = Path(pattern_match.group(1).split()[0])

            # Resolve relative paths
            if not include_path.is_absolute():
                include_path = include_path.resolve()

            # Make sure the parsed path is under include_root
            if include_root not in include_path.parents:
                raise ValueError("Path '{include_path!s}' not found under designated root '{include_root!s}'")
                continue  # Skip this path if the error gets handled

            # If not already included, add the resolved file path and check it for includes
            if include_path not in included_files:
                included_files.add(include_path)
                included_files = get_include_paths(include_path.read_text(), include_root, included_files)

    return included_files
