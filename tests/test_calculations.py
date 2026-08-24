from os import path

from aiida.engine import run
from aiida.plugins import CalculationFactory, DataFactory

from . import TEST_DIR


def test_ngpsice(spice_code):
    """Test running an ngspice calculation."""

    # Prepare input parameters
    singlefile_data = DataFactory("core.singlefile")
    netlist = singlefile_data(file=path.join(TEST_DIR, "input_files/voltage_divider.spice"))
    list_data = DataFactory("core.list")
    analyses = list_data(list=[".op"])

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
    singlefile_data = DataFactory("core.singlefile")
    netlist = singlefile_data(file=path.join(TEST_DIR, "input_files/voltage_divider.spice"))
    list_data = DataFactory("core.list")
    analyses = list_data(list=[".op"])

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
