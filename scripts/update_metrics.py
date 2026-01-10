#!/usr/bin/env python3
"""Update metrics for VC dashboard."""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """Update metrics from mutation run."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-number", type=int, required=True)
    parser.add_argument("--results", type=str, required=True)
    args = parser.parse_args()

    logger.info(f"Updating metrics for run {args.run_number}")

    # Read mutation results
    mutations = []
    with open(args.results) as f:
        for line in f:
            if line.strip():
                mutations.append(json.loads(line))

    # Calculate metrics
    total = len(mutations)
    successful = sum(1 for m in mutations if m.get("success"))

    metrics = {
        "run_number": args.run_number,
        "timestamp": datetime.utcnow().isoformat(),
        "total_mutations": total,
        "successful_mutations": successful,
        "success_rate": successful / total if total > 0 else 0,
    }

    # Save metrics
    metrics_file = Path("metrics") / f"run_{args.run_number}.json"
    metrics_file.parent.mkdir(exist_ok=True)

    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Metrics saved to {metrics_file}")


if __name__ == "__main__":
    main()
