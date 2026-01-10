#!/usr/bin/env python3
"""
Example usage of the Evolving Sun benchmark framework.

This script demonstrates how to use the benchmark harnesses
and interpret results.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def example_watermarked_logging():
    """Demonstrate watermarked logging."""
    print("=" * 60)
    print("Example: Watermarked Logging")
    print("=" * 60)
    
    # Create sample benchmark results
    sample_results = {
        "benchmark": "example",
        "accuracy": 0.85,
        "samples_tested": 100,
        "correct": 85,
        "status": "success"
    }
    
    # Write with watermark
    output_path = "logs/benchmarks/example_results.json"
    watermark_log(sample_results, output_path)
    
    # Read and verify
    with open(output_path, 'r') as f:
        watermarked_data = json.load(f)
    
    print(f"\nWatermark details:")
    print(f"  Timestamp: {watermarked_data['watermark']['timestamp']}")
    print(f"  Content hash: {watermarked_data['watermark']['content_hash']}")
    print(f"  Framework: {watermarked_data['watermark']['framework']}")
    print(f"\nActual data:")
    print(f"  Accuracy: {watermarked_data['data']['accuracy']}")
    print(f"  Status: {watermarked_data['data']['status']}")
    print()


def example_result_parsing():
    """Demonstrate parsing benchmark results."""
    print("=" * 60)
    print("Example: Parsing Results")
    print("=" * 60)
    
    # Check if we have any result files
    results_dir = Path("logs/benchmarks")
    if not results_dir.exists():
        print("No results directory found. Run a benchmark first.")
        return
    
    json_files = list(results_dir.glob("*.json"))
    if not json_files:
        print("No result files found. Run a benchmark first.")
        return
    
    for result_file in json_files:
        print(f"\nParsing: {result_file.name}")
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
            
            # Verify watermark
            if 'watermark' in data:
                print(f"  ✓ Watermark verified")
                print(f"    Timestamp: {data['watermark']['timestamp']}")
            else:
                print(f"  ✗ No watermark found!")
            
            # Display key metrics
            if 'data' in data:
                result_data = data['data']
                status = result_data.get('status', 'unknown')
                print(f"  Status: {status}")
                
                # Display benchmark-specific metrics
                if 'accuracy' in result_data:
                    print(f"  Accuracy: {result_data['accuracy']:.2%}")
                if 'total_pathways' in result_data:
                    print(f"  Pathways: {result_data.get('successful', 0)}/{result_data.get('total_pathways', 0)}")
                
        except Exception as e:
            print(f"  Error parsing: {e}")
    
    print()


def example_benchmark_commands():
    """Display example commands for running benchmarks."""
    print("=" * 60)
    print("Example: Running Benchmarks")
    print("=" * 60)
    
    examples = [
        ("Run GPQA with 50 samples", 
         "python scripts/gpqa_run.py --max_samples 50"),
        
        ("Run KEGG with specific pathways",
         "python scripts/bio_kegg_run.py --pathways hsa00010 hsa00020 hsa00030"),
        
        ("Run SWE-Bench (requires Docker)",
         "python scripts/swe_run.py --image sweagent/swe-agent:latest --max_tasks 10"),
        
        ("Run all benchmarks via unified runner",
         "python scripts/run_benchmarks.py --benchmarks all"),
        
        ("Run specific benchmarks with custom settings",
         "python scripts/run_benchmarks.py --benchmarks gpqa kegg --gpqa-max-samples 100"),
    ]
    
    for i, (description, command) in enumerate(examples, 1):
        print(f"\n{i}. {description}")
        print(f"   $ {command}")
    
    print("\n" + "=" * 60)
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Evolving Sun Benchmark Framework - Examples")
    print("=" * 60 + "\n")
    
    # Example 1: Watermarked logging
    example_watermarked_logging()
    
    # Example 2: Parsing results
    example_result_parsing()
    
    # Example 3: Command examples
    example_benchmark_commands()
    
    print("For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
