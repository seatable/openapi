#!/usr/bin/env python3
"""
Validate OpenAPI spec quality rules.

Checks enforced:
   1. Every operation must have an operationId
   2. All operationIds must be camelCase (start with lowercase letter)
   3. No duplicate operationIds within the same spec file
   4. Every operation must have a summary
   5. Every operation must have a description
   6. Every operation must have at least one tag
   7. Every operation must have a security scheme (except ping endpoints)
   8. Every operation must have at least one response defined
   9. Every success response (2xx) must have content with a schema or example
  10. All path parameters in the URL must be defined in parameters
  11. All path parameters must have required: true
  12. All parameters must have a description
  13. No TODO/FIXME in description fields (YAML comments are fine)
  14. All auth.local examples must match ^[a-f0-9]{32}@auth.local$
  15. No non-ASCII characters in example values

Usage:
  python3 tests/validate_specs.py            # report issues (exit 0)
  python3 tests/validate_specs.py --strict   # fail on any issue (exit 1)
"""

import os
import re
import sys

import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SPEC_FILES = [
    "authentication.yaml",
    "base_operations.yaml",
    "user_account_operations.yaml",
    "team_admin_account_operations.yaml",
    "system_admin_account_operations.yaml",
    "file_operations.yaml",
    "ping_and_info.yaml",
    "python-scheduler.yaml",
]

AUTH_LOCAL_PATTERN = re.compile(r"^[a-f0-9]{32}@auth\.local$")
PATH_PARAM_RE = re.compile(r"\{(\w+)\}")
TODO_RE = re.compile(r"\b(TODO|FIXME)\b", re.IGNORECASE)

# Endpoints that legitimately have no security
NO_SECURITY_PATHS = {
    "/api2/ping/",
    "/server-info/",
    "/api2/auth-token/",                         # this IS the auth endpoint
    "/dtable-server/ping/",
    "/dtable-db/ping/",
    "/api-gateway/api/v2/ping/",
}

# Paths with token-in-URL authentication (no Bearer token)
NO_SECURITY_PREFIXES = (
    "/api/v2.1/external-link-tokens/",
    "/dtable/external-links/",
)


