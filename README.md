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

## Tests

This repository contains tests to detect changes in SeaTable's API behavior between versions. The tests use [Schemathesis](https://schemathesis.readthedocs.io/en/stable/) to extract information from the OpenAPI files, [pytest](https://docs.pytest.org/en/8.2.x/) to run the tests, and [syrupy](https://github.com/tophat/syrupy) for snapshot-based comparison.

There are two ways to run the tests:

### Option 1: Manual tests against an external server

Run the tests locally against any SeaTable Server. Useful for testing a specific server or for developing new tests.

**Prerequisites:**
- Python 3.10+
- pip
- Publicly available SeaTable Server
- Two accounts (user and system-admin permission)

**Setup:**

```bash
cd tests

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment variables
cp env.example .env
# edit .env with the editor of your choice and save it...
```

**Run tests:**

```bash
cd tests
source .venv/bin/activate
source .env

# Run all tests or specific test files
pytest                                           # runs all files starting with test_xxx
pytest test_base_operations.py --color=yes -vv   # runs only one specific test file (verbose mode)
```

**Snapshots:** The tests compare API responses against stored snapshots. On first run, generate them with `pytest --snapshot-update`. The snapshots are stored in `__snapshots__/`. Make sure to commit new or updated snapshot files.

### Option 2: Automated version comparison via Docker

Compare API behavior between two SeaTable versions automatically. Go to GitHub Actions → "Version Compare" → "Run workflow" and enter the old and new version numbers.

You can choose the Docker image per version — use `seatable/seatable-enterprise` for released versions and `seatable/seatable-enterprise-testing` (private) for unreleased versions.

The workflow starts each version via Docker, runs the test suite against both, and uploads a report highlighting any differences in API responses. The Docker setup is in the `version-compare/` directory.

**Required GitHub Secrets:** `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (PAT with read access) for pulling private images.

## Publish Postman Collection

When you tag and push a new version, the corresponding Postman collection is automatically synced.
For example, to publish version 6.0 to Postman:

```
git tag postman-v6.0
git push --tags
```

Pushing the tag triggers a GitHub Action that runs the `.github/sync-with-postman.sh` script.
This action requires the GitHub secret `POSTMAN_API_KEY`, which you can generate at: https://seatable.postman.co/settings/me/api-keys.
