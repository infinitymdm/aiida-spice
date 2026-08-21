#! /usr/bin/env python
"""Run a simple example calculation using ngspice.

Usage: ./voltage_divider.py
"""

from os import path

from aiida import load_profile
from aiida.engine import run
from aiida.orm import List, SinglefileData, load_code
from aiida.plugins import CalculationFactory

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), "input_files")

load_profile()

NgspiceCalculation = CalculationFactory("spice.ngspice")
code = load_code("ngspice@localhost")

# Load netlist & set parameters
netlist = SinglefileData(file=path.join(INPUT_DIR, "voltage_divider.spice"))
analyses = List(list=[".op"])

# Set up the calculation builder
builder = NgspiceCalculation.get_builder()
builder.code = code
builder.netlist = netlist
builder.analyses = analyses
builder.metadata.options.resources = {
    "num_machines": 1,
    "num_mpiprocs_per_machine": 1,
}

# 5. Submit job to the daemon / engine synchronously
results = run(builder)

# Print parsed outputs
print("Parsed Parameters:", results["output_parameters"].get_dict())
