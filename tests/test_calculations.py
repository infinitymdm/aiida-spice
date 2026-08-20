#! /usr/bin/env python
"""Run DC operating point analysis on a simple circuit on localhost using ngspice.

Usage: ./example_01.py
"""

from os import path

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory

from . import TEST_DIR


def test_ngpsice(code):
    """Test running an ngspice calculation."""

    # Prepare input parameters
    singlefile_data = DataFactory("core.singlefile")
    netlist = singlefile_data(file=path.join(TEST_DIR, "voltage_divider.spice"))
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

    result = run(CalculationFactory("spice.ngspice"), **inputs)

    computed_properties = result["output_properties"].get_content()
    print(computed_properties)

    assert computed_properties is not None
