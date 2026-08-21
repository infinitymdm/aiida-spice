from aiida.common.datastructures import CalcInfo, CodeInfo
from aiida.engine import CalcJob
from aiida.orm import ArrayData, Dict, FolderData, List, SinglefileData


class NgspiceCalculation(CalcJob):
    """CalcJob implementation for ngspice circuit simulation."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define inputs
        spec.input("netlist", valid_type=SinglefileData, help="The SPICE netlist file.")
        spec.input("includes", valid_type=FolderData, required=False, help="Folders referenced in the SPICE netlist")
        spec.input("analyses", valid_type=List, help="Analyses to run during simulation.")
        spec.input("parameters", valid_type=Dict, required=False, help="Simulation parameters to set with .param.")
        spec.input("options", valid_type=Dict, required=False, help="Simulation options to set with .option.")

        # Define parser metadata
        spec.input("metadata.options.output_filename", valid_type=str, default="output.raw")
        spec.input("metadata.options.parser_name", valid_type=str, default="spice.rawfile")
        spec.input("metadata.options.parser_dialect", valid_type=str, default="ngspice")

        # Define exit codes
        spec.exit_code(430, "ERROR_NO_RETRIEVED_FOLDER", "Failed to parse the retrieved folder")
        spec.exit_code(440, "ERROR_MISSING_RAWFILE_NAME", "Output rawfile name not present in retrieved results")
        spec.exit_code(450, "ERROR_PARSING_RAWFILE", "Failed to parse the SPICE3 rawfile")

        # Define expected outputs
        spec.output("output_parameters", valid_type=Dict, help="Parsed scalars and run metadata.")
        spec.output("output_arrays", valid_type=ArrayData, help="Parsed voltage and current vectors")

    def prepare_for_submission(self, folder):
        """Write the input files required for the ngspice simulation.

        :param folder: an `~aiida.common.folders.Folder` to temporarily write files on disk
        :return: `~aiida.common.datastructures.CalcInfo` instance
        """
        input_filename = "_aiida_input.ngspice"

        # Write the input SPICE deck
        with folder.open(input_filename, "w") as handle:
            handle.write("* AiiDA ngspice input deck\n")
            if "parameters" in self.inputs:
                for prm, val in self.inputs.parameters.get_dict().items():
                    handle.write(f".param {prm}={val}\n")
            handle.write(f".include {self.inputs.netlist.filename}\n\n")
            for analysis in self.inputs.analyses.get_list():
                handle.write(f"{analysis}\n")
            if "options" in self.inputs:
                for opt, val in self.inputs.options.get_dict().items():
                    handle.write(f".options {opt}={val}\n")
            handle.write("\n.control\n")
            handle.write("run\n")
            handle.write(f"write {self.metadata.options.output_filename}\n")
            handle.write("quit\n")
            handle.write(".endc\n\n")
            handle.write(".end\n")

        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.cmdline_params = ["-b", input_filename]

        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (self.inputs.netlist.uuid, self.inputs.netlist.filename, self.inputs.netlist.filename)
        ]
        calcinfo.retrieve_list = [self.metadata.options.output_filename]

        # Stage includes, preserving relative paths
        if "includes" in self.inputs:
            inc_node = self.inputs.includes
            for filename in inc_node.list_object_names():
                calcinfo.local_copy_list.append((inc_node.uuid, filename, filename))

        return calcinfo
