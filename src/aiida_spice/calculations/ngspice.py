from aiida.engine import CalcJob
from aiida.orm import Dict, SinglefileData, ArrayData

class NgspiceCalculation(CalcJob):
    """CalcJob implementation for ngspice"""

    @classmethod
    def define(cls, spec):
        super().define(spec)

        # Define inputs
        spec.input('parameters', valid_type=Dict, help='Simulation parameters and control blocks.')
        spec.input('netlist', valid_type=SinglefileData, help='The SPICE netlist file.')

        # Define parser metadata
        spec.input('metadata.options.parser_name', valid_type=str, default='spice.rawfile')
        spec.input('metadata.options.output_filename', valid_type=str, default='output.raw')

        # Define expected outputs
        spec.output('output_parameters', valid_type=Dict, help='Parsed scalars and run metadata.')
        spec.output('output_arrays', valid_type=ArrayData, help='Parsed voltage and current vectors')

    def prepare_for_submission(self, folder):
        """Write the input files and configure the execution command"""

        # TODO: set up inputs

        codeinfo = self.get_codeinfo()
        codeinfo.cmdline_params = ['-b', '-r', self.metadata.options.output_filename, 'input.spice']
        codeinfo.stdout_name = 'stdout.txt'

        calcinfo = self.get_calcinfo()
        calcinfo.codes_info
