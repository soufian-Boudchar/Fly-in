#!/bin/bash

category="$1"

if [ -z "$category" ]; then
    echo "Usage: $0 <category>"
    echo "Example: $0 easy"
    exit 1
fi

path="maps/$category"

if [ ! -d "$path" ]; then
    echo "Category not found: $category"
    exit 1
fi

for map in "$path"/*.txt; do
    output=$(python3 -m src "$map")
    lines=$(printf '%s\n' "$output" | wc -l)

    printf "%-50s : %s lines\n" "$map" "$lines"
done