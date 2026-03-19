#!/usr/bin/env python3
"""
Generate static files for api.seatable.com from OpenAPI specs.

Generates:
  - sitemap.xml
  - llms.txt       (compact LLM overview)
  - llms-full.txt  (complete API reference for LLMs)

Usage:
  python3 custom-domain/generate.py
"""

import glob
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

import yaml

BASE_URL = "https://api.seatable.com"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SPEC_DIR = REPO_ROOT
INTRO_DIR = os.path.join(REPO_ROOT, "intro")

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

# Priority per spec file (intro pages get 0.8)
SPEC_PRIORITY = {
    "authentication.yaml": 0.7,
    "base_operations.yaml": 0.6,
    "user_account_operations.yaml": 0.5,
    "team_admin_account_operations.yaml": 0.3,
    "system_admin_account_operations.yaml": 0.3,
    "file_operations.yaml": 0.4,
    "ping_and_info.yaml": 0.2,
    "python-scheduler.yaml": 0.2,
}

SPEC_NAMES = {
    "authentication.yaml": "Authentication",
    "base_operations.yaml": "Base Operations",
    "user_account_operations.yaml": "User Account Operations",
    "team_admin_account_operations.yaml": "Team Admin Operations",
    "system_admin_account_operations.yaml": "System Admin Operations",
    "file_operations.yaml": "File Operations",
    "ping_and_info.yaml": "Ping & Info",
    "python-scheduler.yaml": "Python Scheduler",
}


