#!/usr/bin/env python3
"""Analyze mutation results and determine if improvements warrant a PR."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Analyze mutation results."""
    parser = argparse.ArgumentParser(description='Analyze mutation results')
    parser.add_argument('--input', type=str, required=True, help='Input JSONL file')
    parser.add_argument(
        '--threshold',
        type=float,
        default=0.005,
        help='Minimum fitness improvement threshold'
    )

    args = parser.parse_args()

    logger.info(f"Analyzing mutations from: {args.input}")

    # Read mutation results
    mutations = []
    with open(args.input) as f:
        for line in f:
            if line.strip():
                mutations.append(json.loads(line))

    if not mutations:
        logger.warning("No mutations found")
        print("::set-output name=has_improvements::false")
        return

    # Calculate statistics
    total = len(mutations)
    successful = sum(1 for m in mutations if m.get('success'))
    total_fitness_delta = sum(m.get('fitness_delta', 0) for m in mutations)
    avg_fitness_delta = total_fitness_delta / total if total > 0 else 0

    logger.info(f"Total mutations: {total}")
    logger.info(f"Successful: {successful}")
    logger.info(f"Success rate: {successful/total:.2%}")
    logger.info(f"Avg fitness delta: {avg_fitness_delta:.6f}")

    # Determine if improvements are significant
    has_improvements = avg_fitness_delta > args.threshold

    # Find best mutation
    best_mutation = max(mutations, key=lambda m: m.get('fitness_delta', 0))

    # Create summary
    mutation_summary = f"""
| Metric | Value |
|--------|-------|
| Total Mutations | {total} |
| Successful | {successful} |
| Success Rate | {successful/total:.1%} |
| Avg Fitness Δ | {avg_fitness_delta:.6f} |
| Best Mutation | {best_mutation.get('mutation_id')} |
| Best Fitness Δ | {best_mutation.get('fitness_delta', 0):.6f} |
"""

    # Output for GitHub Actions
    print(f"::set-output name=has_improvements::{str(has_improvements).lower()}")
    print(f"::set-output name=total_mutations::{total}")
    print(f"::set-output name=successful_mutations::{successful}")
    print(f"::set-output name=fitness_delta::{avg_fitness_delta:.6f}")
    print(f"::set-output name=best_mutation_id::{best_mutation.get('mutation_id')}")
    print(f"::set-output name=mutation_summary::{mutation_summary}")
    print(f"::set-output name=timestamp::{datetime.utcnow().isoformat()}")

    # Save analysis
    analysis = {
        'timestamp': datetime.utcnow().isoformat(),
        'total_mutations': total,
        'successful_mutations': successful,
        'success_rate': successful / total,
        'avg_fitness_delta': avg_fitness_delta,
        'has_improvements': has_improvements,
        'threshold': args.threshold,
        'best_mutation': best_mutation,
    }

    with open('mutation_analysis.json', 'w') as f:
        json.dump(analysis, f, indent=2)

    logger.info(f"Analysis complete. Has improvements: {has_improvements}")


if __name__ == '__main__':
    main()
