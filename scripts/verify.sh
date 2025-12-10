#!/bin/bash
# Comprehensive validation script for Physical AI & Humanoid Robotics Textbook
# Runs all validation checks to ensure quality requirements are met

echo "Running comprehensive validation..."

# Make sure scripts have execute permissions
chmod +x scripts/*.sh 2>/dev/null || true

# Run word count validation
echo "1/4 - Checking word counts..."
python3 scripts/check-wordcount.py
WORDCOUNT_RESULT=$?

# Run link validation
echo "2/4 - Checking links..."
bash scripts/link-check.sh
LINK_RESULT=$?

# Check diagram count
echo "3/4 - Checking diagram count..."
DIAGRAM_COUNT=$(find diagrams -name "*.svg" -o -name "*.png" | wc -l)
echo "Found $DIAGRAM_COUNT diagrams"
if [ $DIAGRAM_COUNT -ge 12 ]; then
    echo "✅ Diagram count OK (found $DIAGRAM_COUNT, need at least 12)"
    DIAGRAM_RESULT=0
else
    echo "❌ Diagram count insufficient (found $DIAGRAM_COUNT, need at least 12)"
    DIAGRAM_RESULT=1
fi

# Check example count
echo "4/4 - Checking example count..."
EXAMPLE_COUNT=$(find code -name "*.py" | wc -l)
echo "Found $EXAMPLE_COUNT code examples"
if [ $EXAMPLE_COUNT -ge 20 ]; then
    echo "✅ Example count OK (found $EXAMPLE_COUNT, need at least 20)"
    EXAMPLE_RESULT=0
else
    echo "❌ Example count insufficient (found $EXAMPLE_COUNT, need at least 20)"
    EXAMPLE_RESULT=1
fi

# Summary
echo ""
echo "Validation Results:"
echo "Word count check: $([ $WORDCOUNT_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Link validation: $([ $LINK_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Diagram count: $([ $DIAGRAM_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Example count: $([ $EXAMPLE_RESULT -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"

# Exit with error if any check failed
if [ $WORDCOUNT_RESULT -ne 0 ] || [ $LINK_RESULT -ne 0 ] || [ $DIAGRAM_RESULT -ne 0 ] || [ $EXAMPLE_RESULT -ne 0 ]; then
    echo "❌ Some validations failed!"
    exit 1
else
    echo "✅ All validations passed!"
    exit 0
fi