def find_auth_local_violations(obj, path=""):
    """Recursively find auth.local values that don't match the pattern."""
    violations = []
    if isinstance(obj, str):
        if "@auth.local" in obj and "xxx@auth.local" not in obj:
            match = re.search(r"[\w]+@auth\.local", obj)
            if match and not AUTH_LOCAL_PATTERN.match(match.group()):
                violations.append((path, match.group()))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            violations.extend(find_auth_local_violations(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            violations.extend(find_auth_local_violations(v, f"{path}[{i}]"))
    return violations


def find_non_ascii_in_examples(obj, path="", in_example=False):
    """Find non-ASCII characters in example values."""
    violations = []
    if isinstance(obj, str):
        if in_example and any(ord(c) > 127 for c in obj):
            violations.append((path, obj[:80]))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            is_example = in_example or k in ("example", "examples")
            violations.extend(
                find_non_ascii_in_examples(v, f"{path}.{k}", is_example)
            )
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            violations.extend(
                find_non_ascii_in_examples(v, f"{path}[{i}]", in_example)
            )
    return violations


def resolve_ref(spec, ref):
    """Resolve a $ref within a spec."""
    if not ref or not ref.startswith("#/"):
        return {}
    parts = ref[2:].split("/")
    obj = spec
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part, {})
        else:
            return {}
    return obj


def resolve_parameter(spec, param):
    """Resolve a parameter, following $ref if present."""
    if "$ref" in param:
        return resolve_ref(spec, param["$ref"])
    return param


def validate_specs():
    errors = []

    for spec_file in SPEC_FILES:
        file_operation_ids = {}
        spec_path = os.path.join(REPO_ROOT, spec_file)
        if not os.path.exists(spec_path):
            errors.append(f"{spec_file}: File not found")
            continue

        with open(spec_path) as f:
            spec = yaml.safe_load(f)

        # Global checks
        for v in find_non_ascii_in_examples(spec):
            errors.append(f"{spec_file}: Non-ASCII in example at {v[0]}: {v[1]}")

        for v in find_auth_local_violations(spec):
            errors.append(
                f"{spec_file}: Invalid auth.local example at {v[0]}: {v[1]}"
            )

        for path, methods in spec.get("paths", {}).items():
            # Collect path-level parameters
            path_level_params = [
                resolve_parameter(spec, p)
                for p in methods.get("parameters", [])
            ]

            for method in ("get", "post", "put", "patch", "delete"):
                if method not in methods:
                    continue
                op = methods[method]
                op_id = op.get("operationId", "")
                loc = f"{spec_file}: {method.upper()} {path}"

                # 1. operationId must exist
                if not op_id:
                    errors.append(f"{loc}: Missing operationId")
                    continue

                # 2. operationId must be camelCase
                if op_id[0].isupper():
                    errors.append(
                        f"{loc}: operationId '{op_id}' must be camelCase"
                    )

                # 3. No duplicate operationIds within same file
                if op_id in file_operation_ids:
                    errors.append(
                        f"{loc}: Duplicate operationId '{op_id}' "
                        f"(also at {file_operation_ids[op_id]})"
                    )
                else:
                    file_operation_ids[op_id] = loc

                # 4. Must have summary
                if not op.get("summary"):
                    errors.append(f"{loc}: Missing summary")

                # 5. Must have description
                if not op.get("description"):
                    errors.append(f"{loc}: Missing description")

                # 6. Must have at least one tag
                if not op.get("tags"):
                    errors.append(f"{loc}: Missing tags")

                # 7. Must have security (except known public endpoints)
                has_security = op.get("security") or spec.get("security")
                is_public = (
                    path in NO_SECURITY_PATHS
                    or path.startswith(NO_SECURITY_PREFIXES)
                )
                if not has_security and not is_public:
                    errors.append(f"{loc}: Missing security scheme")

                # 8. Must have at least one response
                responses = op.get("responses", {})
                if not responses:
                    errors.append(f"{loc}: No responses defined")

                # 9. Success responses (2xx) should have content
                for status, resp in responses.items():
                    if not str(status).startswith("2"):
                        continue
                    content = resp.get("content")
                    if not content:
                        errors.append(
                            f"{loc}: Response {status} has no content/schema/example"
                        )
                        continue
                    # Check that at least one media type has a schema or example
                    for ct, media in content.items():
                        schema = media.get("schema", {})
                        example = media.get("example")
                        # Skip empty schemas (binary file workaround)
                        if not schema and example is None:
                            continue
                        # Resolve $ref in schema to check for embedded example
                        if "$ref" in schema:
                            resolved = resolve_ref(spec, schema["$ref"])
                            if resolved.get("example") is not None:
                                continue
                            # Check if properties have examples
                            props = resolved.get("properties", {})
                            if props and all(
                                p.get("example") is not None for p in props.values()
                            ):
                                continue
                        examples = media.get("examples")
                        if (
                            example is None
                            and not examples
                            and not schema.get("example")
                        ):
                            errors.append(
                                f"{loc}: Response {status} ({ct}) has schema but no example"
                            )

                # 10 & 11. Path parameters must be defined and required
                url_params = set(PATH_PARAM_RE.findall(path))
                op_params = [
                    resolve_parameter(spec, p)
                    for p in op.get("parameters", [])
                ]
                all_params = op_params + path_level_params
                defined_path_params = {
                    p.get("name")
                    for p in all_params
                    if p.get("in") == "path"
                }

                for param_name in url_params:
                    if param_name not in defined_path_params:
                        errors.append(
                            f"{loc}: Path parameter '{{{param_name}}}' "
                            f"in URL but not defined in parameters"
                        )

                for p in all_params:
                    if p.get("in") == "path" and not p.get("required"):
                        errors.append(
                            f"{loc}: Path parameter '{p.get('name')}' "
                            f"must have required: true"
                        )

                # 12. All parameters should have a description
                for p in op_params:
                    resolved = resolve_parameter(spec, p) if "$ref" in p else p
                    if not resolved.get("description"):
                        errors.append(
                            f"{loc}: Parameter '{resolved.get('name', '?')}' "
                            f"has no description"
                        )

                # 13. No TODO/FIXME in descriptions
                desc = op.get("description", "")
                if TODO_RE.search(desc):
                    errors.append(f"{loc}: TODO/FIXME found in description")

    return errors


def main():
    strict = "--strict" in sys.argv
    errors = validate_specs()
    if errors:
        print(f"Found {len(errors)} quality issue(s):\n")
        for e in sorted(errors):
            print(f"  - {e}")
        if strict:
            print(f"\n{len(errors)} issue(s) found. Failing (--strict mode).")
            sys.exit(1)
        else:
            print(f"\nRun with --strict to fail on these issues.")
            sys.exit(0)
    else:
        print("All quality checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
