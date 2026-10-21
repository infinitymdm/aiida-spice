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

    def stage_includes(self, calcinfo):
        """Stage includes for local copy or provenance exclude as appropriate"""
        if not calcinfo.local_copy_list:
            calcinfo.local_copy_list = []
        if not calcinfo.provenance_exclude_list:
            calcinfo.provenance_exclude_list = []
        if "includes" in self.inputs:
            includes = self.inputs.includes
            for key, node in includes.items():
                if key in ("metadata", "ip_metadata"):
                    continue  # skip metadata keys
                if isinstance(node, SinglefileData):
                    node_path = includes.metadata.get_dict()["path"] + "/" + node.filename
                    calcinfo.local_copy_list.append((node.uuid, node.filename, node_path))
                elif isinstance(node, Dict):
                    node_path = includes.ip_metadata.get_dict()["path"] + "/" + node.get_dict()["path"]
                    calcinfo.provenance_exclude_list.append(node_path)

    def verify_ip(self):
        """Ensure all ip includes match the expected hashes"""
        pass  # TODO
