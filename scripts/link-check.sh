#!/bin/bash
# Link validation script for Physical AI & Humanoid Robotics Textbook
# Checks for broken internal links in markdown files

echo "Running link validation..."

# Find all markdown files
MARKDOWN_FILES=$(find docs -name "*.md" -type f)

BROKEN_LINKS_FOUND=0

for file in $MARKDOWN_FILES; do
    echo "Checking links in $file..."

    # Extract internal links from markdown file
    LINKS=$(grep -oE '\[.*\]\(([^)]+)\)' "$file" | grep -oE '\(([^)]+)\)' | sed 's/[()]//g' | grep -E '^\.\.\/|^\.' | head -100)

    while IFS= read -r link; do
        if [[ -n "$link" ]]; then
            # Convert relative path from markdown file location
            dir=$(dirname "$file")
            target="$dir/$link"

            # Handle relative paths like ../module-2/some-file.md
            target=$(realpath --relative-to="$dir" "$target" 2>/dev/null) || continue

            # Check if target exists (resolve to actual file)
            if [[ "$link" == *.md ]]; then
                # If it's a .md link, check for the file
                if [[ ! -f "$target" ]] && [[ ! -f "${target%.md}.md" ]]; then
                    echo "❌ Broken link in $file -> $link"
                    ((BROKEN_LINKS_FOUND++))
                fi
            else
                # For non-md links, check if file exists
                if [[ ! -f "$target" ]]; then
                    echo "❌ Broken link in $file -> $link"
                    ((BROKEN_LINKS_FOUND++))
                fi
            fi
        fi
    done <<< "$LINKS"
done

if [ $BROKEN_LINKS_FOUND -eq 0 ]; then
    echo "✅ All links are valid!"
    exit 0
else
    echo "❌ $BROKEN_LINKS_FOUND broken links found!"
    exit 1
fi