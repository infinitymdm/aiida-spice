import hashlib
from pathlib import Path

from aiida.engine import CalcJob
from aiida.orm import ArrayData, Dict, List, SinglefileData


class SpiceCalculation(CalcJob):
    """Abstract generic spice CalcJob. Defines common error codes and I/O."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define exit codes
        spec.exit_code(430, "ERROR_NO_RETRIEVED_FOLDER", "Failed to parse the retrieved folder")
        spec.exit_code(440, "ERROR_MISSING_RAWFILE", "Output rawfile not present in retrieved results")
        spec.exit_code(441, "ERROR_MISSING_STDOUT", "stdout transcript not present in retrieved results")
        spec.exit_code(450, "ERROR_PARSING_RAWFILE", "Failed to parse SPICE3 rawfile")

        # Define inputs
        spec.input("netlist", valid_type=SinglefileData, help="The SPICE netlist file.")
        spec.input_namespace(
            "includes",
            valid_type=(SinglefileData, Dict),
            dynamic=True,
            required=False,
            help="Files referenced in the SPICE netlist",
        )
        spec.input("analyses", valid_type=List, help="Analyses to run during simulation.")
        spec.input("parameters", valid_type=Dict, required=False, help="Simulation parameters to set with .param.")
        spec.input("options", valid_type=Dict, required=False, help="Simulation options to set with .option.")

        # Define parser metadata
        spec.input("metadata.options.stdout_name", valid_type=str, default="stdout.txt")

        # Define expected outputs
        spec.output("metadata", valid_type=Dict, help="Parsed run metadata.")
        spec.output("measurements", valid_type=Dict, help="Parsed measurement results, if .meas directives were used")
        spec.output("trace_data", valid_type=ArrayData, help="Parsed vectors of voltage, current, etc.")

    def stage_includes(self, folder, calcinfo):
        """Stage includes for local copy or provenance exclude as appropriate"""
        if not calcinfo.local_copy_list:
            calcinfo.local_copy_list = []
        if not calcinfo.provenance_exclude_list:
            calcinfo.provenance_exclude_list = []
        if "includes" in self.inputs:
            includes = self.inputs.includes
            for key, node in includes.items():
                if key == "metadata":
                    continue
                if isinstance(node, SinglefileData):
                    node_path = includes.metadata[key]["path"]
                    calcinfo.local_copy_list.append((node.uuid, node.filename, node_path))
                elif isinstance(node, Dict):
                    stage_ip_include(folder, calcinfo, self.inputs.includes.metadata.ip, node)


def stage_ip_include(folder, calcinfo, ip_metadata, ip_file, hash_algorithm="sha3_256"):
    """Stage included IP files by copying them to the sandbox folder and adding them to the provenance exclude list."""
    ip_name = ip_file["ip"]
    ip_root_path = Path(ip_metadata[ip_name]["path"]).resolve()
    ip_file_path = Path(ip_file["path"])

    # Ensure the ip file path isn't absolute
    if ip_file_path.is_absolute() or not ip_file_path.parts:
        raise ValueError("IP include path must be relative to the IP root")

    # Get the full path to the source file
    source = (ip_root_path / ip_file_path).resolve()
    if not source.is_relative_to(ip_root_path):
        raise ValueError("IP include path resolves outside the IP root")

    # Copy the file into the sandbox folder
    destination = ip_file_path
    target_folder = folder.get_subfolder(destination.parent.as_posix(), create=True)
    target_folder.insert_path(str(source), dest_name=destination.name, overwrite=False)

    # Verify the content hash of the staged file
    with folder.open(destination.as_posix(), "rb") as staged_file:
        staged_hash = hashlib.file_digest(staged_file, hash_algorithm).hexdigest()
    if staged_hash != ip_file["hash"]:
        raise ValueError(f"IP include hash mismatch: {ip_file_path}")

    # Exclude the staged file from provenance
    calcinfo.provenance_exclude_list.append(destination.as_posix())
