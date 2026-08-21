import re
from pathlib import Path


def get_include_paths(netlist: Path, included_files: set[Path] = set()) -> set[Path]:
    """Return parent folders of .include and .lib arguments from the input netlist"""
    netlist_path = Path(netlist).resolve()
    pattern = re.compile(r'^\s*\.(?:include|lib)\s+["\']?(.*?)["\']?(?:\s|$)', re.IGNORECASE)

    with open(netlist_path, "r") as f:
        for line in f:
            pattern_match = pattern.search(line)
            if pattern_match:
                # Extract path
                include_path = Path(pattern_match.group(1).split()[0])

                # Resolve relative paths
                if not include_path.is_absolute():
                    include_path = (netlist_path.parent / include_path).resolve()

                # If not already included, add the resolved file path and check it for includes
                if include_path not in included_files:
                    included_files.add(include_path)
                    included_files = get_include_paths(include_path, included_files)

    return included_files
