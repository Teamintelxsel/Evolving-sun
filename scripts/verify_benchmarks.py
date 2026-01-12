#!/usr/bin/env python3
"""
Benchmark Verification Script

This script validates benchmark result JSON files against the schema and checks
for common issues like placeholder data, unrealistic execution times, and
missing provenance information.

Usage:
    python scripts/verify_benchmarks.py [path_to_json_file]
    python scripts/verify_benchmarks.py --dir logs/benchmarks/
    python scripts/verify_benchmarks.py --all
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any


class BenchmarkValidator:
    """Validates benchmark results against quality standards."""

    # Known placeholder/simulated data indicators
    PLACEHOLDER_INDICATORS = [
        "placeholder",
        "simulated",
        "mock",
        "fake",
        "test",
        "sha256:placeholder",
        "abc123",
    ]

    # Minimum realistic execution time (1ms)
    MIN_REALISTIC_DURATION = 0.001

    # Maximum realistic execution time for quick benchmarks (1 hour)
    MAX_REALISTIC_DURATION = 3600

    def __init__(self, schema_path: Path = None):
        """Initialize the validator with optional schema path."""
        if schema_path is None:
            # Default to schemas/benchmark_result.json
            script_dir = Path(__file__).parent
            repo_root = script_dir.parent
            schema_path = repo_root / "schemas" / "benchmark_result.json"

        self.schema_path = schema_path
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict:
        """Load the JSON schema for validation."""
        if not self.schema_path.exists():
            print(f"Warning: Schema not found at {self.schema_path}", file=sys.stderr)
            return {}

        try:
            with open(self.schema_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading schema: {e}", file=sys.stderr)
            return {}

    def validate_file(self, filepath: Path) -> Tuple[bool, List[str]]:
        """
        Validate a single benchmark result file.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Check file exists
        if not filepath.exists():
            return False, [f"File does not exist: {filepath}"]

        # Load JSON
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Error reading file: {e}"]

        # If data is a list, validate each item
        if isinstance(data, list):
            all_valid = True
            for idx, item in enumerate(data):
                item_valid, item_issues = self._validate_benchmark_data(item, f"[{idx}]")
                if not item_valid:
                    all_valid = False
                    issues.extend(item_issues)
            return all_valid, issues
        else:
            return self._validate_benchmark_data(data)

    def _validate_benchmark_data(
        self, data: Dict, prefix: str = ""
    ) -> Tuple[bool, List[str]]:
        """Validate a single benchmark data object."""
        issues = []

        # Check required fields
        required_fields = ["benchmark_name", "timestamp", "status"]
        for field in required_fields:
            if field not in data:
                issues.append(f"{prefix}Missing required field: {field}")

        # Validate duration
        if "duration_seconds" in data:
            duration = data["duration_seconds"]
            if not isinstance(duration, (int, float)):
                issues.append(f"{prefix}duration_seconds must be a number")
            elif duration < self.MIN_REALISTIC_DURATION:
                issues.append(
                    f"{prefix}Unrealistic duration: {duration}s (< {self.MIN_REALISTIC_DURATION}s). "
                    "This may indicate simulated/placeholder data."
                )
            elif duration > self.MAX_REALISTIC_DURATION:
                issues.append(
                    f"{prefix}Suspiciously long duration: {duration}s (> {self.MAX_REALISTIC_DURATION}s)"
                )

        # Check for placeholder indicators in string values
        def check_placeholders(obj, path=""):
            """Recursively check for placeholder values."""
            if isinstance(obj, str):
                lower_val = obj.lower()
                for indicator in self.PLACEHOLDER_INDICATORS:
                    if indicator in lower_val:
                        issues.append(
                            f"{prefix}{path}: Contains placeholder indicator '{indicator}': {obj}"
                        )
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_placeholders(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    check_placeholders(item, f"{path}[{idx}]")

        check_placeholders(data)

        # Check provenance information
        if "provenance" in data:
            prov = data["provenance"]
            if not isinstance(prov, dict):
                issues.append(f"{prefix}provenance must be an object")
            else:
                # Check for important provenance fields
                recommended_fields = ["commit_sha", "timestamp"]
                missing_prov = [f for f in recommended_fields if f not in prov]
                if missing_prov:
                    issues.append(
                        f"{prefix}Missing recommended provenance fields: {', '.join(missing_prov)}"
                    )

                # Validate commit SHA format if present
                if "commit_sha" in prov:
                    sha = prov["commit_sha"]
                    if not isinstance(sha, str) or not all(
                        c in "0123456789abcdef" for c in sha.lower()
                    ):
                        issues.append(
                            f"{prefix}Invalid commit_sha format: {sha} (should be hex string)"
                        )

        # Check watermark if present
        if "watermark" in data:
            if "watermark_algorithm" not in data:
                issues.append(
                    f"{prefix}watermark present but watermark_algorithm missing"
                )

        # Validate status values
        if "status" in data:
            valid_statuses = ["passed", "failed", "completed", "error", "skipped"]
            if data["status"] not in valid_statuses:
                issues.append(
                    f"{prefix}Invalid status: {data['status']} (must be one of {valid_statuses})"
                )

        # If status is failed, should have error field
        if data.get("status") == "failed" and "error" not in data:
            issues.append(f"{prefix}Status is 'failed' but no error message provided")

        return len(issues) == 0, issues

    def validate_directory(self, dirpath: Path) -> Dict[str, Tuple[bool, List[str]]]:
        """
        Validate all JSON files in a directory.

        Returns:
            Dict mapping filename to (is_valid, issues) tuple
        """
        results = {}

        if not dirpath.exists():
            print(f"Error: Directory does not exist: {dirpath}", file=sys.stderr)
            return results

        # Find all JSON files
        json_files = list(dirpath.glob("*.json"))

        if not json_files:
            print(f"No JSON files found in {dirpath}", file=sys.stderr)
            return results

        for json_file in json_files:
            is_valid, issues = self.validate_file(json_file)
            results[json_file.name] = (is_valid, issues)

        return results

    def print_validation_report(
        self, results: Dict[str, Tuple[bool, List[str]]]
    ) -> bool:
        """
        Print a validation report and return overall success status.

        Returns:
            True if all files are valid, False otherwise
        """
        print("\n" + "=" * 70)
        print("BENCHMARK VALIDATION REPORT")
        print("=" * 70)

        all_valid = True
        total_files = len(results)
        valid_files = sum(1 for is_valid, _ in results.values() if is_valid)

        for filename, (is_valid, issues) in sorted(results.items()):
            status_symbol = "✓" if is_valid else "✗"
            print(f"\n{status_symbol} {filename}")

            if not is_valid:
                all_valid = False
                print(f"  Issues found: {len(issues)}")
                for issue in issues:
                    print(f"    - {issue}")

        print("\n" + "=" * 70)
        print(f"Summary: {valid_files}/{total_files} files passed validation")
        print("=" * 70)

        return all_valid


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate benchmark result files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", nargs="?", help="Path to benchmark JSON file to validate")
    group.add_argument(
        "--dir", type=str, help="Directory containing benchmark JSON files"
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Validate all benchmark files in logs/benchmarks/",
    )
    parser.add_argument(
        "--schema", type=str, help="Path to custom JSON schema file"
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Exit with error code if any issues found (for CI)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()

    # Determine schema path
    schema_path = None
    if args.schema:
        schema_path = Path(args.schema)

    validator = BenchmarkValidator(schema_path=schema_path)

    # Determine what to validate
    if args.all:
        # Default to logs/benchmarks/
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        dirpath = repo_root / "logs" / "benchmarks"
        results = validator.validate_directory(dirpath)
    elif args.dir:
        dirpath = Path(args.dir)
        results = validator.validate_directory(dirpath)
    else:
        # Single file
        filepath = Path(args.file)
        is_valid, issues = validator.validate_file(filepath)
        results = {filepath.name: (is_valid, issues)}

    # Print report
    all_valid = validator.print_validation_report(results)

    # Exit code
    if not all_valid and args.fail_on_warning:
        print("\nValidation failed. Exiting with error code 1.", file=sys.stderr)
        return 1

    return 0 if all_valid else 0


if __name__ == "__main__":
    sys.exit(main())
