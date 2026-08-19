from aiida.engine import CalcJob
from aiida.orm import ArrayData, Dict, SinglefileData


class NgspiceCalculation(CalcJob):
    """CalcJob implementation for ngspice circuit simulation."""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define inputs
        spec.input("parameters", valid_type=Dict, help="Simulation options and analyses.")
        spec.input("netlist", valid_type=SinglefileData, help="The SPICE netlist file.")

        # Define parser metadata
        spec.input("metadata.options.parser_name", valid_type=str, default="spice.rawfile")
        spec.input("metadata.options.output_filename", valid_type=str, default="output.raw")

        # Define expected outputs
        spec.output("output_parameters", valid_type=Dict, help="Parsed scalars and run metadata.")
        spec.output("output_arrays", valid_type=ArrayData, help="Parsed voltage and current vectors")

    def prepare_for_submission(self, folder):
        """Write the input files required for the ngspice simulation.

        :param folder: an `~aiida.common.folders.Folder` to temporarily write files on disk
        :return: `~aiida.common.datastructures.CalcInfo` instance
        """

        # Set up inputs
        netlist = self.inputs.netlist
        parameters = self.inputs.parameters.get_dict()
        input_filename = "input.spice"

        # Write the input SPICE deck
        with folder.open(input_filename, "w") as handle:
            handle.write("* AiiDA ngspice input deck\n")
            handle.write(f".include {netlist.filename}\n\n")
            if "analysis" in parameters:
                handle.write(f'{parameters["analysis"]}\n')
            if "options" in parameters:
                for opt, val in parameters["options"].items():
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
