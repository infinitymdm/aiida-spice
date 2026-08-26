from pathlib import Path

from aiida.engine import run
from aiida.orm import List, SinglefileData
from aiida.plugins import CalculationFactory

TEST_DIR = Path(__file__).resolve().parent / "input_files"


def test_ngpsice(spice_code):
    """Test running an ngspice calculation."""

    # Prepare input parameters
    netlist = SinglefileData(file=TEST_DIR / "voltage_divider.spice")
    analyses = List(list=[".op"])

    inputs = {
        "code": spice_code,
        "netlist": netlist,
        "analyses": analyses,
        "metadata": {
            "description": "Test job submission with the aiida_spice plugin",
            "options": {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 1,
                },
            },
        },
    }

    result = run(CalculationFactory("spice.ngspice"), **inputs)
    parsed_metadata = result["metadata"].get_dict()

    assert parsed_metadata is not None


def test_xyce(spice_code):
    """Test running a Xyce calculation."""

    # Prepare input parameters
    netlist = SinglefileData(file=TEST_DIR / "voltage_divider.spice")
    analyses = List(list=[".op"])

    inputs = {
        "code": spice_code,
        "netlist": netlist,
        "analyses": analyses,
        "metadata": {
            "description": "Test job submission with the aiida_spice plugin",
            "options": {
                "resources": {
                    "num_machines": 1,
                    "num_mpiprocs_per_machine": 1,
                },
            },
        },
    }

    result = run(CalculationFactory("spice.xyce"), **inputs)
    trace_data = result["trace_data"].get_arraynames()

    assert trace_data is not None


# def test_ngspice_with_sky130(spice_code, aiida_computer_local):
#     """Test a spice calculation with parameters, includes, and IP"""
#
#     netlist_path = Path(TEST_DIR) / "sky130_buf_1.spice"
#     netlist = SinglefileData(file=netlist_path.resolve())
#
#     analyses = List(list=[".ac dec 100 10Hz 10GHz"])
#     params = Dict(dict={"mc_mm_switch": 0})
#     options = Dict(
#         dict={
#             "temp": "25C",
#             "tnom": "25C",
#             "rshunt": 1e9,
#         }
#     )
#
#     ip_path = Path("~/.ciel/sky130A").expanduser()
#     includes = FolderData()
#     ip_files, include_files = separate_ip_files(get_include_paths(netlist_path), {ip_path})
#     for f in include_files:
#         includes.put_object_from_file(f, path=f.name)
#     ip_folder = RemoteData(remote_path=str(ip_path), computer=aiida_computer_local())
#     ip_hashes = List(list=hash_ip_files(ip_files, ip_path))
#
#     NgspiceCalculation = CalculationFactory("spice.ngspice")
#
#     builder = NgspiceCalculation.get_builder()
#     builder.code = spice_code
#     builder.parameters = params
#     builder.netlist = netlist
#     builder.includes = includes
#     builder.ip = {
#         "sky130": {
#             "folder": ip_folder,
#             "file_hashes": ip_hashes,
#         },
#     }
#     builder.analyses = analyses
#     builder.options = options
#     builder.metadata.options.resources = {
#         "num_machines": 1,
#         "num_mpiprocs_per_machine": 1,
#     }
#
#     results = run(builder)
#
#     trace_data = result["trace_data"].get_arraynames()
#
#     assert trace_data is not None
