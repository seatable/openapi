#!/usr/bin/env bash

set -euo pipefail

if [[ -z "${POSTMAN_API_KEY-}" ]]; then
    echo 'Error: $POSTMAN_API_KEY is not set'
    exit 1
fi

if [[ -z "${COLLECTION_NAME-}" ]]; then
    echo 'Error: $COLLECTION_NAME is not set'
    exit 1
fi

mkdir -p postman

# Convert spec files to Postman collections
for filename in *.yaml; do
    # https://github.com/postmanlabs/openapi-to-postman#-command-line-interface
    # %.* is used to strip the file extension
    openapi2postmanv2 -s "${filename}" -o "postman/${filename%.*}.json" --pretty --options folderStrategy=Tags
done

# Combine collections
# https://www.npmjs.com/package/postman-combine-collections
# npm i -g postman-combine-collections
postman-combine-collections -f 'postman/*.json' --name "${COLLECTION_NAME}" -o postman/collection.json

# Wrap everything in an object under a "collection" key
# This is expected by Postman's API even though exported collections do not contain this key ¯\_(ツ)_/¯
# https://www.postman.com/postman/workspace/postman-public-workspace/request/12959542-049042b8-447f-4f71-8b79-ae978cf40a04
jq '{"collection": .}' < postman/collection.json > postman/collection.wrapped.json

# Create Postman collection
curl -X POST "https://api.getpostman.com/collections" \
    -H "X-Api-Key: $POSTMAN_API_KEY" \
    -H 'Content-Type: application/json' \
    --data '@postman/collection.wrapped.json'
