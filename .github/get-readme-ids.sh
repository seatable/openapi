#!/usr/bin/env bash

# Collects the ReadMe IDs of a version and offers to write them into the repo
# (steps 3 and 4 of .github/workflows/rdme-openapi.yml):
#
#   - the API definition IDs for .github/readme-ids.json, matched to the spec
#     files by info.title. The titles have to match exactly: ReadMe also holds
#     an outdated "Base Operations (before 4.4)" definition.
#   - the category ID for the intro/*.md frontmatter, read from the introduction
#     page itself. Forking a version copies its docs, so that page already
#     carries the category ID of the new version.
#
# The legacy v1 API is still available for our project; only its reference page
# on docs.readme.com was replaced by the ReadMe Refactored (v2) one.
#
# The category ID goes to stdout, everything else to stderr.
#
# Usage: .github/get-readme-ids.sh [version] [--write]
#        version defaults to the current branch, --write skips the prompts

set -euo pipefail

WRITE=false
VERSION=''
for arg in "$@"; do
    case "$arg" in
        -w|--write) WRITE=true ;;
        *) VERSION="$arg" ;;
    esac
done

VERSION="${VERSION:-$(git branch --show-current)}"
VERSION="${VERSION#v}"
SLUG='introduction'
REPO_ROOT="$(git rev-parse --show-toplevel)"
IDS_FILE="${REPO_ROOT}/.github/readme-ids.json"
INTRO_DIR="${REPO_ROOT}/intro"

if [[ -z "${README_API_KEY-}" ]]; then
    if [[ ! -t 0 ]]; then
        echo 'Error: $README_API_KEY is not set' >&2
        exit 1
    fi
    echo "Get the key from https://dash.readme.com/project/seatable/v${VERSION}/api-key" >&2
    read -rsp "ReadMe API key: " README_API_KEY
    echo >&2
fi

# The API key is passed as the username part of basic auth, the password stays empty
readme_api() {
    local response http_code body
    response=$(curl -s -w '\n%{http_code}' -u "${README_API_KEY}:" \
        -H "x-readme-version: ${VERSION}" "https://dash.readme.com/api/v1/$1")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" -lt 200 || "$http_code" -ge 300 ]]; then
        echo "Error: ReadMe API returned HTTP ${http_code} for /${1}" >&2
        echo "$body" | jq -r '.message? // .' >&2
        exit 1
    fi
    echo "$body"
}

# Returns 1 when there is nothing to confirm with, so the ID can still be piped
confirm() {
    [[ "$WRITE" == true ]] && return 0
    [[ -t 0 && -t 1 ]] || return 1

    local answer
    read -rp "$1 [y/N] " answer
    [[ "$answer" == [Yy] ]]
}

spec_title() {
    python3 -c 'import sys, yaml; print(yaml.safe_load(open(sys.argv[1]))["info"]["title"])' "$1"
}

# ---------------------------------------------------------------------------
# API definition IDs -> .github/readme-ids.json
# ---------------------------------------------------------------------------

specs=$(readme_api 'api-specification?perPage=100&page=1')
new_ids=$(jq -n --arg version "$VERSION" '{version: $version}')

# Iterate over the existing keys to keep the order of the file (and python_scheduler
# -> python-scheduler.yaml, the only key whose spec file uses a dash)
while read -r key; do
    spec="${REPO_ROOT}/${key}.yaml"
    [[ -f "$spec" ]] || spec="${REPO_ROOT}/${key//_/-}.yaml"
    if [[ ! -f "$spec" ]]; then
        echo "Error: no spec file for key \"${key}\"" >&2
        exit 1
    fi

    title=$(spec_title "$spec")
    id=$(echo "$specs" | jq -r --arg title "$title" \
        '[.[] | select(.title == $title) | .id] | if length == 1 then .[0] else "" end')
    if [[ -z "$id" ]]; then
        echo "Error: no single API definition titled \"${title}\" in v${VERSION}" >&2
        exit 1
    fi

    printf '%-36s %s (%s)\n' "$id" "$title" "${spec##*/}" >&2
    new_ids=$(echo "$new_ids" | jq --arg key "$key" --arg id "$id" '.[$key] = $id')
done < <(jq -r 'keys_unsorted[] | select(. != "version")' "$IDS_FILE")

# A spec file added since the last version needs its own key in readme-ids.json
for spec in "$REPO_ROOT"/*.yaml; do
    key=$(basename "$spec" .yaml | tr '-' '_')
    jq -e --arg key "$key" 'has($key)' "$IDS_FILE" >/dev/null \
        || echo "Warning: ${spec##*/} has no entry in readme-ids.json" >&2
done

if [[ "$(jq -S . "$IDS_FILE")" == "$(echo "$new_ids" | jq -S .)" ]]; then
    echo "readme-ids.json is up to date" >&2
else
    diff <(jq . "$IDS_FILE") <(echo "$new_ids" | jq .) >&2 || true
    if confirm "Write these IDs to .github/readme-ids.json?"; then
        echo "$new_ids" | jq . > "$IDS_FILE"
        echo "Updated .github/readme-ids.json" >&2
    fi
fi

# ---------------------------------------------------------------------------
# Category ID -> intro/*.md frontmatter
# ---------------------------------------------------------------------------

category=$(readme_api "docs/${SLUG}" | jq -r '.category')

# Name the category so the ID can be sanity-checked before it is used. The intro
# pages have their own category, so it is not part of the api-specification data.
readme_api 'categories?perPage=100&page=1' \
    | jq -r --arg id "$category" --arg version "$VERSION" \
        '.[] | select(._id == $id) | "v\($version) \(.type) category: \(.title) (\(.slug))"' >&2

echo "$category"

current=$(sed -n 's/^category: //p' "${INTRO_DIR}"/*.md | sort -u | paste -sd ', ' -)

if [[ "$current" == "$category" ]]; then
    echo "intro/*.md already use this category" >&2
    exit 0
fi

if confirm "Replace category in intro/*.md (currently ${current})?"; then
    sed -i "s/^category: .*/category: ${category}/" "${INTRO_DIR}"/*.md
    echo "Updated category in $(ls "${INTRO_DIR}"/*.md | wc -l) files in intro/" >&2
fi
