from os import path

import pytest
from aiida.engine import run
from aiida.orm import SinglefileData, Str
from aiida.plugins import CalculationFactory, DataFactory

from aiida_spice.calculations import parse_includes

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


@pytest.mark.parametrize("explicit_root", [False, True])
def test_parse_includes_preserves_duplicate_basenames(tmp_path, monkeypatch, explicit_root):
    monkeypatch.chdir(tmp_path)

    contents = {
        "a/models.lib": "* models from directory a\n",
        "b/models.lib": "* models from directory b\n",
    }
    for relative_path, content in contents.items():
        include_file = tmp_path / relative_path
        include_file.parent.mkdir()
        include_file.write_text(content)

    netlist_file = tmp_path / "circuit.cir"
    netlist_file.write_text(".include a/models.lib\n.include b/models.lib\n")
    netlist = SinglefileData(file=str(netlist_file))

    kwargs = {"root_path": Str(str(tmp_path))} if explicit_root else {}
    includes = parse_includes(netlist, **kwargs)

    assert sorted(includes.list_object_names()) == ["a", "b"]
    for relative_path, expected_content in contents.items():
        assert includes.base.repository.get_object_content(relative_path) == expected_content
