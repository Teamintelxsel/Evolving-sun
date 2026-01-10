#!/usr/bin/env python3
"""Run evolution cycle for KEGG mutation engine."""

import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.mutator import KEGGMutator
from kegg_integration.pathway_fetcher import KEGGPathwayFetcher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for evolution script."""
    parser = argparse.ArgumentParser(description='Run KEGG mutation evolution')
    parser.add_argument(
        '--generations',
        type=int,
        default=10,
        help='Number of generations to evolve'
    )
    parser.add_argument(
        '--pathway-ids',
        nargs='+',
        default=['ko01100'],
        help='KEGG pathway IDs to use'
    )
    parser.add_argument(
        '--target-mutations',
        type=int,
        default=10,
        help='Target mutations per generation'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='mutations.jsonl',
        help='Output file for mutation logs'
    )

    args = parser.parse_args()

    logger.info("=== Starting Evolution Run ===")
    logger.info(f"Generations: {args.generations}")
    logger.info(f"Pathways: {args.pathway_ids}")
    logger.info(f"Target mutations/gen: {args.target_mutations}")
    logger.info(f"Output: {args.output}")

    # Initialize mutation engine
    fetcher = KEGGPathwayFetcher()
    mutator = KEGGMutator(fetcher, mutation_log_path=args.output)

    # Run evolution
    results = mutator.evolve(
        generations=args.generations,
        pathway_ids=args.pathway_ids,
        target_mutations_per_gen=args.target_mutations
    )

    # Print summary
    logger.info("\n=== Evolution Summary ===")
    logger.info(f"Total mutations: {results['total_mutations']}")
    logger.info(f"Successful: {results['successful_mutations']}")
    logger.info(f"Failed: {results['failed_mutations']}")
    logger.info(f"Success rate: {results['success_rate']:.2%}")
    logger.info(f"Avg fitness improvement: {results['avg_fitness_improvement']:.4f}")

    # Save final state
    state_file = args.output.replace('.jsonl', '_state.json')
    mutator.save_state(state_file)
    logger.info(f"State saved to: {state_file}")


if __name__ == '__main__':
    main()
