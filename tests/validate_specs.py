#!/usr/bin/env python3
"""
Validate OpenAPI spec quality rules.

Checks enforced:
  1. All operationIds must be camelCase (start with lowercase letter)
  2. Every operation must have a summary
  3. Every operation must have a description
  4. Every operation must have at least one response defined
  5. Every success response (2xx) must have content with a schema or example
  6. All auth.local examples must match ^[a-f0-9]{32}@auth.local$
  7. No non-ASCII characters in example values (catches leftover non-English text)
  8. No duplicate operationIds within the same spec file

Usage:
  python3 tests/validate_specs.py
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


def check_camel_case(op_id):
    """operationId must start with a lowercase letter."""
    return op_id[0].islower() if op_id else False


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
            is_example = in_example or k == "example" or k == "examples"
            violations.extend(
                find_non_ascii_in_examples(v, f"{path}.{k}", is_example)
            )
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            violations.extend(
                find_non_ascii_in_examples(v, f"{path}[{i}]", in_example)
            )
    return violations


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

        # Check for non-ASCII in examples
        for v in find_non_ascii_in_examples(spec):
            errors.append(f"{spec_file}: Non-ASCII in example at {v[0]}: {v[1]}")

        # Check for auth.local violations
        for v in find_auth_local_violations(spec):
            errors.append(
                f"{spec_file}: Invalid auth.local example at {v[0]}: {v[1]}"
            )

        for path, methods in spec.get("paths", {}).items():
            for method in ("get", "post", "put", "patch", "delete"):
                if method not in methods:
                    continue
                op = methods[method]
                op_id = op.get("operationId", "")
                loc = f"{spec_file}: {method.upper()} {path}"

                # 1. operationId must be camelCase
                if op_id and not check_camel_case(op_id):
                    errors.append(
                        f"{loc}: operationId '{op_id}' must start with lowercase (camelCase)"
                    )

                # 2. Must have summary
                if not op.get("summary"):
                    errors.append(f"{loc}: Missing summary")

                # 3. Must have description
                if not op.get("description"):
                    errors.append(f"{loc}: Missing description")

                # 4. Must have at least one response
                responses = op.get("responses", {})
                if not responses:
                    errors.append(f"{loc}: No responses defined")

                # 5. Success responses (2xx) should have content
                for status, resp in responses.items():
                    if str(status).startswith("2") and not resp.get("content"):
                        errors.append(
                            f"{loc}: Response {status} has no content/schema/example"
                        )

                # 8. Duplicate operationId within same file
                if op_id:
                    if op_id in file_operation_ids:
                        errors.append(
                            f"{loc}: Duplicate operationId '{op_id}' "
                            f"(also at {file_operation_ids[op_id]})"
                        )
                    else:
                        file_operation_ids[op_id] = loc

    return errors


def main():
    strict = "--strict" in sys.argv
    errors = validate_specs()
    if errors:
        print(f"Found {len(errors)} quality issue(s):\n")
        for e in sorted(errors):
            print(f"  - {e}")
        if strict:
            sys.exit(1)
        else:
            print(f"\nRun with --strict to fail on these issues.")
            sys.exit(0)
    else:
        print("All quality checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
