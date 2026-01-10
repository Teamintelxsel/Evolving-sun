#!/usr/bin/env python3
"""
GPQA Benchmark Runner

This script provides integration with GPQA (Graduate-Level Google-Proof Q&A)
via HuggingFace datasets, with baseline tallying and watermarked logging.

Usage:
    python scripts/gpqa_run.py [--limit <n>] [--split <split>]
"""

import argparse
import hashlib
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


def calculate_dataset_hash(dataset_info):
    """
    Calculate a hash of the dataset version for provenance.
    
    Args:
        dataset_info: Dataset information dictionary
    
    Returns:
        str: Hexadecimal hash of dataset info
    """
    info_str = json.dumps(dataset_info, sort_keys=True)
    return hashlib.sha256(info_str.encode('utf-8')).hexdigest()[:16]


def run_gpqa_baseline(args):
    """
    Run GPQA baseline evaluation (tally only, no model inference).
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        dict: Results dictionary with baseline tallies
    """
    print(f"Loading GPQA dataset: Idavidrein/gpqa, split={args.split}")
    
    try:
        # Try to import datasets
        try:
            from datasets import load_dataset
            has_datasets = True
        except ImportError:
            has_datasets = False
            print("WARNING: 'datasets' library not installed. Running in simulation mode.")
        
        if has_datasets:
            try:
                # Load the dataset
                dataset = load_dataset("Idavidrein/gpqa", split=args.split)
                
                # Apply limit if specified
                if args.limit and args.limit < len(dataset):
                    dataset = dataset.select(range(args.limit))
                
                # Baseline tally - count questions by category/difficulty if available
                total_questions = len(dataset)
                
                # Get dataset info for provenance
                dataset_info = {
                    "name": "Idavidrein/gpqa",
                    "split": args.split,
                    "total_size": len(dataset),
                    "features": list(dataset.features.keys()) if hasattr(dataset, 'features') else []
                }
                
                dataset_hash = calculate_dataset_hash(dataset_info)
                
                # Baseline results (no model inference yet)
                results = {
                    "benchmark": "gpqa",
                    "dataset": "Idavidrein/gpqa",
                    "split": args.split,
                    "limit": args.limit,
                    "total_questions": total_questions,
                    "baseline_tally": {
                        "questions_loaded": total_questions,
                        "analysis": "Baseline load - no model inference performed"
                    },
                    "dataset_hash": dataset_hash,
                    "status": "completed"
                }
                
                print(f"✓ Loaded {total_questions} questions from GPQA dataset")
                
            except Exception as e:
                print(f"ERROR loading dataset: {e}")
                # Fall back to simulation
                has_datasets = False
        
        if not has_datasets:
            # Simulation mode
            total_questions = min(args.limit if args.limit else 500, 500)
            dataset_info = {
                "name": "Idavidrein/gpqa",
                "split": args.split,
                "simulated": True
            }
            dataset_hash = calculate_dataset_hash(dataset_info)
            
            results = {
                "benchmark": "gpqa",
                "dataset": "Idavidrein/gpqa",
                "split": args.split,
                "limit": args.limit,
                "total_questions": total_questions,
                "baseline_tally": {
                    "questions_loaded": total_questions,
                    "analysis": "SIMULATED - Install 'datasets' library for real run"
                },
                "dataset_hash": dataset_hash,
                "status": "simulated",
                "note": "Install 'datasets' library and run again for real results"
            }
            
            print(f"✓ Simulated load of {total_questions} questions")
    
    except Exception as e:
        print(f"ERROR: {e}")
        return None
    
    return results


def main():
    """Main entry point for GPQA runner."""
    parser = argparse.ArgumentParser(
        description="Run GPQA baseline evaluation with provenance tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--split",
        type=str,
        default="diamond",
        help="Dataset split to use (default: diamond)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=500,
        help="Limit number of questions to process (default: 500)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: logs/benchmarks/gpqa_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run the benchmark
    results = run_gpqa_baseline(args)
    
    if results is None:
        print("ERROR: Benchmark run failed")
        return 1
    
    # Capture provenance
    provenance = {
        "commit_sha": get_git_commit_sha(),
        "dataset": "Idavidrein/gpqa",
        "split": args.split,
        "limit": args.limit,
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0.0",
        "dataset_hash": results.get("dataset_hash", "unknown")
    }
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        repo_root = get_repo_root()
        output_path = repo_root / "logs" / "benchmarks" / "gpqa_results.json"
    
    # Write watermarked log
    try:
        # Import watermark_log from utils
        sys.path.insert(0, str(get_repo_root() / "src"))
        from utils.secure_logging import watermark_log
        
        success = watermark_log(str(output_path), results, provenance)
        
        if success:
            print(f"\n✓ Results saved to: {output_path}")
            print(f"  Commit SHA: {provenance['commit_sha']}")
            print(f"  Dataset: {provenance['dataset']}")
            print(f"  Split: {provenance['split']}")
            print(f"  Dataset Hash: {provenance['dataset_hash']}")
        else:
            print(f"\n✗ Failed to save results to: {output_path}")
            return 1
    
    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
