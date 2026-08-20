"""pytest fixtures for simplified testing."""

import pytest

pytest_plugins = ["aiida.tools.pytest_fixtures"]


@pytest.fixture(scope="function", autouse=True)
def clear_database_auto(aiida_profile_clean):
    """Automatically clear database in between tests."""


@pytest.fixture(scope="function")
def spice_code(aiida_computer_local, aiida_code_installed):
    """Get a spice code."""
    return aiida_code_installed(
        computer=aiida_computer_local(), filepath_executable="ngspice", default_calc_job_plugin="spice.ngspice"
    )
