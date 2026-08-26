from aiida.common.datastructures import CalcInfo, CodeInfo

from aiida_spice.calculations.spice import SpiceCalculation


class NgspiceCalculation(SpiceCalculation):
    """CalcJob implementation for ngspice circuit simulation."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define parser metadata for Rawfile parsing
        spec.input("metadata.options.parser_name", valid_type=str, default="spice.rawfile")
        spec.input("metadata.options.rawfile_name", valid_type=str, default="output.raw")
        spec.input("metadata.options.parser_dialect", valid_type=str, default="ngspice")

    def prepare_for_submission(self, folder):
        """Write the input files required for simulation with ngspice."""
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
            handle.write(f"write {self.metadata.options.rawfile_name}\n")
            handle.write("quit\n")
            handle.write(".endc\n\n")
            handle.write(".end\n")

        codeinfo = CodeInfo()
        codeinfo.code_uuid = self.inputs.code.uuid
        codeinfo.stdout_name = self.metadata.options.stdout_name
        codeinfo.join_files = True
        codeinfo.cmdline_params = ["-b", input_filename]

        calcinfo = CalcInfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.local_copy_list = [
            (self.inputs.netlist.uuid, self.inputs.netlist.filename, self.inputs.netlist.filename),
        ]
        calcinfo.retrieve_list = [self.metadata.options.stdout_name, self.metadata.options.rawfile_name]

        # Stage includes, preserving relative paths
        self.stage_includes(calcinfo)

        # Validate ip folders & file hashes
        calcinfo.remote_symlink_list = []
        self.stage_ip_files(calcinfo)

        return calcinfo
