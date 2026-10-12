from pathlib import Path

from aiida_spice.utils import get_include_paths


def test_get_include_paths_does_not_share_state_between_calls(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    include_file = tmp_path / "first.lib"
    include_file.write_text("* include file")

    first_result = get_include_paths(".include first.lib", tmp_path)
    second_result = get_include_paths("V1 in 0 1", tmp_path)

    assert first_result == {Path("first.lib").resolve()}
    assert second_result == set()


def test_get_include_paths_preserves_spaces_in_quoted_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    include_file = tmp_path / "model files" / "cell.lib"
    include_file.parent.mkdir()
    include_file.write_text("* Dummy file with spaces in the pathname\n")

    netlist = '.include "model files/cell.lib"\n'

    assert get_include_paths(netlist, tmp_path) == {include_file.resolve()}
