#!/usr/bin/env python3
"""
Unified Benchmark Runner for All Harnesses

This script provides a single entry point to run all benchmark harnesses:
- Legacy benchmarks (performance, accuracy, security)
- SWE-bench Verified
- GPQA Diamond
- KEGG KGML

Usage:
    python scripts/unified_runner.py [options]
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def run_command(cmd: List[str], name: str) -> Dict:
    """
    Run a command and capture results.
    
    Args:
        cmd: Command to run as list of strings
        name: Name of the benchmark for logging
        
    Returns:
        Dictionary with execution results
    """
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout per benchmark
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return {
            "name": name,
            "status": "completed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "duration_seconds": duration,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
    except subprocess.TimeoutExpired:
        return {
            "name": name,
            "status": "timeout",
            "returncode": -1,
            "duration_seconds": 3600,
            "error": "Benchmark timed out after 1 hour"
        }
    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "returncode": -1,
            "error": str(e)
        }


def run_all_benchmarks(args) -> List[Dict]:
    """
    Run all configured benchmarks.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        List of result dictionaries
    """
    results = []
    repo_root = Path(__file__).parent.parent
    
    # Define benchmarks to run
    benchmarks = []
    
    if args.legacy:
        benchmarks.append({
            "name": "Legacy Benchmarks",
            "cmd": [sys.executable, str(repo_root / "scripts" / "run_benchmarks.py"), "--benchmark", "all"]
        })
    
    if args.swe_bench:
        benchmarks.append({
            "name": "SWE-bench Verified",
            "cmd": [
                sys.executable,
                str(repo_root / "scripts" / "swe_run.py"),
                "--max-tasks", str(args.swe_max_tasks),
                "--num-workers", str(args.swe_workers)
            ]
        })
    
    if args.gpqa:
        benchmarks.append({
            "name": "GPQA Diamond",
            "cmd": [
                sys.executable,
                str(repo_root / "scripts" / "gpqa_run.py"),
                "--limit", str(args.gpqa_limit)
            ]
        })
    
    if args.kegg:
        benchmarks.append({
            "name": "KEGG KGML",
            "cmd": [
                sys.executable,
                str(repo_root / "scripts" / "bio_kegg_run.py"),
                "--max-pathways", str(args.kegg_pathways)
            ]
        })
    
    # Run each benchmark
    for benchmark in benchmarks:
        result = run_command(benchmark["cmd"], benchmark["name"])
        results.append(result)
    
    return results


def print_summary(results: List[Dict]):
    """Print a summary of all benchmark results."""
    print("\n" + "="*60)
    print("UNIFIED BENCHMARK SUMMARY")
    print("="*60)
    
    total = len(results)
    completed = sum(1 for r in results if r["status"] == "completed")
    failed = sum(1 for r in results if r["status"] == "failed")
    errors = sum(1 for r in results if r["status"] in ["timeout", "error"])
    
    print(f"\nTotal Benchmarks: {total}")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Errors/Timeouts: {errors}")
    print()
    
    for result in results:
        status_symbol = "✓" if result["status"] == "completed" else "✗"
        duration = result.get("duration_seconds", 0)
        print(f"{status_symbol} {result['name']}: {result['status']} ({duration:.1f}s)")
        if "error" in result:
            print(f"  Error: {result['error']}")
    
    print("="*60)


def save_summary(results: List[Dict], output_dir: Path):
    """Save a summary of all results to a JSON file."""
    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_benchmarks": len(results),
        "completed": sum(1 for r in results if r["status"] == "completed"),
        "failed": sum(1 for r in results if r["status"] == "failed"),
        "errors": sum(1 for r in results if r["status"] in ["timeout", "error"]),
        "results": results
    }
    
    output_file = output_dir / "unified_summary.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nUnified summary saved to: {output_file}")


def main():
    """Main entry point for unified runner."""
    parser = argparse.ArgumentParser(
        description="Run all benchmark harnesses with a unified interface",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Benchmark selection
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all benchmarks (default if no specific benchmarks selected)'
    )
    parser.add_argument(
        '--legacy',
        action='store_true',
        help='Run legacy benchmarks (performance, accuracy, security)'
    )
    parser.add_argument(
        '--swe-bench',
        action='store_true',
        help='Run SWE-bench Verified'
    )
    parser.add_argument(
        '--gpqa',
        action='store_true',
        help='Run GPQA Diamond'
    )
    parser.add_argument(
        '--kegg',
        action='store_true',
        help='Run KEGG KGML'
    )
    
    # SWE-bench options
    parser.add_argument(
        '--swe-max-tasks',
        type=int,
        default=10,
        help='Maximum tasks for SWE-bench (default: 10)'
    )
    parser.add_argument(
        '--swe-workers',
        type=int,
        default=1,
        help='Number of workers for SWE-bench (default: 1)'
    )
    
    # GPQA options
    parser.add_argument(
        '--gpqa-limit',
        type=int,
        default=500,
        help='Example limit for GPQA (default: 500)'
    )
    
    # KEGG options
    parser.add_argument(
        '--kegg-pathways',
        type=int,
        default=10,
        help='Maximum pathways for KEGG (default: 10)'
    )
    
    # Output options
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for results (default: logs/benchmarks/)'
    )
    
    args = parser.parse_args()
    
    # If --all or no specific benchmarks selected, enable all
    if args.all or not (args.legacy or args.swe_bench or args.gpqa or args.kegg):
        args.legacy = True
        args.swe_bench = True
        args.gpqa = True
        args.kegg = True
    
    # Set up output directory
    repo_root = Path(__file__).parent.parent
    output_dir = args.output_dir or (repo_root / "logs" / "benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*60)
    print("UNIFIED BENCHMARK RUNNER")
    print("="*60)
    print(f"Output directory: {output_dir}")
    print(f"Benchmarks to run:")
    if args.legacy:
        print("  - Legacy benchmarks")
    if args.swe_bench:
        print(f"  - SWE-bench Verified (max_tasks={args.swe_max_tasks}, workers={args.swe_workers})")
    if args.gpqa:
        print(f"  - GPQA Diamond (limit={args.gpqa_limit})")
    if args.kegg:
        print(f"  - KEGG KGML (pathways={args.kegg_pathways})")
    
    # Run benchmarks
    results = run_all_benchmarks(args)
    
    # Print and save summary
    print_summary(results)
    save_summary(results, output_dir)
    
    # Exit with error if any benchmark failed
    if any(r["status"] != "completed" for r in results):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
