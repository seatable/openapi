#!/bin/bash

echo "Extracting links into /tmp/seatable-openapi-links.txt"
grep -oP --no-filename '\]\(\K[^\)]+(?=\))' intro/*.md ./*.yaml | awk '/^\// {print "https://api.seatable.com" $0; next} {print}' > /tmp/seatable-openapi-links.txt

# clean unwanted urls:
sed -i '/^https/!d' /tmp/seatable-openapi-links.txt

COUNT=$(wc -l < /tmp/seatable-openapi-links.txt)
echo -e "Found ${COUNT} links!\n"

INPUT_FILE="/tmp/seatable-openapi-links.txt"
NOW=$(date +"%Y-%m-%d-%H-%M-%S")
OUTPUT_FILE="result-${NOW}.txt"

# Process URLs
while IFS= read -r url; do
    if [ -z "$url" ]; then
        continue
    fi

    echo "Checking: $url"

    response=$(curl -s -o /dev/null -w "%{http_code} %{url_effective}" -I -L -m 10 "$url" 2>&1)
    status_code=$(echo "$response" | awk '{print $1}')

    echo "$status_code | $url" >> "$OUTPUT_FILE"
done < "$INPUT_FILE"

echo "Report generated: $OUTPUT_FILE"
