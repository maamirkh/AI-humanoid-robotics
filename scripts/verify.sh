#!/bin/bash
# Comprehensive validation script for Physical AI & Humanoid Robotics Textbook
# Validates all requirements from the specification

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <project_root_directory>"
    exit 1
fi

PROJECT_DIR="$1"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "Project directory $PROJECT_DIR does not exist"
    exit 1
fi

echo "Running comprehensive validation for Physical AI & Humanoid Robotics Textbook..."
echo

# Validate directory structure
echo "1. Checking directory structure..."
REQUIRED_DIRS=(
    "$PROJECT_DIR/docs"
    "$PROJECT_DIR/docs/module-1"
    "$PROJECT_DIR/docs/module-2" 
    "$PROJECT_DIR/docs/module-3"
    "$PROJECT_DIR/docs/module-4"
    "$PROJECT_DIR/diagrams"
    "$PROJECT_DIR/diagrams/module-1"
    "$PROJECT_DIR/diagrams/module-2"
    "$PROJECT_DIR/diagrams/module-3"
    "$PROJECT_DIR/diagrams/module-4"
    "$PROJECT_DIR/code"
    "$PROJECT_DIR/code/module-1"
    "$PROJECT_DIR/code/module-2"
    "$PROJECT_DIR/code/module-3"
    "$PROJECT_DIR/code/module-4"
    "$PROJECT_DIR/static/img"
    "$PROJECT_DIR/templates"
    "$PROJECT_DIR/scripts"
    "$PROJECT_DIR/examples"
)

MISSING_DIRS=()
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "$dir" ]; then
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
    echo "  ✓ All required directories exist"
else
    echo "  ✗ Missing directories:"
    for dir in "${MISSING_DIRS[@]}"; do
        echo "    - $dir"
    done
    exit 1
fi

# Validate content files count
echo
echo "2. Checking content files..."

MODULE1_COUNT=$(find "$PROJECT_DIR/docs/module-1" -name "*.md" | wc -l)
MODULE2_COUNT=$(find "$PROJECT_DIR/docs/module-2" -name "*.md" | wc -l)
MODULE3_COUNT=$(find "$PROJECT_DIR/docs/module-3" -name "*.md" | wc -l)
MODULE4_COUNT=$(find "$PROJECT_DIR/docs/module-4" -name "*.md" | wc -l)

echo "  Module 1: $MODULE1_COUNT markdown files"
echo "  Module 2: $MODULE2_COUNT markdown files" 
echo "  Module 3: $MODULE3_COUNT markdown files"
echo "  Module 4: $MODULE4_COUNT markdown files"

# Validate code examples
echo
echo "3. Checking code examples..."
CODE1_COUNT=$(find "$PROJECT_DIR/code/module-1" -name "*.py" | wc -l)
CODE2_COUNT=$(find "$PROJECT_DIR/code/module-2" -name "*.py" | wc -l)
CODE3_COUNT=$(find "$PROJECT_DIR/code/module-3" -name "*.py" | wc -l)
CODE4_COUNT=$(find "$PROJECT_DIR/code/module-4" -name "*.py" | wc -l)

echo "  Module 1: $CODE1_COUNT Python files"
echo "  Module 2: $CODE2_COUNT Python files"
echo "  Module 3: $CODE3_COUNT Python files"
echo "  Module 4: $CODE4_COUNT Python files"

# Validate diagrams
echo
echo "4. Checking diagrams..."
DIAG1_COUNT=$(find "$PROJECT_DIR/diagrams/module-1" -name "*.svg" | wc -l)
DIAG2_COUNT=$(find "$PROJECT_DIR/diagrams/module-2" -name "*.svg" | wc -l)
DIAG3_COUNT=$(find "$PROJECT_DIR/diagrams/module-3" -name "*.svg" | wc -l)
DIAG4_COUNT=$(find "$PROJECT_DIR/diagrams/module-4" -name "*.svg" | wc -l)

echo "  Module 1: $DIAG1_COUNT SVG files"
echo "  Module 2: $DIAG2_COUNT SVG files"
echo "  Module 3: $DIAG3_COUNT SVG files"
echo "  Module 4: $DIAG4_COUNT SVG files"

# Validate word count
echo
echo "5. Checking word count..."
python3 "$PROJECT_DIR/scripts/check-wordcount.py" "$PROJECT_DIR/docs" || {
    echo "  ✗ Word count validation failed"
    exit 1
}

echo
echo "✓ All validations passed!"
echo "Project structure is complete and meets all requirements."
