"""Run DC operating point analysis on a simple circuit on localhost using ngspice.

Usage: ./example_01.py
"""

from os import path

import click
from aiida import cmdline, engine
from aiida.plugins import CalculationFactory, DataFactory

from aiida_spice import helpers

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), "input_files")


def test_run(code):
    """Run a calculation on the localhost computer.

    Uses test helpers to create AiiDA Code on the fly.
    """
    if not code:
        # get code
        computer = helpers.get_computer()
        code = helpers.get_code(entry_point="spice.ngspice", computer=computer)

    # Prepare input parameters
    singlefile_data = DataFactory("core.singlefile")
    netlist = singlefile_data(file=path.join(INPUT_DIR, "voltage_divider.spice"))
    list_data = DataFactory("core.list")
    analyses = list_data(list=[".op"])

    inputs = {
        "code": code,
        "netlist": netlist,
        "analyses": analyses,
        "metadata": {
            "description": "Test job submission with the aiida_spice plugin",
        },
    }

    result = engine.run(CalculationFactory("spice.ngspice"), **inputs)

    computed_properties = result["output_properties"].get_content()
    print(computed_properties)


@click.command()
@cmdline.utils.decorators.with_dbenv()
@cmdline.params.options.CODE()
def cli(code):
    """Run example.

    Example usage: $ ./example_01.py --code ngspice@localhost

    Alternative (creates test code): $ ./example_01.py

    Help: $ ./example_01.py --help
    """
    test_run(code)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
