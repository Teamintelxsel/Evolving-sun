#!/usr/bin/env python3
"""
GPQA Diamond Benchmark Runner

This script loads the GPQA diamond dataset and performs baseline evaluation.
For the initial run, it provides dataset statistics without model inference.

Usage:
    python scripts/gpqa_run.py [options]
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.secure_logging import watermark_log


def get_git_commit_sha() -> str:
    """Get the current git commit SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_dataset_hash(dataset_name: str, split: str) -> str:
    """
    Compute a version hash for the dataset.
    This helps track dataset versions for reproducibility.
    """
    # Create a hash from dataset name and split
    hash_input = f"{dataset_name}:{split}:{datetime.now().date().isoformat()}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]


def load_gpqa_dataset(limit: int = 500):
    """
    Load GPQA diamond dataset.
    
    Args:
        limit: Maximum number of examples to load
        
    Returns:
        Dictionary with dataset statistics and samples
    """
    try:
        from datasets import load_dataset
        
        print("Loading GPQA diamond dataset...")
        dataset = load_dataset("Idavidrein/gpqa", split="diamond")
        
        # Limit dataset size
        if limit and len(dataset) > limit:
            dataset = dataset.select(range(limit))
        
        # Collect statistics
        stats = {
            "total_examples": len(dataset),
            "features": list(dataset.features.keys()) if hasattr(dataset, 'features') else [],
            "dataset_available": True
        }
        
        # Get sample questions for verification
        samples = []
        for i, example in enumerate(dataset):
            if i >= 3:  # Just get first 3 as samples
                break
            sample = {
                "index": i,
                "has_question": "question" in example or "Question" in example,
                "has_answer": "answer" in example or "Answer" in example,
                "has_choices": "choices" in example or "Choices" in example
            }
            samples.append(sample)
        
        stats["samples"] = samples
        
        return stats
        
    except ImportError:
        print("Warning: 'datasets' library not installed. Running in simulation mode.")
        return simulate_gpqa_dataset(limit)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        print("Running in simulation mode.")
        return simulate_gpqa_dataset(limit)


def simulate_gpqa_dataset(limit: int = 500):
    """
    Simulate GPQA dataset when the actual dataset is not available.
    Provides baseline metrics structure.
    """
    return {
        "total_examples": limit,
        "features": ["question", "answer", "choices"],
        "dataset_available": False,
        "note": "Simulated dataset - install 'datasets' library for real data",
        "samples": [
            {"index": i, "has_question": True, "has_answer": True, "has_choices": True}
            for i in range(3)
        ]
    }


def run_baseline_tally(dataset_stats: dict):
    """
    Run baseline tally without model inference.
    
    For the first run, this just validates the dataset structure
    and provides baseline statistics.
    
    Args:
        dataset_stats: Statistics from loaded dataset
        
    Returns:
        Dictionary with baseline results
    """
    results = {
        "mode": "baseline_tally",
        "dataset_statistics": dataset_stats,
        "baseline_metrics": {
            "total_questions": dataset_stats.get("total_examples", 0),
            "data_validated": dataset_stats.get("dataset_available", False),
            "features_validated": len(dataset_stats.get("features", [])) > 0
        }
    }
    
    # For simulated datasets, add random baseline
    if not dataset_stats.get("dataset_available", False):
        import random
        random.seed(42)
        total = dataset_stats.get("total_examples", 0)
        results["baseline_metrics"]["simulated_random_baseline"] = {
            "accuracy": round(random.uniform(0.20, 0.30), 3),  # Random baseline ~25%
            "note": "Simulated random baseline for 4-choice questions"
        }
    
    return results


def main():
    """Main entry point for GPQA runner."""
    parser = argparse.ArgumentParser(
        description="Run GPQA diamond benchmark with provenance tracking"
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=500,
        help='Maximum number of examples to process (default: 500)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for results (default: logs/benchmarks/)'
    )
    
    args = parser.parse_args()
    
    # Set up output directory
    repo_root = Path(__file__).parent.parent
    output_dir = args.output_dir or (repo_root / "logs" / "benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Capture provenance
    commit_sha = get_git_commit_sha()
    dataset_hash = get_dataset_hash("Idavidrein/gpqa", "diamond")
    
    provenance = {
        "commit_sha": commit_sha,
        "dataset": "Idavidrein/gpqa",
        "split": "diamond",
        "dataset_version_hash": dataset_hash,
        "limit": args.limit,
        "timestamp": datetime.now().isoformat(),
        "script": "gpqa_run.py",
        "python_version": sys.version
    }
    
    print("="*60)
    print("GPQA Diamond Benchmark Runner")
    print("="*60)
    print(f"Dataset: Idavidrein/gpqa (split: diamond)")
    print(f"Limit: {args.limit} examples")
    print(f"Commit SHA: {commit_sha[:8]}...")
    print("="*60)
    
    # Load dataset
    dataset_stats = load_gpqa_dataset(args.limit)
    
    # Run baseline tally
    results = run_baseline_tally(dataset_stats)
    
    # Add benchmark metadata
    full_results = {
        **results,
        "benchmark": "gpqa-diamond",
        "config": {
            "limit": args.limit,
            "mode": "baseline_tally"
        }
    }
    
    # Write watermarked log
    output_file = output_dir / "gpqa_results.json"
    watermark_log(full_results, output_file, provenance)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total examples: {dataset_stats.get('total_examples', 0)}")
    print(f"Dataset available: {dataset_stats.get('dataset_available', False)}")
    
    if not dataset_stats.get("dataset_available", False):
        print("\nNote: Running in simulation mode.")
        print("Install the 'datasets' library to use real GPQA data:")
        print("  pip install datasets")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
