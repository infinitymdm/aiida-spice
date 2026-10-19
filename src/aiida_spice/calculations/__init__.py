"""
aiida_spice.calculations

Calculations for aiida-spice.
"""

from pathlib import Path

from aiida.engine import calcfunction
from aiida.orm import SinglefileData, Str

from aiida_spice import utils


@calcfunction
def parse_includes(netlist: SinglefileData, root_path: Str | None = None) -> dict[str, SinglefileData]:
    """Parse .include and .lib statements from a spice netlist into a map of SinglefileData nodes.

    :param netlist: a SinglefileData node containing a spice netlist.
    :param root_path: a Str containing a valid path. Includes in the netlist must be located under this path. Defaults
        to the current working directory.
    :raises ValueError: if a parsed include path is outside root_path.

    Parsed paths are mapped relative to root_path.
    """
    include_root = (Path.cwd() if root_path is None else Path(root_path.value)).resolve()
    include_files = utils.get_include_paths(netlist.get_content(), include_root)
    include_map = {}
    for hashed_file in utils.hash_include_files(include_files, include_root):
        key = utils.sanitize(hashed_file["path"]) + hashed_file["hash"]
        include_map[key] = SinglefileData(hashed_file["path"])
    return include_map


def parse_ip_includes(netlist: SinglefileData, pdk_path: Str) -> dict[str, str]:
    """Parse .include and .lib statements from a spice netlist into a map containing each path and hash.

    When working with intellectual property, we must not copy protected file content into the AiiDA provenance graph.
    This helper calculation builds a list of file paths (relative to pdk_path) and file hashes, ensuring provenance
    while protecting IP.
    """
    # Hash PDK and add its identifier to the include_map
    # Recursively read includes. Catch paths outside pdk_path and skip those files (but parse their includes)
    pass  # TODO
