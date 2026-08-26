import hashlib
import re
from pathlib import Path


def get_include_paths(netlist: Path, included_files: set[Path] = set()) -> set[Path]:
    """Return parent folders of .include and .lib arguments from the input netlist

    :param netlist: The path to an existing netlist file
    :param included_files: A set of previously-parsed include files (prevents duplicate parsing during recursion)
    :returns: A complete set of paths to files referenced by the input netlist.
    """
    netlist_path = Path(netlist).resolve()
    pattern = re.compile(r"^\s*\.(?:include|inc|lib)\s+([^\s]+)", re.IGNORECASE)

    with open(netlist_path, "r") as f:
        for line in f:
            pattern_match = pattern.search(line)
            if pattern_match:
                # Extract path
                include_path = Path(pattern_match.group(1).split()[0])
                if not include_path.is_file():
                    continue

                # Resolve relative paths
                if not include_path.is_absolute():
                    include_path = (netlist_path.parent / include_path).resolve()

                # If not already included, add the resolved file path and check it for includes
                if include_path not in included_files:
                    included_files.add(include_path)
                    included_files = get_include_paths(include_path, included_files)

    return included_files


def separate_ip_files(files: set[Path], ip_folders: set[Path]) -> tuple[set[Path], set[Path]]:
    """Given a set of files, identify which are in ip_folders and separate them.

    :param files: A set of existing file Paths to check
    :param ip_folders: A set of existing folders which should be treated as IP
    :returns: Two sets of existing file Paths: IP files and non-IP files
    """
    ip_files = set()

    ip_dirs = {path.resolve() for path in ip_folders}
    for path in files:
        for folder in ip_dirs:
            if path.resolve().is_relative_to(folder):
                ip_files.add(path)
                break

    return ip_files, files - ip_files


def hash_ip_files(ip_files: set[Path], ip_folder: Path) -> list[tuple[str, str]]:
    """Given a set of ip files, compute the hash of each file using SHA256.

    :param ip_files: A set of existing file Paths to hash
    :param ip_folder: The common parent folder of all ip_files values
    :returns: a list of 2-tuples of filename relative to ip_folder and hash
    """
    file_hashes = {}
    ip_folder = ip_folder.resolve()
    for path in ip_files:
        resolved = path.resolve()
        with open(resolved, "rb") as f:
            digest = hashlib.file_digest(f, "sha256")
            file_hashes[str(resolved.relative_to(ip_folder))] = digest.hexdigest()
    return [(f, h) for f, h in file_hashes.items()]
