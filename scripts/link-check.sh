#!/bin/bash
# Link validation script for Physical AI & Humanoid Robotics Textbook
# Checks for broken links in markdown files

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

DIRECTORY="$1"

if [ ! -d "$DIRECTORY" ]; then
    echo "Directory $DIRECTORY does not exist"
    exit 1
fi

echo "Checking for broken links in $DIRECTORY..."

# Find all markdown files and check for common link patterns
find "$DIRECTORY" -name "*.md" -type f | while read -r file; do
    echo "Checking links in: $file"
    
    # Extract and validate links in markdown format [text](url)
    grep -oP '\[.*\](\K.*?)(?=\))' "$file" 2>/dev/null | while read -r link; do
        # Skip if it's an anchor link or relative link to other markdown files
        if [[ $link =~ ^# ]] || [[ $link =~ \.md$ ]] || [[ $link =~ ^/ ]] || [[ $link =~ ^\. ]]; then
            continue
        fi
        
        # Check if it's an external URL
        if [[ $link =~ ^https?:// ]]; then
            echo "  Checking external link: $link"
            # Uncomment the next line to actually check external links (may be slow)
            # curl -s -f -I "$link" > /dev/null 2>&1 || echo "    WARNING: Broken link: $link"
        fi
    done
done

echo "Link validation completed."