def git_lastmod(filepath):
    """Get the last commit date (YYYY-MM-DD) for a file via git log."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", filepath],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()[:10]  # YYYY-MM-DD
    except FileNotFoundError:
        pass
    return None


def git_blame_dates(filepath):
    """Run git blame and return dict: line_number (1-based) -> 'YYYY-MM-DD'."""
    try:
        result = subprocess.run(
            ["git", "blame", "--line-porcelain", "--", filepath],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            return {}
    except FileNotFoundError:
        return {}

    dates = {}
    current_line = None
    for raw in result.stdout.splitlines():
        parts = raw.split()
        if len(parts) >= 3 and len(parts[0]) == 40 and parts[2].isdigit():
            current_line = int(parts[2])
        elif raw.startswith("author-time ") and current_line is not None:
            ts = int(raw.split()[1])
            dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            dates[current_line] = dt.strftime("%Y-%m-%d")
    return dates


def find_operation_line_ranges(filepath):
    """Find line ranges for each operationId in a YAML spec file.

    Returns dict: operationId -> (start_line, end_line) with 1-based inclusive lines.
    """
    with open(filepath) as f:
        lines = f.readlines()

    HTTP_METHODS = {"get:", "post:", "put:", "patch:", "delete:"}
    result = {}

    for i, line in enumerate(lines):
        if "operationId:" not in line:
            continue
        op_id = line.split("operationId:")[1].strip()
        if not op_id:
            continue

        # Walk backwards to find the HTTP method line
        method_line = i
        method_indent = None
        for j in range(i - 1, -1, -1):
            stripped = lines[j].strip()
            if stripped in HTTP_METHODS:
                method_line = j
                method_indent = len(lines[j]) - len(lines[j].lstrip())
                break

        if method_indent is None:
            continue

        # Walk forward to find end of this operation block
        end_line = len(lines) - 1
        for j in range(i + 1, len(lines)):
            stripped = lines[j].strip()
            if not stripped or stripped.startswith("#"):
                continue
            current_indent = len(lines[j]) - len(lines[j].lstrip())
            if current_indent <= method_indent:
                end_line = j - 1
                break

        result[op_id] = (method_line + 1, end_line + 1)  # Convert to 1-based

    return result


def get_operation_lastmods(filepath):
    """Get per-operation lastmod dates for a spec file.

    Returns dict: operationId -> 'YYYY-MM-DD'.
    Falls back to file-level lastmod if git blame fails.
    """
    blame_dates = git_blame_dates(filepath)
    if not blame_dates:
        fallback = git_lastmod(filepath)
        return None, fallback

    op_ranges = find_operation_line_ranges(filepath)
    op_lastmods = {}

    for op_id, (start, end) in op_ranges.items():
        max_date = None
        for line_no in range(start, end + 1):
            date = blame_dates.get(line_no)
            if date and (max_date is None or date > max_date):
                max_date = date
        if max_date:
            op_lastmods[op_id] = max_date

    return op_lastmods, None


def load_yaml(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def resolve_ref(spec, ref):
    """Resolve a $ref within a spec."""
    if not ref.startswith("#/"):
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


def get_intro_pages():
    """Extract slug and title from intro/*.md frontmatter."""
    pages = []
    for md_file in sorted(glob.glob(os.path.join(INTRO_DIR, "*.md"))):
        with open(md_file, "r") as f:
            content = f.read()
        if not content.startswith("---"):
            continue
        end = content.index("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        pages.append(
            {
                "slug": frontmatter.get("slug", ""),
                "title": frontmatter.get("title", ""),
                "excerpt": frontmatter.get("excerpt", ""),
                "file": md_file,
            }
        )
    return pages


def get_operations(spec):
    """Extract all operations from an OpenAPI spec."""
    operations = []
    for path, methods in spec.get("paths", {}).items():
        # Collect path-level parameters
        path_params = [
            resolve_parameter(spec, p) for p in methods.get("parameters", [])
        ]
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in methods:
                continue
            op = methods[method]
            params = [resolve_parameter(spec, p) for p in op.get("parameters", [])]
            # Merge path-level params (unless overridden by operation-level)
            param_names = {p.get("name") for p in params}
            for pp in path_params:
                if pp.get("name") not in param_names:
                    params.append(pp)

            # Determine auth type
            security = op.get("security", spec.get("security", []))
            auth = ""
            for s in security:
                for key in s:
                    if "Account" in key:
                        auth = "Account-Token"
                    elif "Api" in key:
                        auth = "API-Token"
                    elif "Base" in key:
                        auth = "Base-Token"
                    break
                if auth:
                    break

            operations.append(
                {
                    "operationId": op.get("operationId", ""),
                    "summary": op.get("summary", ""),
                    "description": op.get("description", ""),
                    "method": method.upper(),
                    "path": path,
                    "tags": op.get("tags", []),
                    "parameters": params,
                    "requestBody": op.get("requestBody"),
                    "auth": auth,
                }
            )
    return operations


# ---------------------------------------------------------------------------
# sitemap.xml
# ---------------------------------------------------------------------------
def generate_sitemap(intro_pages, specs_data):
    # Collect all URLs with metadata: (url, lastmod, priority)
    entries = []

    # Intro / doc pages
    for page in intro_pages:
        url = f"{BASE_URL}/reference/{page['slug']}"
        lastmod = git_lastmod(page["file"])
        entries.append((url, lastmod, 0.8))

    # API operations — lastmod per operation via git blame
    for spec_file, spec, operations in specs_data:
        spec_path = os.path.join(SPEC_DIR, spec_file)
        op_lastmods, fallback = get_operation_lastmods(spec_path)
        priority = SPEC_PRIORITY.get(spec_file, 0.3)
        for op in operations:
            if op["operationId"]:
                url = f"{BASE_URL}/reference/{op['operationId'].lower()}"
                if op_lastmods:
                    lastmod = op_lastmods.get(op["operationId"], fallback)
                else:
                    lastmod = fallback
                entries.append((url, lastmod, priority))

    # Deduplicate by URL (keep highest priority)
    seen = {}
    for url, lastmod, priority in entries:
        if url not in seen or priority > seen[url][1]:
            seen[url] = (lastmod, priority)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<?xml-stylesheet type="text/xsl" href="/sitemap.xsl"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for url in sorted(seen):
        lastmod, priority = seen[url]
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# llms.txt  (compact index)
# ---------------------------------------------------------------------------
def generate_llms_txt(intro_pages, specs_data):
    lines = [
        "# SeaTable API",
        "",
        "> SeaTable is a collaborative no-code database platform."
        " This is the official REST API reference for managing"
        " bases, tables, rows, columns, views, users, teams,"
        " automations, and more.",
        "",
        "## Documentation",
        "",
    ]
    for page in intro_pages:
        excerpt = page["excerpt"]
        if excerpt:
            lines.append(
                f"- [{page['title']}]({BASE_URL}/reference/{page['slug']}): {excerpt}"
            )
        else:
            lines.append(f"- [{page['title']}]({BASE_URL}/reference/{page['slug']})")

    lines += ["", "## API Categories", ""]
    for spec_file, spec, operations in specs_data:
        name = SPEC_NAMES.get(spec_file, spec_file)
        tags = spec.get("tags", [])
        tag_list = ", ".join(t["name"] for t in tags)
        lines.append(f"- **{name}** ({len(operations)} endpoints): {tag_list}")

    lines += [
        "",
        "## Complete API Reference",
        "",
        f"- [llms-full.txt]({BASE_URL}/llms-full.txt): Complete API reference"
        " with all endpoints, parameters, and descriptions",
        "",
        "## Optional",
        "",
        "- [SeaTable Website](https://seatable.com): Product website with features, pricing, and use cases",
        "- [Developer Manual](https://developer.seatable.com): Tutorials, SDK documentation, and code examples",
        "- [Admin Manual](https://admin.seatable.com): Self-hosting installation, configuration, and administration",
        "- [Community Forum](https://forum.seatable.com): Community support, discussions, and feature requests",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# llms-full.txt  (complete reference)
# ---------------------------------------------------------------------------
def clean_description(desc):
    """Remove HTML/style blocks that are meaningless for LLMs."""
    if not desc:
        return ""
    out = []
    skip = False
    for line in desc.strip().splitlines():
        s = line.strip()
        if s.startswith("<style"):
            skip = True
            continue
        if skip:
            if "</style>" in s:
                skip = False
            continue
        out.append(line)
    return "\n".join(out).strip()


def format_params(params):
    """Format parameters as a compact markdown list."""
    lines = []
    for p in params:
        name = p.get("name", "?")
        location = p.get("in", "?")
        required = "required" if p.get("required") else "optional"
        schema = p.get("schema", {})
        ptype = schema.get("type", "")
        enum = schema.get("enum")
        desc = (p.get("description") or "").strip().replace("\n", " ")
        line = f"- `{name}` ({location}, {ptype}, {required})"
        if desc:
            line += f": {desc}"
        if enum:
            line += f" Values: {', '.join(str(e) for e in enum)}"
        lines.append(line)
    return "\n".join(lines)


def format_request_body(rb):
    """Format request body properties as a compact markdown list."""
    if not rb:
        return ""
    lines = []
    for content_type, media in rb.get("content", {}).items():
        schema = media.get("schema", {})
        props = schema.get("properties", {})
        if not props:
            continue
        lines.append(f"**Request body** ({content_type}):")
        lines.append("")
        required_fields = set(schema.get("required", []))
        for prop_name, prop_schema in props.items():
            ptype = prop_schema.get("type", "")
            pdesc = (prop_schema.get("description") or "").strip().replace("\n", " ")
            req = "required" if prop_name in required_fields else "optional"
            line = f"- `{prop_name}` ({ptype}, {req})"
            if pdesc:
                line += f": {pdesc}"
            example = prop_schema.get("example")
            if example is not None and not isinstance(example, (dict, list)):
                line += f" Example: `{example}`"
            lines.append(line)
    return "\n".join(lines)


def generate_llms_full_txt(specs_data):
    lines = [
        "# SeaTable API Reference",
        "",
        "SeaTable is a collaborative no-code database platform."
        " This is the complete REST API reference.",
        "",
        "Base URL: `https://cloud.seatable.io` (SeaTable Cloud)"
        " or your self-hosted server URL.",
        "",
        "## Authentication",
        "",
        "SeaTable uses three types of bearer tokens:",
        "",
        "- **Account-Token**: Generated from username/password."
        " Used for account-level operations (manage bases, groups, shares).",
        "- **API-Token**: Created in the SeaTable UI for a specific base."
        " Permanent. Used to generate Base-Tokens.",
        "- **Base-Token**: Generated from an API-Token or Account-Token."
        " Valid for 3 days. Used for all operations within a base"
        " (rows, columns, tables, views).",
        "",
        "Pass tokens via the `Authorization: Bearer {token}` header.",
        "",
    ]

    for spec_file, spec, operations in specs_data:
        name = SPEC_NAMES.get(spec_file, spec_file)
        lines += [f"## {name}", ""]

        # Group by tag
        tagged = {}
        for op in operations:
            tag = op["tags"][0] if op["tags"] else "Other"
            tagged.setdefault(tag, []).append(op)

        for tag, ops in tagged.items():
            lines += [f"### {tag}", ""]
            for op in ops:
                summary = op["summary"] or op["operationId"]
                lines += [f"#### {summary}", ""]
                lines.append(f"`{op['method']} {op['path']}`")
                if op["auth"]:
                    lines.append(f"Auth: {op['auth']}")
                lines.append("")

                desc = clean_description(op.get("description", ""))
                if desc:
                    lines += [desc, ""]

                if op["parameters"]:
                    lines += ["**Parameters:**", "", format_params(op["parameters"]), ""]

                rb = format_request_body(op.get("requestBody"))
                if rb:
                    lines += [rb, ""]

                lines += ["---", ""]

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    intro_pages = get_intro_pages()

    specs_data = []
    all_operations = []
    for spec_file in SPEC_FILES:
        spec_path = os.path.join(SPEC_DIR, spec_file)
        if not os.path.exists(spec_path):
            print(f"Warning: {spec_path} not found, skipping", file=sys.stderr)
            continue
        spec = load_yaml(spec_path)
        operations = get_operations(spec)
        specs_data.append((spec_file, spec, operations))
        all_operations.extend(operations)

    sitemap = generate_sitemap(intro_pages, specs_data)
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w") as f:
        f.write(sitemap)
    print(f"sitemap.xml   — {len(intro_pages)} doc pages + {len(all_operations)} operations")

    llms_txt = generate_llms_txt(intro_pages, specs_data)
    with open(os.path.join(OUTPUT_DIR, "llms.txt"), "w") as f:
        f.write(llms_txt)
    print(f"llms.txt      — {len(llms_txt):,} bytes")

    llms_full = generate_llms_full_txt(specs_data)
    with open(os.path.join(OUTPUT_DIR, "llms-full.txt"), "w") as f:
        f.write(llms_full)
    print(f"llms-full.txt — {len(llms_full):,} bytes")


if __name__ == "__main__":
    main()
