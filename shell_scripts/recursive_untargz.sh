#!/bin/bash

# Function to extract all tar.gz files in the current directory and subdirectories
extract_recursive() {
    local found=true

    while [ "$found" = true ]; do
        # Find all .tar.gz files
        files=$(find . -name "*.tgz")

        if [ -z "$files" ]; then
            found=false
            echo "No more .tar.gz files found."
        else
            for f in $files; do
                echo "Extracting: $f"
                # Extract in the same directory as the file
                tar -xzvf "$f" -C "$(dirname "$f")"
                # Optional: Remove the archive after extraction to avoid infinite loops
                rm "$f"
            done
        fi
    done
}

extract_recursive

