#!/bin/bash

# Test script for module-1 code examples
# Verifies that all examples run successfully in Ubuntu 22.04 environment

set -e  # Exit on any error

echo "Testing Module 1 Code Examples"
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

# Test each example in module-1
EXAMPLES=(
    "example-1-sensor-loop.py"
    "example-2-balance-logic.py"
    "example-3-object-recognition.py"
    "example-4-digital-twin.py"
    "example-5-embodiment.py"
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
echo "Module 1 Test Summary:"
echo "======================"
echo "Total examples: $TOTAL_COUNT"
echo "Successful: $SUCCESS_COUNT"
echo "Failed: $((TOTAL_COUNT - SUCCESS_COUNT))"

if [[ $SUCCESS_COUNT -eq $TOTAL_COUNT ]]; then
    echo "✓ All module 1 examples passed!"
    exit 0
else
    echo "✗ Some examples failed"
    exit 1
fi