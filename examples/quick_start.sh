#!/bin/bash
# Quick Start Script for Benchmark System
# 
# This script demonstrates how to run the benchmark system in different modes

set -e  # Exit on error

echo "=================================================="
echo "Evolving-sun Benchmark System - Quick Start"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Check if in correct directory
if [ ! -f "scripts/meta_optimization_500.py" ]; then
    echo "Error: Please run this script from the repository root"
    exit 1
fi

# Install dependencies (if needed)
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt || echo "Note: Some dependencies may not be available"

echo ""
echo "=================================================="
echo "Running Quick Tests"
echo "=================================================="

# 1. Run verification on existing benchmarks
echo ""
echo "[1/4] Verifying existing benchmark results..."
python3 scripts/verify_benchmarks.py logs/benchmarks/ || true

# 2. Run a quick latency benchmark
echo ""
echo "[2/4] Running latency benchmark (50 requests)..."
python3 scripts/latency_benchmark_real.py \
    --mode simulation \
    --requests 50 \
    --workers 5

# 3. Run meta-optimization in dry-run mode (10 iterations)
echo ""
echo "[3/4] Running meta-optimization (dry-run, 10 iterations)..."
python3 scripts/meta_optimization_500.py --dry-run

# 4. Verify the new results
echo ""
echo "[4/4] Verifying newly generated results..."
LATEST_FILE=$(ls -t logs/benchmarks/meta_opt_*.json 2>/dev/null | head -1)
if [ -n "$LATEST_FILE" ]; then
    python3 scripts/verify_benchmarks.py "$LATEST_FILE"
else
    echo "No meta-optimization results found"
fi

echo ""
echo "=================================================="
echo "Quick Start Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Run full 500-iteration optimization:"
echo "     python3 scripts/meta_optimization_500.py"
echo ""
echo "  2. Start the dashboard:"
echo "     python3 dashboard/app.py"
echo ""
echo "  3. Run distributed execution (requires Ray):"
echo "     python3 scripts/distributed_executor.py"
echo ""
echo "Results are saved in: logs/benchmarks/"
echo "Checkpoints are saved in: checkpoints/"
echo ""
