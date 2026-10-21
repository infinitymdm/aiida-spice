"""
aiida_spice.calculations

Calculations for aiida-spice.
"""

from pathlib import Path

from aiida.engine import calcfunction
from aiida.orm import Dict, SinglefileData, Str

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
    include_map = {}
    include_metadata = {"path": str(include_root)}
    include_files = utils.get_include_paths(netlist.get_content(), include_root)
    for hashed_file in utils.hash_include_files(include_files, include_root):
        key = utils.sanitize(hashed_file["path"]) + "__" + hashed_file["hash"]
        include_metadata[key] = {"path": hashed_file["path"]}
        include_map[key] = SinglefileData(include_root / hashed_file["path"])
    include_map["metadata"] = Dict(dict=include_metadata)
    return include_map


@calcfunction
def parse_ip_includes(netlist: SinglefileData, ip_root: Str) -> dict[str, Dict]:
    """Parse .include and .lib statements from a spice netlist into a map containing each path and hash.

    :param netlist: a SinglefileData node containing a spice netlist.
    :param ip_root: a Str containing a valid path. All files under ip_root are assumed to be protected IP.

    When working with intellectual property, we must not copy protected file content into the AiiDA provenance graph.
    This helper calculation builds a dict of file paths (relative to ip_root) and file hashes, ensuring provenance
    while protecting IP.

    In addition to storing the hash & path of each included file, the ip_root directory itself is recursively hashed.
    This means that changing any file in, for example, a PDK directory will cause the ip_root directory hash to change.
    This should be very helpful as a version control measure to ensure that spice simulations are run against a
    uniquely identifiable version of an IP library.
    """
    # Hash ip_root and add its identifier to the include_map
    ip_path = Path(ip_root.value).resolve()
    ip_identifier = utils.hash_pdk(ip_path)
    ip_map = {"ip_metadata": Dict(dict={"path": ip_path.as_posix(), "hash": ip_identifier})}

    ip_files = utils.get_include_paths(netlist.get_content(), ip_path)
    # TODO: Catch paths outside pdk_path and skip those files (but parse their includes)
    # TODO: Figure out what to do in the case that there are multiple independent IP paths
    for hashed_ip in utils.hash_include_files(ip_files, ip_path):
        key = utils.sanitize(hashed_ip["path"]) + "__" + hashed_ip["hash"]
        ip_map[key] = Dict(dict=hashed_ip)
    return ip_map
