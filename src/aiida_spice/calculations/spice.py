from aiida.engine import CalcJob
from aiida.orm import ArrayData, Dict, FolderData, List, RemoteData, SinglefileData


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
        spec.input("includes", valid_type=FolderData, required=False, help="Files referenced in the SPICE netlist")
        spec.input_namespace(
            "ip",
            dynamic=True,
            required=False,
            validator=validate_ip_inputs,
            help="IP folders and files whose content must not be copied into the provenance graph.",
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

    def stage_includes(self, calcinfo):
        """Stage includes for local copy"""
        if "includes" in self.inputs:
            inc_node = self.inputs.includes
            for filename in inc_node.list_object_names():
                calcinfo.local_copy_list.append((inc_node.uuid, filename, filename))

    def stage_ip_files(self, calcinfo):
        """Check whether the input ip groups contain valid paths"""
        if "ip" in self.inputs:
            hash_check_script = ["# IP file hash checks"]
            for label, ip_group in self.inputs.ip.items():
                folder_node = ip_group.get("folder", None)

                # Stage each file relative to the remote folder
                remote_path = folder_node.get_remote_path()
                computer_uuid = folder_node.computer.uuid
                hashes = ip_group.get("file_hashes", None).get_list()
                for relative_path, expected_hash in hashes:
                    source_path = f"{remote_path}/{relative_path}"
                    target_path = f"ip/{label}/{relative_path}"

                    # Stage IP file as symlinks
                    calcinfo.remote_symlink_list.append((computer_uuid, source_path, target_path))

                    # Add pre-execution verification script for this file
                    hash_check_script.append(
                        f"echo {expected_hash} {target_path} | sha256sum -c --status || "
                        f"{{echo 'IP hash mismatch in {label}: {relative_path}'; exit 1;}}"
                    )
            calcinfo.prepended_text = "\n".join(hash_check_script)


def validate_ip_inputs(value, port):
    """Validates inputs to ip namespaces.

    Each entry in an ip namespace must have a valid 'folder' (RemoteData) and 'file_hashes' (List) containing at least
    one item.
    """
    if not value:
        return None  # empty inputs are valid since required=false

    for label, group in value.items():
        # Ensure a RemoteData folder field is provided
        if "folder" not in group:
            return f"Missing required 'folder' input under 'ip.{label}'."
        if not isinstance(group["folder"], RemoteData):
            return f"ip.{label}.folder must be of type RemoteData, got {type(group['folder']).__name__}."

        # Ensure a List file_hashes field is provided with at least 1 item
        if "file_hashes" not in group:
            return f"Missing required 'file_hashes' input under 'ip.{label}'."
        if not isinstance(group["file_hashes"], List):
            return f"ip.{label}.file_hashes must be of type List, got {type(group['file_hashes']).__name__}."
        if not group["file_hashes"]:
            return f"ip.{label}.file_hashes must contain at least 1 item."
