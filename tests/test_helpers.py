from pathlib import Path

import pytest

from aiida_spice.utils import get_include_paths


def test_get_include_paths_does_not_share_state_between_calls(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    include_file = tmp_path / "first.lib"
    include_file.write_text("* include file")

    first_result = get_include_paths(".include first.lib", tmp_path)
    second_result = get_include_paths("V1 in 0 1", tmp_path)

    assert first_result == {Path("first.lib").resolve()}
    assert second_result == set()


@pytest.mark.skip(reason="Tracked in issue #4")
def test_get_include_paths_preserves_spaces_in_quoted_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    include_file = tmp_path / "model files" / "cell.lib"
    include_file.parent.mkdir()
    include_file.write_text("* Dummy file with spaces in the pathname\n")

    netlist = '.include "model files/cell.lib"\n'

    assert get_include_paths(netlist, tmp_path) == {include_file.resolve()}


@pytest.mark.parametrize("directive", [".include", ".lib"])
@pytest.mark.parametrize("escape", ["parent_traversal", "symlink"])
def test_get_include_paths_rejects_absolute_path_escape(tmp_path, directive, escape):
    root = tmp_path / "approved"
    root.mkdir()

    outside_file = tmp_path / "outside.lib"
    outside_file.write_text("* outside the approved root")

    if escape == "parent_traversal":
        # Keep ".." intact to exercise the containment check.
        include_path = root / ".." / outside_file.name
    else:
        include_path = root / "link.lib"
        try:
            include_path.symlink_to(outside_file)
        except (OSError, NotImplementedError) as error:
            pytest.skip(f"Cannot create a symlink: {error}")

    assert include_path.is_absolute()
    assert include_path.resolve() == outside_file.resolve()

    with pytest.raises(ValueError):
        get_include_paths(f'{directive} "{include_path}"', root)


def test_nested_include_resolves_from_including_file(tmp_path, monkeypatch):
    models = tmp_path / "models"
    models.mkdir()

    cells = models / "cells.lib"
    cells.write_text(".include devices.lib\n")

    nested_devices = models / "devices.lib"
    nested_devices.write_text("* Correct nested include\n")

    cwd_devices = tmp_path / "devices.lib"
    cwd_devices.write_text("* Wrong file, but still under include_root\n")

    monkeypatch.chdir(tmp_path)

    included_files = get_include_paths(
        ".include models/cells.lib\n",
        include_root=tmp_path,
    )

    assert included_files == {cells.resolve(), nested_devices.resolve()}
