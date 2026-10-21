import hashlib
from os import path

import pytest
from aiida.engine import run
from aiida.orm import Dict, SinglefileData, Str
from aiida.plugins import CalculationFactory, DataFactory

from aiida_spice.calculations import parse_includes, parse_ip_includes
from aiida_spice.utils import sanitize

from . import TEST_DIR


@pytest.fixture(
    params=[
        pytest.param((parse_includes, "metadata"), id="parse_includes"),
        pytest.param((parse_ip_includes, "ip_metadata"), id="parse_ip_includes"),
    ]
)
def include_parser(request):
    """Exercise both include representations with the existing AiiDA profile."""
    return request.param


def test_parse_includes_and_parse_ip_includes_basic(tmp_path, include_parser):
    helper, metadata_key = include_parser
    ip_root = tmp_path / "ip"
    contents = {
        "models.lib": b".include nested/device.lib\n",
        "nested/device.lib": b"* device model\n",
    }
    for relative_path, content in contents.items():
        include_file = ip_root / relative_path
        include_file.parent.mkdir(parents=True, exist_ok=True)
        include_file.write_bytes(content)
    netlist_file = tmp_path / "circuit.cir"
    netlist_file.write_text(".include models.lib\n")

    includes = helper(SinglefileData(file=netlist_file), Str(str(ip_root)))

    expected_keys = {metadata_key}
    pdk_hash = hashlib.sha3_256()
    for relative_path in sorted(contents):
        content = contents[relative_path]
        expected_digest = hashlib.sha3_256(content).hexdigest()
        pdk_hash.update(expected_digest.encode("utf-8"))
        key = sanitize(relative_path) + "__" + expected_digest
        expected_keys.add(key)
        node = includes[key]
        if helper is parse_includes:
            assert isinstance(node, SinglefileData)
            with node.open(mode="rb") as handle:
                assert handle.read() == content
        else:
            assert isinstance(node, Dict)
            assert node.get_dict() == {"path": relative_path, "hash": expected_digest}
            assert node.base.repository.list_object_names() == []

    assert set(includes) == expected_keys
    metadata = includes[metadata_key].get_dict()
    assert metadata["path"] == str(ip_root.resolve())
    if helper is parse_ip_includes:
        assert metadata["hash"] == pdk_hash.hexdigest()
        assert includes[metadata_key].base.repository.list_object_names() == []


def test_parse_includes_and_parse_ip_includes_empty(tmp_path, include_parser):
    helper, metadata_key = include_parser
    ip_root = tmp_path / "ip"
    ip_root.mkdir()
    netlist_file = tmp_path / "empty.cir"
    netlist_file.write_bytes(b"")

    includes = helper(SinglefileData(file=netlist_file), Str(str(ip_root)))

    assert set(includes) == {metadata_key}
    expected_metadata = {"path": str(ip_root.resolve())}
    if helper is parse_ip_includes:
        expected_metadata["hash"] = hashlib.sha3_256().hexdigest()
    assert includes[metadata_key].get_dict() == expected_metadata


def test_parse_includes_and_parse_ip_includes_outside_root(tmp_path, include_parser):
    helper, _ = include_parser
    ip_root = tmp_path / "ip"
    ip_root.mkdir()
    outside_file = tmp_path / "outside.lib"
    outside_file.write_bytes(b"* outside model\n")
    netlist_file = tmp_path / "circuit.cir"
    netlist_file.write_text(".include ../outside.lib\n")

    with pytest.raises(ValueError, match="not found under designated root"):
        helper(SinglefileData(file=netlist_file), Str(str(ip_root)))


def test_parse_includes_and_parse_ip_includes_changed_bytes(tmp_path, include_parser):
    helper, metadata_key = include_parser
    ip_root = tmp_path / "ip"
    ip_root.mkdir()
    include_file = ip_root / "models.lib"
    original_content = b"* original model\n"
    changed_content = b"* changed model\n"
    include_file.write_bytes(original_content)
    netlist_file = tmp_path / "circuit.cir"
    netlist_file.write_text(".include models.lib\n")
    netlist = SinglefileData(file=netlist_file)
    root = Str(str(ip_root))

    before = helper(netlist, root)
    include_file.write_bytes(changed_content)
    after = helper(netlist, root)

    original_digest = hashlib.sha3_256(original_content).hexdigest()
    changed_digest = hashlib.sha3_256(changed_content).hexdigest()
    original_key = sanitize("models.lib") + "__" + original_digest
    changed_key = sanitize("models.lib") + "__" + changed_digest
    assert set(before) == {metadata_key, original_key}
    assert set(after) == {metadata_key, changed_key}
    assert original_key != changed_key
    if helper is parse_ip_includes:
        assert before[original_key].get_dict()["hash"] == original_digest
        assert after[changed_key].get_dict()["hash"] == changed_digest
        assert before[metadata_key].get_dict()["hash"] != after[metadata_key].get_dict()["hash"]


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

    if explicit_root:
        assert includes["metadata"].get_dict()["path"] == str(tmp_path)
    includes.pop("metadata")
    assert len(includes) == len(contents)
    for relative_path, expected_content in contents.items():
        sanitized_prefix = sanitize(relative_path)
        matching_keys = [key for key in includes if key.startswith(sanitized_prefix)]
        assert len(matching_keys) == 1, f"Expected exactly 1 key matching {relative_path}"
        assert includes[matching_keys[0]].get_content() == expected_content
