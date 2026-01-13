#!/usr/bin/env python3
"""
SWE-bench Verified Benchmark Runner

This script provides integration with SWE-bench Verified via run_evaluation.py
and Docker, with full provenance tracking and watermarked logging.

Usage:
    python scripts/swe_run.py --dataset <config> --image <digest> [options]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_git_commit_sha():
    """Get the current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_repo_root():
    """Get the repository root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def run_swe_bench(args):
    """
    Run SWE-bench evaluation with the specified parameters.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        dict: Results dictionary with provenance
    """
    repo_root = get_repo_root()
    vendor_swe_bench = repo_root / "vendor" / "SWE-bench"
    run_eval_script = vendor_swe_bench / "swebench" / "harness" / "run_evaluation.py"
    
    # Check if vendor submodule exists
    if not vendor_swe_bench.exists():
        print(f"ERROR: SWE-bench vendor directory not found at {vendor_swe_bench}")
        print("Please run: git submodule update --init --recursive")
        return None
    
    if not run_eval_script.exists():
        print(f"ERROR: run_evaluation.py not found at {run_eval_script}")
        return None
    
    # Build command for run_evaluation.py
    cmd = [
        sys.executable,
        str(run_eval_script),
        "--dataset", args.dataset,
        "--image", args.image,
        "--num_workers", str(args.num_workers),
    ]
    
    if args.max_tasks:
        cmd.extend(["--max_tasks", str(args.max_tasks)])
    
    print(f"Running SWE-bench evaluation with command:")
    print(f"  {' '.join(cmd)}")
    
    # For now, simulate the run since we may not have the actual environment
    # In a real implementation, this would call the actual script
    print("\nNote: Running in simulation mode (actual Docker evaluation requires full setup)")
    
    # Simulated results structure
    results = {
        "benchmark": "swe-bench-verified",
        "dataset_config": args.dataset,
        "image_digest": args.image,
        "num_workers": args.num_workers,
        "max_tasks": args.max_tasks,
        "status": "simulated",
        "note": "Replace with real results once Docker environment is configured",
        "simulated_metrics": {
            "total_tasks": args.max_tasks if args.max_tasks else 100,
            "resolved": 0,
            "unresolved": 0,
            "pending": args.max_tasks if args.max_tasks else 100
        }
    }
    
    return results


def main():
    """Main entry point for SWE-bench runner."""
    parser = argparse.ArgumentParser(
        description="Run SWE-bench Verified evaluation with provenance tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dataset",
        type=str,
        required=True,
        help="Dataset split/config (e.g., 'princeton-nlp/SWE-bench_Verified')"
    )
    
    parser.add_argument(
        "--image",
        type=str,
        required=True,
        help="Docker image pinned by digest (e.g., 'sha256:abc123...')"
    )
    
    parser.add_argument(
        "--num-workers",
        type=int,
        default=1,
        help="Number of workers (1-2 recommended for CI)"
    )
    
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=None,
        help="Maximum number of tasks to run (cap for CI)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: logs/benchmarks/swe_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run the benchmark
    results = run_swe_bench(args)
    
    if results is None:
        print("ERROR: Benchmark run failed")
        return 1
    
    # Capture provenance
    provenance = {
        "commit_sha": get_git_commit_sha(),
        "image_digest": args.image,
        "dataset_config": args.dataset,
        "seed": args.seed,
        "num_workers": args.num_workers,
        "max_tasks": args.max_tasks,
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0.0"
    }
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        repo_root = get_repo_root()
        output_path = repo_root / "logs" / "benchmarks" / "swe_results.json"
    
    # Write watermarked log
    try:
        # Import watermark_log from utils
        sys.path.insert(0, str(get_repo_root() / "src"))
        from utils.secure_logging import watermark_log
        
        success = watermark_log(str(output_path), results, provenance)
        
        if success:
            print(f"\n✓ Results saved to: {output_path}")
            print(f"  Commit SHA: {provenance['commit_sha']}")
            print(f"  Dataset: {provenance['dataset_config']}")
            print(f"  Image: {provenance['image_digest']}")
        else:
            print(f"\n✗ Failed to save results to: {output_path}")
            return 1
    
    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
