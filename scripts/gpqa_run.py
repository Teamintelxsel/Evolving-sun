#!/usr/bin/env python3
"""
GPQA (Graduate-Level Google-Proof Q&A) benchmark harness runner.

This script loads the GPQA dataset from HuggingFace and runs evaluation
with watermarked logging.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def run_gpqa_baseline(split: str = "diamond", max_samples: int = None) -> dict:
    """
    Run GPQA baseline evaluation using provided answer fields.
    
    Args:
        split: Dataset split to use (default: "diamond")
        max_samples: Maximum number of samples to evaluate (None for all)
    
    Returns:
        Dictionary containing benchmark results
    """
    try:
        from datasets import load_dataset
    except ImportError:
        return {
            "error": "datasets library not installed. Run: pip install datasets",
            "status": "failed"
        }
    
    print(f"Loading GPQA dataset (split: {split})...")
    
    try:
        # Load dataset from HuggingFace
        dataset = load_dataset("Idavidrein/gpqa", split=split)
        
        if max_samples:
            dataset = dataset.select(range(min(max_samples, len(dataset))))
        
        print(f"Loaded {len(dataset)} samples")
        
        # Baseline evaluation: tally using provided answer fields
        # This is a placeholder - will be replaced with actual model calls later
        correct = 0
        total = 0
        results_detail = []
        
        for idx, item in enumerate(dataset):
            # GPQA format typically has: question, correct_answer, and distractor answers
            # For baseline, we'll just verify the data structure
            question = item.get("Question", "")
            correct_answer = item.get("Correct Answer", "")
            
            # Baseline: assume random performance (25% for 4-choice)
            # This is a placeholder for actual model evaluation
            is_correct = (idx % 4 == 0)  # Simulated 25% accuracy
            
            if is_correct:
                correct += 1
            total += 1
            
            results_detail.append({
                "index": idx,
                "question_preview": question[:100] + "..." if len(question) > 100 else question,
                "correct": is_correct
            })
        
        accuracy = correct / total if total > 0 else 0.0
        
        results = {
            "dataset": "Idavidrein/gpqa",
            "split": split,
            "total_samples": total,
            "correct": correct,
            "accuracy": accuracy,
            "status": "success",
            "note": "Baseline evaluation using simulated responses. Replace with actual model calls.",
            "samples": results_detail[:10]  # Include first 10 for inspection
        }
        
        print(f"Accuracy: {accuracy:.2%} ({correct}/{total})")
        
        return results
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


def main():
    """Main entry point for GPQA harness."""
    parser = argparse.ArgumentParser(
        description="Run GPQA evaluation with watermarked logging"
    )
    parser.add_argument(
        "--split",
        default="diamond",
        choices=["diamond", "main", "extended"],
        help="Dataset split to use (default: diamond)"
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="Maximum number of samples to evaluate (default: all)"
    )
    parser.add_argument(
        "--output",
        default="logs/benchmarks/gpqa_results.json",
        help="Output path for results (default: logs/benchmarks/gpqa_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run benchmark
    print("=" * 60)
    print("GPQA Benchmark Harness")
    print("=" * 60)
    results = run_gpqa_baseline(
        split=args.split,
        max_samples=args.max_samples
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
