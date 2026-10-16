"""
aiida_spice.calculations

Calculations for aiida-spice.
"""

from pathlib import Path

from aiida.engine import calcfunction
from aiida.orm import List, SinglefileData, Str

from aiida_spice.utils import get_include_paths, hash_include_files


@calcfunction
def parse_includes(netlist: SinglefileData, root_path: Str | None = None) -> List:
    """Parse .include and .lib statements from a spice netlist and return a List containing each file's path and hash

    Paths are stored relative to root_path, which defaults to the current working directory if not provided. Includes
    outside root_path will cause a ValueError.
    """
    include_root = (Path.cwd() if root_path is None else Path(root_path.value)).resolve()
    included_files = get_include_paths(netlist.get_content(), include_root)
    include_hash_list = List(list=list(hash_include_files(included_files, include_root)))

    return include_hash_list
