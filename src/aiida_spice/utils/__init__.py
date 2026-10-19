"""
aiida_spice.utils

Utilities and helper functions for aiida-spice.
"""

import hashlib
import re
from pathlib import Path
from typing import Generator


def sanitize(name: str) -> str:
    """Convert input strings to database-compatible keys.

    :param name: an input string to sanitize.
    :returns: a sanitized version of the input string."""
    mappings = {"(": "_", ")": None, "/": "__", ".": "__", "#": None}
    return name.translate(str.maketrans(mappings))


_include_pattern = re.compile(r'^\s*\.(?:include|lib)\s+["\']?(.*?)["\']?(?:\s|$)', re.IGNORECASE)


def get_include_paths(
    netlist: str, include_root: Path, base_dir: Path | None = None, included_files: set[Path] | None = None
) -> set[Path]:
    """Return parent folders of .include and .lib arguments from the input netlist

    :param netlist: the string content of a netlist
    :param include_root: a common root folder that all includes must be located under
    :param base_dir: the current working directory (under include_root) which files are resolved against. If omitted,
                     same as include_root.
    :param included_files: a set of previously-parsed include files (prevents duplicate parsing during recursion)
    :raises ValueError: if a parsed include is not in include_root
    :returns: A complete set of paths to files referenced in the input netlist.
    """
    if included_files is None:
        included_files = set()

    # Make sure we have the fully qualified path to include_root
    if not include_root.is_absolute():
        include_root = include_root.resolve()

    if base_dir is None:
        base_dir = include_root
    elif base_dir != include_root and include_root not in base_dir.parents:
        raise ValueError(f"Base directory '{base_dir!s}' not found under designated root '{include_root!s}'")

    for line in netlist.split("\n"):
        pattern_match = _include_pattern.search(line)
        if pattern_match:
            # Extract path
            include_path = Path(pattern_match.group(1).split()[0])

            # Check against base_dir first
            if not include_path.is_absolute():
                include_path = base_dir / include_path

            # Make sure the parsed path is under include_root
            include_path = include_path.resolve()
            if include_root not in include_path.parents:
                raise ValueError(f"Path '{include_path!s}' not found under designated root '{include_root!s}'")
                continue  # Skip this path if the error gets handled

            # If not already included, add the resolved file path and check it for includes
            if include_path not in included_files:
                included_files.add(include_path)
                included_files = get_include_paths(
                    include_path.read_text(), include_root, include_path.parent, included_files
                )

    return included_files


def hash_include_files(
    included_files: set[Path], include_root: Path, hash_algorithm: str = "sha3_256"
) -> Generator[dict, None, None]:
    """For each included file, yield the path and hash as a dict

    :param included_files: a set of resolved absolute paths.
    :param include_root: a folder Path which all included_files must fall under.
    :param hash_algorithm: the name of a hash algorithm to use, as defined in hashlib. Defaults to sha3_256.
    """
    for file in included_files:
        file_path = file.relative_to(include_root).as_posix()
        with open(file, "rb") as f:
            file_hash = hashlib.file_digest(f, hash_algorithm).hexdigest()
        yield {"path": file_path, "hash": file_hash}


def hash_pdk(pdk_root: Path, hash_algorithm: str = "sha3_256") -> str:
    """Compute the hash of the PDK located at pdk_root.

    :param pdk_root: the root directory of the PDK.
    :param hash_algorithm: the name of a hash algorithm to use, as defined in hashlib. Defaults to sha3_256.

    This method computes the content-based hash of a PDK as follows:
    1. Create an alphabetically sorted manifest of all files under pdk_root by recursively walking the directories.
    2. Compute the hash of each file.
    3. Combine all hashes into a single stream and return the hash of that stream.
    """
    files = pdk_root.rglob("*")
    hash_function = hashlib.new(hash_algorithm)
    for file in sorted(files):
        with open(file, "rb") as f:
            hash_function.update(hashlib.file_digest(f, hash_algorithm).hexdigest())
    return hash_function.hexdigest()
