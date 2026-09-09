"""
aiida_spice.calculations

Calculations for aiida-spice.
"""

from aiida.engine import calcfunction
from aiida.orm import FolderData, SinglefileData

from aiida_spice.utils import get_include_paths


@calcfunction
def parse_includes(netlist: SinglefileData) -> FolderData:
    """Parse .include and .lib statements from a spice netlist and return a FolderData populated with each file path"""
    include_paths = get_include_paths(netlist.get_content())
    include_folder = FolderData()
    for path in include_paths:
        include_folder.put_object_from_file(path.resolve(), path.name)
    return include_folder
