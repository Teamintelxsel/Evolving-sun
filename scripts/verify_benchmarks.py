#!/usr/bin/env python3
"""
Enhanced Benchmark Verification Script

Validates benchmark results against quality criteria:
- Timing validation (no instant execution)
- Data integrity (SHA256 verification)
- Statistical validity
- Hardware verification
- Schema compliance

Usage:
    python verify_benchmarks.py <path_to_results>
    python verify_benchmarks.py logs/benchmarks/
"""

import argparse
import hashlib
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("Warning: jsonschema not installed. Schema validation will be skipped.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkVerifier:
    """Verifies benchmark results for authenticity and quality."""
    
    def __init__(self, schema_path: Path = None):
        """Initialize the verifier with optional schema."""
        self.schema = None
        if schema_path and schema_path.exists() and JSONSCHEMA_AVAILABLE:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
    
    def verify_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Verify a single benchmark result file.
        
        Args:
            filepath: Path to the benchmark result JSON file
            
        Returns:
            Dictionary with verification results
        """
        logger.info(f"Verifying: {filepath}")
        
        result = {
            "file": str(filepath),
            "passed": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
        except Exception as e:
            result["passed"] = False
            result["errors"].append(f"Failed to load JSON: {e}")
            return result
        
        # Handle list of results (legacy format)
        if isinstance(data, list):
            result["warnings"].append("File contains list of results. Verifying each item.")
            all_checks = {"timing": [], "data_integrity": [], "statistical": [], "hardware": [], "schema": []}
            
            for idx, item in enumerate(data):
                item_checks = {
                    "timing": self._check_timing(item),
                    "data_integrity": self._check_data_integrity(item),
                    "statistical": self._check_statistical_validity(item),
                    "hardware": self._check_hardware_specs(item),
                    "schema": self._check_schema_compliance(item)
                }
                
                for check_name, check_result in item_checks.items():
                    all_checks[check_name].append(check_result)
                    if not check_result["passed"]:
                        result["passed"] = False
                        result["errors"].extend([f"Item {idx}: {err}" for err in check_result.get("errors", [])])
                    result["warnings"].extend([f"Item {idx}: {warn}" for warn in check_result.get("warnings", [])])
            
            result["checks"] = {
                check_name: {
                    "passed": all(c["passed"] for c in checks),
                    "items": checks
                }
                for check_name, checks in all_checks.items()
            }
            return result
        
        # Run all verification checks for single result
        result["checks"]["timing"] = self._check_timing(data)
        result["checks"]["data_integrity"] = self._check_data_integrity(data)
        result["checks"]["statistical"] = self._check_statistical_validity(data)
        result["checks"]["hardware"] = self._check_hardware_specs(data)
        result["checks"]["schema"] = self._check_schema_compliance(data)
        
        # Aggregate results
        for check_name, check_result in result["checks"].items():
            if not check_result["passed"]:
                result["passed"] = False
                result["errors"].extend(check_result.get("errors", []))
            result["warnings"].extend(check_result.get("warnings", []))
        
        return result
    
    def _check_timing(self, data: Dict) -> Dict[str, Any]:
        """Validate that timing is realistic (not simulated)."""
        check = {"passed": True, "errors": [], "warnings": []}
        
        duration = data.get("duration_seconds", 0)
        
        # Check for suspiciously fast execution (likely simulated)
        if duration < 0.01:
            check["passed"] = False
            check["errors"].append(
                f"Suspiciously fast execution: {duration}s (< 0.01s). "
                "This indicates simulated or fake data."
            )
        
        # Check for scientific notation issues
        if duration > 0 and duration < 0.001:
            check["warnings"].append(
                f"Very fast execution: {duration}s. Verify this is accurate."
            )
        
        # Check if duration matches expected range for benchmark type
        benchmark_name = data.get("benchmark_name", "")
        if "latency" in benchmark_name.lower() and duration < 1:
            check["warnings"].append(
                "Latency benchmark completed in < 1s. "
                "Expected longer duration for proper measurement."
            )
        
        return check
    
    def _check_data_integrity(self, data: Dict) -> Dict[str, Any]:
        """Verify SHA256 hash and data integrity."""
        check = {"passed": True, "errors": [], "warnings": []}
        
        verification = data.get("verification", {})
        
        if not verification:
            check["warnings"].append("No verification block found")
            return check
        
        stored_hash = verification.get("sha256_hash", "")
        
        if not stored_hash:
            check["warnings"].append("No SHA256 hash found")
            return check
        
        # Validate hash format
        if not self._is_valid_sha256(stored_hash):
            check["passed"] = False
            check["errors"].append(
                f"Invalid SHA256 hash format: {stored_hash}"
            )
            return check
        
        # Attempt to recompute and verify hash
        # (This would require knowing which fields to hash)
        check["warnings"].append("Hash verification requires additional context")
        
        return check
    
    def _check_statistical_validity(self, data: Dict) -> Dict[str, Any]:
        """Check for reasonable variance and distribution."""
        check = {"passed": True, "errors": [], "warnings": []}
        
        metrics = data.get("metrics", {})
        
        # Check for suspiciously perfect numbers
        if "accuracy" in metrics:
            accuracy = metrics["accuracy"]
            # Flag perfect scores without proper verification
            if accuracy >= 0.99 and "iterations" not in data:
                check["warnings"].append(
                    f"High accuracy ({accuracy:.1%}) claimed without iteration count"
                )
            
            # Flag impossible scores
            if accuracy > 1.0:
                check["passed"] = False
                check["errors"].append(f"Impossible accuracy: {accuracy} (> 1.0)")
        
        # Check latency metrics
        latency = metrics.get("latency_ms", {})
        if latency:
            p50 = latency.get("p50", 0)
            p95 = latency.get("p95", 0)
            p99 = latency.get("p99", 0)
            
            # Validate percentile ordering
            if p50 > 0 and p95 > 0 and p99 > 0:
                if not (p50 <= p95 <= p99):
                    check["passed"] = False
                    check["errors"].append(
                        f"Invalid percentile ordering: p50={p50}, p95={p95}, p99={p99}"
                    )
            
            # Check coefficient of variation for stability
            cv = latency.get("cv", 0)
            if cv > 0.001:  # 0.1%
                check["warnings"].append(
                    f"High latency variance (CV={cv:.4f}). Target is < 0.001 (0.1%)"
                )
        
        # Check CPU utilization claims
        cpu_util = metrics.get("cpu_utilization_percent", 0)
        if cpu_util > 99.95:
            check["warnings"].append(
                f"Very high CPU utilization claimed: {cpu_util:.1f}%. "
                "Verify this is sustained over the full benchmark duration."
            )
        
        return check
    
    def _check_hardware_specs(self, data: Dict) -> Dict[str, Any]:
        """Verify hardware specifications are documented."""
        check = {"passed": True, "errors": [], "warnings": []}
        
        hardware = data.get("hardware", {})
        
        if not hardware:
            check["warnings"].append("No hardware specifications documented")
            return check
        
        # Check required fields
        required_fields = ["cpu_model", "total_memory_gb"]
        for field in required_fields:
            if field not in hardware:
                check["warnings"].append(f"Missing hardware field: {field}")
        
        # Validate values
        if "total_memory_gb" in hardware:
            mem = hardware["total_memory_gb"]
            if mem <= 0:
                check["passed"] = False
                check["errors"].append(f"Invalid memory size: {mem} GB")
        
        return check
    
    def _check_schema_compliance(self, data: Dict) -> Dict[str, Any]:
        """Validate against JSON schema if available."""
        check = {"passed": True, "errors": [], "warnings": []}
        
        if not self.schema:
            check["warnings"].append("No schema available for validation")
            return check
        
        if not JSONSCHEMA_AVAILABLE:
            check["warnings"].append("jsonschema library not available")
            return check
        
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            check["passed"] = False
            check["errors"].append(f"Schema validation failed: {e.message}")
        except Exception as e:
            check["warnings"].append(f"Schema validation error: {e}")
        
        return check
    
    def _is_valid_sha256(self, hash_str: str) -> bool:
        """Check if string is a valid SHA256 hash."""
        if not hash_str or not isinstance(hash_str, str):
            return False
        if len(hash_str) != 64:
            return False
        try:
            int(hash_str, 16)
            return True
        except ValueError:
            return False
    
    def verify_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Verify all JSON files in a directory.
        
        Args:
            directory: Path to directory containing benchmark results
            
        Returns:
            List of verification results for each file
        """
        results = []
        
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return results
        
        json_files = list(directory.glob("*.json"))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return results
        
        logger.info(f"Found {len(json_files)} JSON files to verify")
        
        for filepath in json_files:
            result = self.verify_file(filepath)
            results.append(result)
        
        return results
    
    def generate_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary report from verification results.
        
        Args:
            results: List of individual file verification results
            
        Returns:
            Summary report dictionary
        """
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed
        
        report = {
            "summary": {
                "total_files": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": passed / total if total > 0 else 0
            },
            "timestamp": datetime.now().isoformat(),
            "files": results
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]) -> None:
        """Print formatted verification report."""
        print("\n" + "="*70)
        print("BENCHMARK VERIFICATION REPORT")
        print("="*70)
        
        summary = report["summary"]
        print(f"\nTotal files: {summary['total_files']}")
        print(f"Passed: {summary['passed']} ({summary['pass_rate']:.1%})")
        print(f"Failed: {summary['failed']}")
        
        print("\n" + "-"*70)
        print("INDIVIDUAL FILE RESULTS")
        print("-"*70)
        
        for file_result in report["files"]:
            status = "✓ PASS" if file_result["passed"] else "✗ FAIL"
            print(f"\n{status}: {Path(file_result['file']).name}")
            
            if file_result["errors"]:
                print("  Errors:")
                for error in file_result["errors"]:
                    print(f"    - {error}")
            
            if file_result["warnings"]:
                print("  Warnings:")
                for warning in file_result["warnings"]:
                    print(f"    - {warning}")
        
        print("\n" + "="*70)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Verify benchmark results for authenticity and quality",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "path",
        type=str,
        help="Path to benchmark result file or directory"
    )
    parser.add_argument(
        "--schema",
        type=str,
        default=None,
        help="Path to JSON schema file for validation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to save verification report JSON"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Determine schema path
    schema_path = None
    if args.schema:
        schema_path = Path(args.schema)
    else:
        # Try to find schema in standard location
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        default_schema = repo_root / "schemas" / "benchmark_result.json"
        if default_schema.exists():
            schema_path = default_schema
            logger.info(f"Using schema: {schema_path}")
    
    # Initialize verifier
    verifier = BenchmarkVerifier(schema_path=schema_path)
    
    # Verify path
    target_path = Path(args.path)
    
    if target_path.is_file():
        results = [verifier.verify_file(target_path)]
    elif target_path.is_dir():
        results = verifier.verify_directory(target_path)
    else:
        logger.error(f"Path not found: {target_path}")
        return 1
    
    # Generate and print report
    report = verifier.generate_report(results)
    verifier.print_report(report)
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to: {output_path}")
    
    # Return exit code based on results
    return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
