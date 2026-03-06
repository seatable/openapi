# SeaTable OpenAPI

This repository contains all supported API calls for the SeaTable Server as OpenAPI 3.0 definitions. It serves two primary purposes:

1. Generate the online API reference at https://api.seatable.com (via ReadMe.com).
2. Generate the Postman collection at https://www.postman.com/seatable.

The repository is organized into version branches (e.g. `v6.1`, `v6.2`).

## Publish to ReadMe

Every push to a version branch automatically syncs all OpenAPI specs and intro docs to ReadMe.com via the GitHub Action in `.github/workflows/rdme-openapi.yml`. Before uploading, the workflow validates all links (using [lychee](https://github.com/lycheeverse/lychee)) and all OpenAPI specs (using swagger-cli).

The ReadMe category IDs for each version are stored in `.github/readme-ids.json`.

### New version

To publish a new API version (e.g. v6.2):

1. Create a new branch: `git checkout -b v6.2`
2. Fork the API definition on https://dash.readme.com to the new version.
3. Get the new category IDs from the ReadMe dashboard or via API.
4. Update `.github/readme-ids.json` with the new IDs and version.
5. Update the `category` value in all `intro/*.md` frontmatter.
6. Update the version in all YAML spec files.
7. Push the branch: `git push --set-upstream origin v6.2`

## Automatic tests

This repository contains automated tests to detect possible regressions. The tests use [Schemathesis](https://schemathesis.readthedocs.io/en/stable/) to extract information from the OpenAPI files and [pytest](https://docs.pytest.org/en/8.2.x/) to run the actual tests.

Snapshots are stored and compared using [syrupy](https://github.com/tophat/syrupy) to detect possible regressions.

### Prerequisites

- Python 3.10+
- pip
- Publicly available SeaTable Server
- Two accounts (user and system-admin permission)

### Preparation of local test setup

For local test execution, we recommend setting up a virtual environment.

```bash
cd tests

# Create virtual environment (instead of python, you might also use python3)
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies - only once!
pip install -r requirements.txt

# Create environment variables
cp env.example .env
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

The reason is that the test cases compare previous outputs (snapshots) with the real results. Because you don't have any snapshots yet, pytest has nothing to compare with and all tests will fail.

To generate or update your snapshots just run pytest with the `--snapshot-update` flag to instruct syrupy to generate and update all snapshot files.
The snapshots will be stored in the directory `__snapshots__`.

Make sure to commit new snapshot files or any changes you made to them.

## Publish Postman Collection

When you tag and push a new version, the corresponding Postman collection is automatically synced.
For example, to publish version 6.0 to Postman:

```
git tag postman-v6.0
git push --tags
```

Pushing the tag triggers a GitHub Action that runs the `.github/sync-with-postman.sh` script.
This action requires the GitHub secret `POSTMAN_API_KEY`, which you can generate at: https://seatable.postman.co/settings/me/api-keys.
