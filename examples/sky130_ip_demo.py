"""Run an AC sweep on a sky130 buf_1 standard cell. This file demos how to use ip with provenance.

Usage: ./sky130_ip_demo.py
"""

from pathlib import Path

from aiida import load_profile
from aiida.engine import run
from aiida.orm import Dict, FolderData, List, RemoteData, SinglefileData, load_code, load_computer
from aiida.plugins import CalculationFactory

from aiida_spice.utils.include_paths import get_include_paths, hash_ip_files, separate_ip_files

INPUT_DIR = Path(__file__).resolve().parent / "input_files"

load_profile()

netlist_path = INPUT_DIR / "sky130_buf_1.spice"
netlist = SinglefileData(file=netlist_path.resolve())

ip_path = Path("~/.ciel/sky130A").expanduser()
includes = FolderData()
ip, include_files = separate_ip_files(get_include_paths(netlist_path), {ip_path})
for i in include_files:
    includes.put_object_from_file(i, path=i.name)
ip_folder = RemoteData(remote_path=str(ip_path), computer=load_computer("localhost"))
ip_hashes = List(list=hash_ip_files(ip, ip_path))

analyses = List(list=[".ac dec 100 10Hz 10GHz"])

params = Dict(dict={"mc_mm_switch": 0})

options = Dict(
    dict={
        "temp": "25C",
        "tnom": "25C",
        "rshunt": 1e9,
    }
)


NgspiceCalculation = CalculationFactory("spice.ngspice")
code = load_code("ngspice@localhost")

builder = NgspiceCalculation.get_builder()
builder.code = code
builder.parameters = params
builder.netlist = netlist
builder.includes = includes
builder.ip = {
    "sky130": {
        "folder": ip_folder,
        "file_hashes": ip_hashes,
    },
}
builder.analyses = analyses
builder.options = options
builder.metadata.options.resources = {
    "num_machines": 1,
    "num_mpiprocs_per_machine": 1,
}

results = run(builder)

print(results["trace_data"].get_arraynames())
