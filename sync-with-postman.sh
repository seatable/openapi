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

DESCRIPTION="This is the reference for the SeaTable API. On this page you will find everything you need to know to use SeaTable's API.

    The SeaTable API is organized around REST. This means: SeaTable's API has predictable resource-oriented URLs, accepts form-encoded request bodies, returns JSON-encoded responses, and uses standard HTTP response codes, authentication, and verbs.

    With SeaTable, you can design individual databases, workflows and apps in no time at all - without any programming knowledge.
    Our no-code solution combines the intuitive operation of tables with the power of modern database and app builder functions and also impresses as a flexible low-code platform for all users.
"

# Set description (required for Postman verification)
jq --arg description "${DESCRIPTION}" '.collection.info.description = $description' postman/collection.wrapped.json | sponge postman/collection.wrapped.json

# Create Postman collection
response=$(curl -X POST "https://api.getpostman.com/collections?workspace=80b1ca4c-1f9e-41bf-b0e1-6bde43e012fc" \
    -H "X-Api-Key: $POSTMAN_API_KEY" \
    -H 'Content-Type: application/json' \
    --data '@postman/collection.wrapped.json')
