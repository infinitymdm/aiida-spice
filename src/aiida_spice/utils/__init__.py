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


def get_include_paths(netlist: str, included_files: set[Path] = set()) -> set[Path]:
    """Return parent folders of .include and .lib arguments from the input netlist

    :param netlist: The string content of a netlist
    :param included_files: A set of previously-parsed include files (prevents duplicate parsing during recursion)
    :returns: A complete set of paths to files referenced in the input netlist.
    """
    pattern = re.compile(r'^\s*\.(?:include|lib)\s+["\']?(.*?)["\']?(?:\s|$)', re.IGNORECASE)

    for line in netlist.split("\n"):
        pattern_match = pattern.search(line)
        if pattern_match:
            # Extract path
            include_path = Path(pattern_match.group(1).split()[0])

            # Resolve relative paths
            if not include_path.is_absolute():
                include_path = include_path.resolve()

            # If not already included, add the resolved file path and check it for includes
            if include_path not in included_files:
                included_files.add(include_path)
                included_files = get_include_paths(include_path.read_text(), included_files)

    return included_files
