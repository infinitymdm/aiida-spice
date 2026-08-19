from aiida.engine import CalcJob
from aiida.orm import ArrayData, Dict, List, SinglefileData


class NgspiceCalculation(CalcJob):
    """CalcJob implementation for ngspice circuit simulation."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define inputs
        spec.input("netlist", valid_type=SinglefileData, help="The SPICE netlist file.")
        spec.input("analyses", valid_type=List, help="Analyses to run during simulation.")
        spec.input("parameters", valid_type=Dict, help="Simulation parameters to set with .param.")
        spec.input("options", valid_type=Dict, help="Simulation options to set with .option.")

        # Define parser metadata
        spec.input("metadata.options.parser_name", valid_type=str, default="spice.rawfile")
        spec.input("metadata.options.output_filename", valid_type=str, default="output.raw")

        # Define exit codes
        spec.exit_code()

        # Define expected outputs
        spec.output("output_parameters", valid_type=Dict, help="Parsed scalars and run metadata.")
        spec.output("output_arrays", valid_type=ArrayData, help="Parsed voltage and current vectors")

    def prepare_for_submission(self, folder):
        """Write the input files required for the ngspice simulation.

        :param folder: an `~aiida.common.folders.Folder` to temporarily write files on disk
        :return: `~aiida.common.datastructures.CalcInfo` instance
        """
        input_filename = "input.spice"

        # Write the input SPICE deck
        with folder.open(input_filename, "w") as handle:
            handle.write("* AiiDA ngspice input deck\n")
            for prm, val in self.inputs.parameters.get_dict().items():
                handle.write(f".param {prm}={val}\n")
            handle.write(f".include {self.inputs.netlist.filename}\n\n")
            for analysis in self.inputs.parameters.get_list():
                handle.write(f"{analysis}\n")
            for opt, val in self.inputs.options.get_dict().items():
                handle.write(f".options {opt}={val}\n")
            handle.write("\n.control\n")
            handle.write("run\n")
            handle.write("quit\n")
            handle.write(".endc\n\n")
            handle.write(".end\n")

        codeinfo = self.get_codeinfo()
        codeinfo.cmdline_params = ["-r", self.metadata.options.output_filename, "-b", input_filename]

        calcinfo = self.get_calcinfo()
        calcinfo.codes_info = [codeinfo]
        calcinfo.retrieve_list = [self.metadata.options.filename]

        return calcinfo
