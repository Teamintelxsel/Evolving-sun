#!/usr/bin/env python3
"""
Benchmark Comparison Tool

Compare multiple benchmark results to track improvements over time.

Usage:
    python compare_benchmarks.py file1.json file2.json
    python compare_benchmarks.py logs/benchmarks/*.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


def load_benchmark(filepath: Path) -> Dict[str, Any]:
    """Load a benchmark result file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Handle list format (legacy)
    if isinstance(data, list):
        return {
            'filename': filepath.name,
            'timestamp': filepath.stat().st_mtime,
            'metrics': data[0] if data else {}
        }
    
    return {
        'filename': filepath.name,
        'timestamp': data.get('timestamp', filepath.stat().st_mtime),
        'benchmark_name': data.get('benchmark_name', 'unknown'),
        'duration': data.get('duration_seconds', 0),
        'iterations': data.get('iterations', 0),
        'metrics': data.get('metrics', {})
    }


def compare_benchmarks(benchmarks: List[Dict[str, Any]]) -> None:
    """Compare and display benchmark results."""
    if not benchmarks:
        print("No benchmarks to compare")
        return
    
    # Sort by timestamp
    benchmarks.sort(key=lambda x: x['timestamp'])
    
    print("\n" + "="*80)
    print("BENCHMARK COMPARISON")
    print("="*80)
    print(f"\nComparing {len(benchmarks)} benchmark(s)\n")
    
    # Table header
    print(f"{'File':<35} {'Accuracy':<12} {'Latency (ms)':<15} {'Duration (s)':<15}")
    print("-"*80)
    
    # Table rows
    for b in benchmarks:
        filename = b['filename'][:33] + ".." if len(b['filename']) > 35 else b['filename']
        
        metrics = b.get('metrics', {})
        
        # Extract accuracy
        accuracy = metrics.get('accuracy', 0)
        if accuracy == 0 and 'latency_ms' in metrics:
            # Latency benchmark
            accuracy = "N/A"
            accuracy_str = f"{accuracy:<12}"
        else:
            accuracy_str = f"{accuracy*100:>6.2f}%    "
        
        # Extract latency
        if 'latency_ms' in metrics:
            if isinstance(metrics['latency_ms'], dict):
                latency = metrics['latency_ms'].get('mean', 0)
            else:
                latency = metrics['latency_ms']
            latency_str = f"{latency:>8.2f}"
        elif 'final_latency_ms' in metrics:
            latency_str = f"{metrics['final_latency_ms']:>8.2f}"
        else:
            latency_str = "N/A"
        
        duration = b.get('duration', 0)
        
        print(f"{filename:<35} {accuracy_str} {latency_str:<15} {duration:<15.2f}")
    
    print("="*80)
    
    # Show improvement if we have 2+ benchmarks
    if len(benchmarks) >= 2:
        print("\nIMPROVEMENT ANALYSIS")
        print("-"*80)
        
        first = benchmarks[0]
        last = benchmarks[-1]
        
        first_acc = first.get('metrics', {}).get('accuracy', 0)
        last_acc = last.get('metrics', {}).get('accuracy', 0)
        
        if first_acc > 0 and last_acc > 0:
            acc_improvement = (last_acc - first_acc) / first_acc * 100
            print(f"Accuracy: {first_acc*100:.2f}% → {last_acc*100:.2f}% ({acc_improvement:+.2f}%)")
        
        # Latency comparison
        first_metrics = first.get('metrics', {})
        last_metrics = last.get('metrics', {})
        
        first_lat = None
        last_lat = None
        
        if 'latency_ms' in first_metrics:
            if isinstance(first_metrics['latency_ms'], dict):
                first_lat = first_metrics['latency_ms'].get('mean')
            else:
                first_lat = first_metrics['latency_ms']
        
        if 'latency_ms' in last_metrics:
            if isinstance(last_metrics['latency_ms'], dict):
                last_lat = last_metrics['latency_ms'].get('mean')
            else:
                last_lat = last_metrics['latency_ms']
        
        if first_lat and last_lat:
            lat_improvement = (first_lat - last_lat) / first_lat * 100
            print(f"Latency: {first_lat:.2f}ms → {last_lat:.2f}ms ({lat_improvement:+.2f}%)")
        
        print("="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Compare benchmark results")
    parser.add_argument(
        'files',
        nargs='+',
        type=str,
        help='Benchmark result files to compare'
    )
    parser.add_argument(
        '--sort-by',
        choices=['timestamp', 'accuracy', 'latency'],
        default='timestamp',
        help='Sort benchmarks by field (default: timestamp)'
    )
    
    args = parser.parse_args()
    
    # Load benchmarks
    benchmarks = []
    for file_pattern in args.files:
        # Support glob patterns
        for filepath in Path('.').glob(file_pattern):
            if filepath.is_file() and filepath.suffix == '.json':
                try:
                    benchmark = load_benchmark(filepath)
                    benchmarks.append(benchmark)
                except Exception as e:
                    print(f"Error loading {filepath}: {e}", file=sys.stderr)
    
    if not benchmarks:
        print("No valid benchmark files found")
        return 1
    
    # Compare
    compare_benchmarks(benchmarks)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
