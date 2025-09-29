#!/bin/bash

set -e -u -o pipefail

imagepaths=$(find source -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.svg" \))
counter=0

for imagepath in $imagepaths; do
    filename=$(basename -- "$imagepath")
    if ! grep -q -r "$filename" --include '*.md' --include '*.ipynb' --include '*.py' source README.md; then
        echo "Found unused image $imagepath"
        counter=$((counter+1))
    fi
done

if [ "$counter" -eq "0" ]; then
    echo "No unused images found!"
else
    echo "Found $counter unused images"
    exit 1
fi
