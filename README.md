# SeaTable OpenAPI

This repository contains all supported API calls for the SeaTable Server as OpenAPI 3.0 definitions. It serves two primary purposes:

1. Generate the online API reference at https://api.seatable.com (via ReadMe.com).
2. Generate the Postman collection at https://www.postman.com/seatable.
3. Generate the official [SeaTable PHP client](https://github.com/seatable/seatable-api-php) via OpenAPI Generator.

The repository is organized into version branches (e.g. `v6.1`, `v6.2`).

## Publish workflow

Every push to a version branch triggers the workflow in `.github/workflows/rdme-openapi.yml`, which runs two jobs:

### Job 1: Publish to ReadMe

1. **Link check** — validates all URLs in docs and specs using [lychee](https://github.com/lycheeverse/lychee)
2. **Spec validation** — validates all 8 OpenAPI specs using swagger-cli
3. **Quality check** — runs `tests/validate_specs.py` to enforce documentation quality rules (see below)
4. **Publish** — syncs intro docs and all OpenAPI specs to ReadMe.com

The ReadMe category IDs for each version are stored in `.github/readme-ids.json`.

### Job 2: Deploy static files

Generates and deploys static files to the api.seatable.com vserver via rsync:

- **sitemap.xml** — generated from specs with per-endpoint `lastmod` (via git blame) and per-category priority
- **llms.txt** / **llms-full.txt** — LLM-readable API reference ([llms.txt standard](https://llmstxt.org/))
- **robots.txt** — static file from `custom-domain/robots.txt`
- **sitemap.xsl** — XSL stylesheet for human-readable sitemap rendering

See `custom-domain/README.md` for server configuration details.

### Quality checks

The script `tests/validate_specs.py` enforces the following rules:

| # | Check | Description |
|---|-------|-------------|
| 1 | operationId exists | Every operation must have an operationId |
| 2 | camelCase | All operationIds must start with a lowercase letter |
| 3 | No duplicates | No duplicate operationIds within the same spec file |
| 4 | Summary | Every operation must have a summary |
| 5 | Description | Every operation must have a description |
| 6 | Tags | Every operation must have at least one tag |
| 7 | Security | Every operation must declare a security scheme (public endpoints exempted) |
| 8 | Responses | Every operation must have at least one response |
| 9 | Response content | Every 2xx response must have a schema or example |
| 10 | Path params defined | Path parameters in the URL must be defined in parameters |
| 11 | Path params required | Path parameters must have `required: true` |
| 12 | Param descriptions | All parameters must have a description |
| 13 | No TODO in descriptions | No TODO/FIXME in description fields (YAML comments are fine) |
| 14 | auth.local pattern | All auth.local examples must match `^[a-f0-9]{32}@auth.local$` |
| 15 | English only | No non-ASCII characters in example values |
| 16 | Example-schema match | Examples must match their schema (required fields, types, enums) |
| 17 | Schema completeness | Response schemas with `type: object` should define properties *(warning only)* |

Checks 1-16 are enforced in `--strict` mode (fail the build). Check 17 is advisory (reported but never fails).

Run locally: `python3 tests/validate_specs.py` (report) or `python3 tests/validate_specs.py --strict` (fail on errors).

### Breaking change detection

The workflow uses [oasdiff](https://github.com/oasdiff/oasdiff) to compare the current specs against the main branch (v6.0). Breaking changes are reported in the workflow summary but do not block the build — changes between versions are expected. Update the base branch reference in the workflow when the main branch changes.

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

### Option 1: Manual tests

Run the tests locally against a SeaTable Server. Useful for testing a specific server or for developing new tests.

**Prerequisites:**
- Python 3.10+
- pip

**SeaTable Installation:**

```bash
cd version-compare

# seatable/seatable-enterprise or seatable/seatable-enterprise-testing
export SEATABLE_IMAGE=seatable/seatable-enterprise
export SEATABLE_VERSION=6.0.10

# Create license file
cp "SOURCE" seatable-license.txt

docker compose up -d

./setup.sh
```

**Setup:**

```bash
cd tests

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Run tests:**

```bash
cd tests
source .venv/bin/activate
set -a && source ../version-compare/.env && set +a

# Run all tests or specific test files
pytest                                           # runs all files starting with test_xxx
pytest test_base_operations.py --color=yes -vv   # runs only one specific test file (verbose mode)
```

**Snapshots:** The tests compare API responses against stored snapshots. On first run, generate them with `pytest --snapshot-update`. The snapshots are stored in `__snapshots__/`. Make sure to commit new or updated snapshot files.

### Option 2: Automated version comparison via Docker

Compare API behavior between two SeaTable versions automatically. Go to GitHub Actions → "Version Compare" → "Run workflow" and enter the old and new version numbers.

You can choose the Docker image per version — use `seatable/seatable-enterprise` for released versions and `seatable/seatable-enterprise-testing` (private) for unreleased versions.

The workflow starts each version via Docker, runs the test suite against both, and uploads a report highlighting any differences in API responses. The Docker setup is in the `version-compare/` directory.

**Required GitHub Secrets:** `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` (PAT with read access) for pulling private images, and `SEATABLE_LICENSE` (SeaTable Enterprise license file content).

## Publish Postman Collection

When you tag and push a new version, the corresponding Postman collection is automatically synced.
For example, to publish version 6.0 to Postman:

```
git tag postman-v6.0
git push --tags
```

Pushing the tag triggers a GitHub Action that runs the `.github/sync-with-postman.sh` script.
This action requires the GitHub secret `POSTMAN_API_KEY`, which you can generate at: https://seatable.postman.co/settings/me/api-keys.
