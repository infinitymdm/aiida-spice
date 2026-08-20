[![Build Status][ci-badge]][ci-link]
[![Coverage Status][cov-badge]][cov-link]
[![Docs status][docs-badge]][docs-link]
[![PyPI version][pypi-badge]][pypi-link]

# aiida-spice

AiiDA plugin for SPICE circuit simulation.

## Repository contents

* [`.github/`](.github/): [Github Actions](https://github.com/features/actions) configuration
  * [`ci.yml`](.github/workflows/ci.yml): runs tests, checks test coverage and builds documentation at every new commit
  * [`publish-on-pypi.yml`](.github/workflows/publish-on-pypi.yml): automatically deploy git tags to PyPI - just generate a [PyPI API token](https://pypi.org/help/#apitoken) for your PyPI account and add it to the `pypi_token` secret of your github repository
* [`aiida_spice/`](src/aiida_spice/): The main source code of the plugin package
  * [`calculations`](src/aiida_spice/calculations): `CalcJob` subclasses for each supported simulator.
  * [`parsers`](src/aiida_spice/parsers): A new `Parser` for the Berkeley SPICE3 rawfiles `RawfileParser`
* [`docs/`](docs/): A documentation template ready for publication on [Read the Docs](http://aiida-diff.readthedocs.io/en/latest/)
* [`examples/`](examples/): An example of how to submit a calculation using this plugin
* [`tests/`](tests/): Basic regression tests using the [pytest](https://docs.pytest.org/en/latest/) framework (submitting a calculation, ...). Install `pip install -e .[testing]` and run `pytest`.
* [`.gitignore`](.gitignore): Telling git which files to ignore
* [`.pre-commit-config.yaml`](.pre-commit-config.yaml): Configuration of [pre-commit hooks](https://pre-commit.com/) that sanitize coding style and check for syntax errors. Enable via `pip install -e .[pre-commit] && pre-commit install`
* [`.readthedocs.yml`](.readthedocs.yml): Configuration of documentation build for [Read the Docs](https://readthedocs.org/)
* [`LICENSE`](LICENSE): License for your plugin
* [`README.md`](README.md): This file
* [`conftest.py`](conftest.py): Configuration of fixtures for [pytest](https://docs.pytest.org/en/latest/)
* [`pyproject.toml`](setup.json): Python package metadata for registration on [PyPI](https://pypi.org/) and the [AiiDA plugin registry](https://aiidateam.github.io/aiida-registry/) (including entry points)

## Features

TBA

## Installation

```shell
pip install aiida-spice
# Everthing else TBA
```

## Usage

TBA

## Development

```shell
git clone https://github.com/infinitymdm/aiida-spice .
cd aiida-spice
pip install --upgrade pip
pip install -e .[pre-commit,testing]  # install extra dependencies
pre-commit install  # install pre-commit hooks
pytest -v  # discover and run all tests
```

See the [developer guide](http://aiida-spice.readthedocs.io/en/latest/developer_guide/index.html) for more information.

## License

MIT
## Contact

marcus@infinitymdm.dev


[ci-badge]: https://github.com/infinitymdm/aiida-spice/workflows/ci/badge.svg?branch=master
[ci-link]: https://github.com/infinitymdm/aiida-spice/actions
[cov-badge]: https://coveralls.io/repos/github/infinitymdm/aiida-spice/badge.svg?branch=master
[cov-link]: https://coveralls.io/github/infinitymdm/aiida-spice?branch=master
[docs-badge]: https://readthedocs.org/projects/aiida-spice/badge
[docs-link]: http://aiida-spice.readthedocs.io/
[pypi-badge]: https://badge.fury.io/py/aiida-spice.svg
[pypi-link]: https://badge.fury.io/py/aiida-spice
