#!/bin/bash

# Test script for module-2 code examples
# Verifies that all examples run successfully in Ubuntu 22.04 environment

set -e  # Exit on any error

echo "Testing Module 2 Code Examples"
echo "==============================="

# Define the Python interpreter to use
PYTHON="${PYTHON:-python3}"

# Check if Python is available
if ! command -v "$PYTHON" &> /dev/null; then
    echo "Error: Python interpreter '$PYTHON' not found"
    exit 1
fi

echo "Using Python interpreter: $($PYTHON --version)"
echo

# Test each example in module-2
EXAMPLES=(
    "example-1-physics-scenario.py"
    "example-2-human-robot-interaction.py"
    "example-3-contact-modeling.py"
    "example-4-force-analysis.py"
    "example-5-friction-modeling.py"
)

SUCCESS_COUNT=0
TOTAL_COUNT=${#EXAMPLES[@]}

for example in "${EXAMPLES[@]}"; do
    echo "Testing $example..."

    # Check if the file exists
    if [[ ! -f "$example" ]]; then
        echo "Error: File $example does not exist"
        continue
    fi

    # Run the example with a timeout to prevent hanging
    if timeout 30s "$PYTHON" "$example" > "/tmp/test_output_${example%.*}.txt" 2>&1; then
        echo "✓ $example executed successfully"
        ((SUCCESS_COUNT++))
    else
        echo "✗ $example failed to execute"
        echo "Output:"
        cat "/tmp/test_output_${example%.*}.txt"
        echo
    fi

    # Clean up temporary output file
    rm -f "/tmp/test_output_${example%.*}.txt"
done

echo
echo "Module 2 Test Summary:"
echo "======================"
echo "Total examples: $TOTAL_COUNT"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $((TOTAL_COUNT - SUCCESS_COUNT))"

if [[ $SUCCESS_COUNT -eq $TOTAL_COUNT ]]; then
    echo "✓ All module 2 examples passed!"
    exit 0
else
    echo "✗ Some examples failed"
    exit 1
fi