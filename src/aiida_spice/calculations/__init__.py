"""
aiida_spice.calculations

Calculations for aiida-spice.
"""

from pathlib import Path

from aiida.engine import calcfunction
from aiida.orm import FolderData, SinglefileData, Str

from aiida_spice.utils import get_include_paths


@calcfunction
def parse_includes(netlist: SinglefileData, root_path: Str | None = None) -> FolderData:
    """Parse .include and .lib statements from a spice netlist and return a FolderData populated with each file path

    Paths are stored relative to root_path, which defaults to the current working directory if not provided. Includes
    outside root_path will cause a ValueError.
    """
    if root_path is None:
        include_root = Path.cwd().resolve()
    else:
        include_root = Path(root_path.value)

    include_folder = FolderData()
    for path in get_include_paths(netlist.get_content(), include_root):
        include_folder.put_object_from_file(path.resolve(), path.name)
    return include_folder
