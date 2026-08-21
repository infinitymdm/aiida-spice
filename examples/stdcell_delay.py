#! /usr/bin/env python
"""Run transient and propagation delay measurements on an ami035 FAX1 standard cell.

Usage: ./stdcell_delay.py
"""

from os import path

from aiida import load_profile
from aiida.engine import run
from aiida.orm import Dict, FolderData, List, SingleFileData, load_code
from aiida.plugins import CalculationFactory
from aiida_spice.utils.include_paths import get_include_paths

INPUT_DIR = path.join(path.dirname(path.realpath(__file__)), "input_files")

load_profile()

NgspiceCalculation = CalculationFactory("spice.ngspice")
code = load_code("ngspice@localhost")

# Load netlist & set parameters
netlist = SingleFileData(file=path.join(INPUT_DIR, "osu350_FAX1_delay.spice"))
includes = FolderData()
for include_file in get_include_paths(netlist):
    pass  # TODO
analyses = List(
    list=[
        # TODO
    ]
)
options = Dict(
    dict={
        # TODO
    }
)

builder = NgspiceCalculation.get_builder()
builder.code = code
builder.netlist = netlist
builder.includes = includes
builder.analyses = analyses
builder.options = options
builder.metadata.options.resources = {
    "num_machines": 1,
    "num_mpiprocs_per_machine": 1,
}

results = run(builder)

# Print parsed outputs
print("Parsed Parameters:", results["output_parameters"].get_dict())
