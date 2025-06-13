# SeaTable OpenAPI

Welcome to the SeaTable OpenAPI Definition Repository! 🌊🔍✨

This repository encompasses all supported API calls for the SeaTable Server. The OpenAPI definition here serves two primary purposes:

1. Generate the online API reference accessible at https://api.seatable.com.
2. Generate the Postman collection, which is available at https://www.postman.com/seatable.

The repository is organized into version branches.

## Automatic tests

This repository contains automated tests to detect possible regressions. The tests use [Schemathesis](https://schemathesis.readthedocs.io/en/stable/)
to extract information from the OpenAPI files and [pytest](https://docs.pytest.org/en/8.2.x/) to run the actual tests.

Snapshots are stored and compared using [syrupy](https://github.com/tophat/syrupy) to detect possible regressions.

### Prerequisites

- Python 3.10+
- pip
- Public available SeaTable Server
- Two accounts (user and system-admin permission)

### Preparation of local test setup

For local test execution, we recommend to setup a virtual environment.

```bash
cd tests

# Create virtual environment (instead of python, you might also user python3)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies - only once!
pip install -r requirements.txt

# Create environment variables
copy env.example .env
# edit .env with the editor of your choice and save it...

# Deactivate virtual environment
deactivate
```

### Local execution of tests

With this virtual environment it is super easy to run your tests locally.

```bash
cd tests

# Activate virtual environment
source .venv/bin/activate

# Source environment variables
source .env

# Run tests
# You can specify specific test scenarios or run all tests
pytest                                           # runs all files starting with test_xxx
pytest test_base_operations.py --color=yes -vv   # runs only the scenario from test_base_operations.py (verbose mode)

# Deactivate virtual environment (optional)
deactivate
```

### Create/Update Snapshots

If you add a test for the first time, you might receive the result that all tests failed.

```bash
============================================== short test summary info ===============================================
FAILED test_base_operations.py::test_createBase - assert [- snapshot] == [+ received]
FAILED test_base_operations.py::test_createTable[createTable] - assert [- snapshot] == [+ received]
...
```

The reason is that the test cases compare previous outputs (snapshots) with the real results. Because you don't have any snapshots yet, pytest has nothing to compare with and and all tests will fail.

To generate or update your snapshots just run pytest with the `--snapshot-update` flag to instruct syrupy to generate and update all snapshot files.
The snapshots will be stored in the directory `__snapshots__`.

Make sure to commit new snapshot files or any changes you made to them.
