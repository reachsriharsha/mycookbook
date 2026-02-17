#!/bin/bash
# This shell script is used to find huge files and folders in a directory recursively.
#
# Usage: ./find_huge.sh <directory> <size>
#
# Example: ./find_huge.sh /var/log 100M
# The size argument format is the same as for the `find` command (e.g., 100M, 1G).

# --- Configuration ---
TARGET_DIR=$1
SIZE_THRESHOLD=$2

# --- Validation ---
if [ -z "$TARGET_DIR" ] || [ -z "$SIZE_THRESHOLD" ]; then
    echo "Error: Missing arguments."
    echo "Usage: $0 <directory> <size>"
    echo "Example: $0 /var/log 100M"
    exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
    echo "Error: Directory '$TARGET_DIR' not found."
    exit 1
fi

# --- Main Logic ---

echo "--- Searching for files larger than $SIZE_THRESHOLD in '$TARGET_DIR' ---"
# Use find to locate files. -type f specifies files only.
# -size +$SIZE_THRESHOLD finds files greater than the specified size.
# -exec ls -lh {} + is an efficient way to list file details.
find "$TARGET_DIR" -type f -size +$SIZE_THRESHOLD -exec ls -lh {} + 2>/dev/null | sort -rh -k 5

echo ""
echo "--- Searching for directories larger than $SIZE_THRESHOLD in '$TARGET_DIR' ---"
# Use du to get disk usage of directories.
# -h for human-readable sizes.
# --threshold ensures we only see directories meeting the size criteria.
# The output is piped to sort for clear ordering.
du -h --threshold=$SIZE_THRESHOLD "$TARGET_DIR" 2>/dev/null | sort -rh

echo ""
echo "Search complete."

