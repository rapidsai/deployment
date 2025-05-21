#!/bin/bash

set -e -u -o pipefail

imagepaths=$(find source -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.gif" -o -iname "*.svg" \) ! -path "./build/*" ! -path "./node_modules/*" ! -path "./jupyter_execute/*" ! -path "./.ipynb_checkpoints/*")
counter=0

for imagepath in $imagepaths; do
    filename=$(basename -- "$imagepath")
    if ! grep -q -r --exclude-dir=".git" --exclude-dir="build" --exclude-dir="node_modules" --exclude-dir="jupyter_execute" --exclude-dir=".ipynb_checkpoints" "$filename" source README.md; then
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
