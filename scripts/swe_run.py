#!/usr/bin/env python3
"""
SWE-Bench benchmark harness runner.

This script shells to the vendor/SWE-bench/scripts/run_evaluation.py
and processes results with watermarked logging.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def run_swe_bench(dataset: str, image: str, num_workers: int, max_tasks: int) -> dict:
    """
    Run SWE-Bench evaluation with specified parameters.
    
    Args:
        dataset: Dataset split/config (e.g., "princeton-nlp/SWE-bench_Verified")
        image: Docker image built per SWE-Bench specifications
        num_workers: Number of parallel workers (1-2 recommended for CI)
        max_tasks: Maximum number of tasks to run (cap for CI)
    
    Returns:
        Dictionary containing benchmark results
    """
    swe_bench_script = Path(__file__).parent.parent / "vendor" / "SWE-bench" / "scripts" / "run_evaluation.py"
    
    if not swe_bench_script.exists():
        print(f"ERROR: SWE-Bench script not found at {swe_bench_script}")
        print("Please ensure the SWE-bench submodule is initialized:")
        print("  git submodule update --init --recursive")
        return {
            "error": "SWE-bench submodule not initialized",
            "status": "failed"
        }
    
    # Build command to shell to SWE-Bench
    cmd = [
        sys.executable,
        str(swe_bench_script),
        "--dataset", dataset,
        "--image", image,
        "--num_workers", str(num_workers),
        "--max_tasks", str(max_tasks)
    ]
    
    print(f"Running SWE-Bench with command: {' '.join(cmd)}")
    
    try:
        # Run the evaluation
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        # Parse results
        results = {
            "dataset": dataset,
            "image": image,
            "num_workers": num_workers,
            "max_tasks": max_tasks,
            "returncode": result.returncode,
            "status": "success" if result.returncode == 0 else "failed",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        # Try to extract metrics from output if available
        # SWE-Bench typically outputs results to a predictions directory
        # We'll look for those files and incorporate them
        
        return results
        
    except subprocess.TimeoutExpired:
        return {
            "dataset": dataset,
            "error": "Execution timeout (1 hour)",
            "status": "timeout"
        }
    except Exception as e:
        return {
            "dataset": dataset,
            "error": str(e),
            "status": "error"
        }


def main():
    """Main entry point for SWE-Bench harness."""
    parser = argparse.ArgumentParser(
        description="Run SWE-Bench evaluation with watermarked logging"
    )
    parser.add_argument(
        "--dataset",
        default="princeton-nlp/SWE-bench_Verified",
        help="Dataset split/config to use (default: Verified split)"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Docker image built per SWE-Bench specifications"
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=1,
        choices=[1, 2],
        help="Number of parallel workers (1-2, default: 1)"
    )
    parser.add_argument(
        "--max_tasks",
        type=int,
        default=10,
        help="Maximum number of tasks to run (cap for CI, default: 10)"
    )
    parser.add_argument(
        "--output",
        default="logs/benchmarks/swe_results.json",
        help="Output path for results (default: logs/benchmarks/swe_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run benchmark
    print("=" * 60)
    print("SWE-Bench Benchmark Harness")
    print("=" * 60)
    results = run_swe_bench(
        dataset=args.dataset,
        image=args.image,
        num_workers=args.num_workers,
        max_tasks=args.max_tasks
    )
    
    # Write watermarked results
    watermark_log(results, args.output)
    
    print("=" * 60)
    print(f"Status: {results.get('status', 'unknown')}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if results.get("status") == "success" else 1)


if __name__ == "__main__":
    main()
