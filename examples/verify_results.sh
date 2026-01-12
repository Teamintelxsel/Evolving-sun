#!/bin/bash
# Verify Benchmark Results Script
#
# This script verifies all benchmark results in a directory

set -e

BENCHMARK_DIR="${1:-logs/benchmarks}"

echo "=================================================="
echo "Benchmark Verification Tool"
echo "=================================================="
echo ""

if [ ! -d "$BENCHMARK_DIR" ]; then
    echo "Error: Directory not found: $BENCHMARK_DIR"
    exit 1
fi

echo "Verifying benchmarks in: $BENCHMARK_DIR"
echo ""

# Run verification
python3 scripts/verify_benchmarks.py "$BENCHMARK_DIR" --output logs/verification_report.json

echo ""
echo "Verification complete!"
echo "Report saved to: logs/verification_report.json"
