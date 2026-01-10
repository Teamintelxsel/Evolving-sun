#!/usr/bin/env python3
"""
Unified benchmark runner for all harnesses.

This script orchestrates execution of SWE-Bench, GPQA, and KEGG benchmarks
with consolidated reporting and result archiving.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def run_benchmark(script_name: str, args: List[str]) -> Dict:
    """
    Run a benchmark script and capture results.
    
    Args:
        script_name: Name of the benchmark script to run
        args: Additional arguments to pass to the script
    
    Returns:
        Dictionary containing execution results
    """
    script_path = Path(__file__).parent / script_name
    cmd = [sys.executable, str(script_path)] + args
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    start_time = datetime.utcnow()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=7200  # 2 hour timeout
        )
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            "script": script_name,
            "returncode": result.returncode,
            "status": "success" if result.returncode == 0 else "failed",
            "duration_seconds": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "start_time": start_time.isoformat() + 'Z',
            "end_time": end_time.isoformat() + 'Z'
        }
        
    except subprocess.TimeoutExpired:
        return {
            "script": script_name,
            "status": "timeout",
            "error": "Execution timeout (2 hours)"
        }
    except Exception as e:
        return {
            "script": script_name,
            "status": "error",
            "error": str(e)
        }


def main():
    """Main entry point for unified benchmark runner."""
    parser = argparse.ArgumentParser(
        description="Unified benchmark runner for SWE-Bench, GPQA, and KEGG"
    )
    parser.add_argument(
        "--benchmarks",
        nargs="+",
        choices=["swe", "gpqa", "kegg", "all"],
        default=["all"],
        help="Benchmarks to run (default: all)"
    )
    parser.add_argument(
        "--output-dir",
        default="logs/benchmarks",
        help="Output directory for results (default: logs/benchmarks)"
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Archive results with timestamp"
    )
    
    # SWE-Bench specific args
    parser.add_argument(
        "--swe-image",
        help="Docker image for SWE-Bench (required if running swe)"
    )
    parser.add_argument(
        "--swe-max-tasks",
        type=int,
        default=5,
        help="Max tasks for SWE-Bench (default: 5 for CI)"
    )
    
    # GPQA specific args
    parser.add_argument(
        "--gpqa-max-samples",
        type=int,
        default=50,
        help="Max samples for GPQA (default: 50)"
    )
    
    # KEGG specific args
    parser.add_argument(
        "--kegg-pathways",
        nargs="+",
        default=["hsa00010", "hsa00020"],
        help="KEGG pathway IDs (default: glycolysis, TCA)"
    )
    
    args = parser.parse_args()
    
    # Determine which benchmarks to run
    benchmarks_to_run = []
    if "all" in args.benchmarks:
        benchmarks_to_run = ["gpqa", "kegg"]  # SWE requires image
        if args.swe_image:
            benchmarks_to_run.insert(0, "swe")
    else:
        benchmarks_to_run = args.benchmarks
    
    print("=" * 60)
    print("Unified Benchmark Runner")
    print("=" * 60)
    print(f"Running benchmarks: {', '.join(benchmarks_to_run)}")
    print(f"Output directory: {args.output_dir}")
    print()
    
    # Execute benchmarks
    execution_results = []
    overall_start = datetime.utcnow()
    
    for benchmark in benchmarks_to_run:
        if benchmark == "swe":
            if not args.swe_image:
                print("WARNING: Skipping SWE-Bench (no --swe-image provided)")
                continue
            
            result = run_benchmark(
                "swe_run.py",
                [
                    "--image", args.swe_image,
                    "--max_tasks", str(args.swe_max_tasks),
                    "--output", f"{args.output_dir}/swe_results.json"
                ]
            )
            execution_results.append(result)
            
        elif benchmark == "gpqa":
            result = run_benchmark(
                "gpqa_run.py",
                [
                    "--max_samples", str(args.gpqa_max_samples),
                    "--output", f"{args.output_dir}/gpqa_results.json"
                ]
            )
            execution_results.append(result)
            
        elif benchmark == "kegg":
            result = run_benchmark(
                "bio_kegg_run.py",
                [
                    "--pathways"] + args.kegg_pathways + [
                    "--output", f"{args.output_dir}/kegg_results.json"
                ]
            )
            execution_results.append(result)
    
    overall_end = datetime.utcnow()
    overall_duration = (overall_end - overall_start).total_seconds()
    
    # Compile summary
    summary = {
        "total_benchmarks": len(execution_results),
        "successful": sum(1 for r in execution_results if r.get("status") == "success"),
        "failed": sum(1 for r in execution_results if r.get("status") == "failed"),
        "errors": sum(1 for r in execution_results if r.get("status") == "error"),
        "overall_duration_seconds": overall_duration,
        "start_time": overall_start.isoformat() + 'Z',
        "end_time": overall_end.isoformat() + 'Z',
        "executions": execution_results
    }
    
    # Write summary
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if args.archive:
        summary_path = f"{args.output_dir}/summary_{timestamp}.json"
    else:
        summary_path = f"{args.output_dir}/summary.json"
    
    watermark_log(summary, summary_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("Benchmark Execution Summary")
    print("=" * 60)
    print(f"Total benchmarks: {summary['total_benchmarks']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Errors: {summary['errors']}")
    print(f"Duration: {overall_duration:.2f} seconds")
    print(f"Summary written to: {summary_path}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if summary["failed"] == 0 and summary["errors"] == 0 else 1)


if __name__ == "__main__":
    main()
