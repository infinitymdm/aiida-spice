#! /usr/bin/env python
"""Run transient and propagation delay measurements on an ami035 FAX1 standard cell.

Usage: ./stdcell_delay.py
"""

from pathlib import Path

from aiida import load_profile
from aiida.engine import run
from aiida.manage.caching import enable_caching
from aiida.orm import Dict, FolderData, List, SinglefileData, load_code
from aiida.plugins import CalculationFactory

from aiida_spice.utils.include_paths import get_include_paths

INPUT_DIR = Path(__file__).resolve().parent / "input_files"

load_profile()

NgspiceCalculation = CalculationFactory("spice.ngspice")
code = load_code("ngspice@localhost")

# Load netlist & set parameters
# NOTE: This netlist has several includes which must be present on your system.
#       See https://stineje.github.io/CharLib/chapters/03_user_guide.html#yaml-configuration-examples
#       for instructions to get the required files, and adjust the netlist to point to the correct
#       locations on your system.
netlist_path = INPUT_DIR / "osu350_FAX1_delay.spice"
netlist = SinglefileData(file=netlist_path.resolve())
includes = FolderData()
for include_file in get_include_paths(netlist_path):
    includes.put_object_from_file(include_file, path=include_file.name)
analyses = List(
    list=[
        ".meas TRAN cell_fall__c_to_ys trig v(vC) val=1.65 fall=1 targ v(vYS) val=1.65 fall=1",
        ".meas TRAN fall_transition__c_to_ys trig v(vYS) val=2.64 fall=1 targ v(vYS) val=0.66 fall=1",
        ".tran 0.025ns 200.0ns 0s",
    ]
)
options = Dict(
    dict={
        "temp": "25C",
        "tnom": "25C",
        "autostop": 1,
        "trtol": 1,
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

with enable_caching(identifier="spice.ngspice"):
    results = run(builder)

    # Print parsed outputs
    print("Metadata:", results["metadata"].get_dict())
    print("Measurements:", results["measurements"].get_dict())
    print("Traces:", results["trace_data"].get_arraynames())
