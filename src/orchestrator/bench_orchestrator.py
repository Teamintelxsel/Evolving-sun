#!/usr/bin/env python3
"""
Benchmark Orchestrator for Evolving-sun

This module orchestrates the execution of benchmark suites with:
- Task sharding and parallel execution
- Retry logic with exponential backoff
- Deterministic seed management
- Comprehensive provenance logging
- Watermarked JSON summaries
"""

import hashlib
import json
import logging
import os
import platform
import re
import subprocess
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class BenchmarkOrchestrator:
    """Orchestrates benchmark suite execution with provenance tracking."""
    
    # SHA256 digest format: sha256: followed by 64 hexadecimal characters
    DIGEST_PATTERN = re.compile(r'^sha256:[0-9a-f]{64}$', re.IGNORECASE)
    
    # Version for compatibility tracking
    VERSION = "2.0.0"
    
    def __init__(self, tasks_file: str = "tasks.yaml", output_dir: Optional[str] = None):
        """
        Initialize the benchmark orchestrator.
        
        Args:
            tasks_file: Path to the tasks YAML configuration file
            output_dir: Output directory for benchmark results (defaults to logs/benchmarks)
        """
        self.tasks_file = Path(tasks_file)
        
        # Set up logging with enhanced formatting
        self.logger = logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Log orchestrator initialization
        self.logger.info(f"Initializing BenchmarkOrchestrator v{self.VERSION}")
        
        if output_dir is None:
            # Default to logs/benchmarks in repository root
            if self.tasks_file.is_absolute():
                repo_root = self._find_repo_root()
            else:
                repo_root = Path.cwd()
            self.output_dir = repo_root / "logs" / "benchmarks"
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Output directory: {self.output_dir}")
        
        # Load tasks configuration with validation
        try:
            self.tasks = self._load_tasks()
            self._validate_configuration()
        except Exception as e:
            self.logger.error(f"Failed to load or validate configuration: {e}")
            raise
        
        # Provenance data
        self.provenance = self._collect_provenance()
        self.logger.info("Orchestrator initialized successfully")
    
    def _find_repo_root(self) -> Path:
        """Find the repository root directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return Path.cwd()
    
    def _load_tasks(self) -> Dict[str, Any]:
        """Load tasks configuration from YAML file with enhanced error handling."""
        if not self.tasks_file.exists():
            raise FileNotFoundError(f"Tasks file not found: {self.tasks_file}")
        
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                tasks = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in tasks file: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to read tasks file: {e}")
        
        if not tasks or 'suites' not in tasks:
            raise ValueError("Invalid tasks.yaml: missing 'suites' key")
        
        self.logger.info(f"Loaded {len(tasks.get('suites', {}))} benchmark suite(s)")
        return tasks
    
    def _validate_configuration(self) -> None:
        """Validate the loaded configuration for completeness and correctness."""
        suites = self.tasks.get('suites', {})
        
        if not suites:
            raise ValueError("No benchmark suites defined in configuration")
        
        for suite_name, suite_config in suites.items():
            # Validate required fields
            if 'timeout' not in suite_config:
                self.logger.warning(f"Suite '{suite_name}' missing 'timeout' field, using default")
            
            # Validate timeout values
            timeout = suite_config.get('timeout', 3600)
            if not isinstance(timeout, int) or timeout <= 0:
                raise ValueError(f"Suite '{suite_name}' has invalid timeout: {timeout} (must be positive integer)")
            
            # Suite-specific validation
            if suite_name == 'swebench':
                if 'shards' in suite_config:
                    shards = suite_config['shards']
                    if not isinstance(shards, int) or shards < 1:
                        raise ValueError(f"Invalid shards value: {shards}")
                
                if 'shard_size' in suite_config:
                    shard_size = suite_config['shard_size']
                    if not isinstance(shard_size, int) or shard_size < 1:
                        raise ValueError(f"Invalid shard_size value: {shard_size}")
        
        self.logger.info("Configuration validation passed")
    
    def _collect_provenance(self) -> Dict[str, Any]:
        """Collect comprehensive provenance information."""
        provenance = {
            "timestamp": datetime.now().isoformat(),
            "environment": {
                "os": platform.system(),
                "os_version": platform.version(),
                "os_release": platform.release(),
                "python_version": sys.version,
                "python_implementation": platform.python_implementation(),
                "machine": platform.machine(),
                "processor": platform.processor(),
            },
            "repository": {},
            "libraries": {}
        }
        
        # Git information
        try:
            git_commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            provenance["repository"]["commit_sha"] = git_commit
            
            git_branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            provenance["repository"]["branch"] = git_branch
            
            git_remote = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"],
                stderr=subprocess.DEVNULL,
                text=True
            ).strip()
            provenance["repository"]["remote_url"] = git_remote
        except (subprocess.CalledProcessError, FileNotFoundError):
            provenance["repository"]["error"] = "Git information not available"
        
        # Library versions
        try:
            import importlib.metadata
            
            # Try to get common library versions
            for lib in ["pyyaml", "requests", "numpy", "biopython"]:
                try:
                    version = importlib.metadata.version(lib)
                    provenance["libraries"][lib] = version
                except importlib.metadata.PackageNotFoundError:
                    pass
        except ImportError:
            pass
        
        return provenance
    
    def _get_deterministic_seed(self, suite_name: str, shard_idx: int = 0) -> int:
        """
        Generate a deterministic seed based on suite name and shard index.
        
        Args:
            suite_name: Name of the benchmark suite
            shard_idx: Shard index (for sharded execution)
        
        Returns:
            Deterministic integer seed
        """
        # Create a deterministic seed from suite name and shard
        seed_string = f"{suite_name}_shard_{shard_idx}"
        hash_obj = hashlib.sha256(seed_string.encode())
        # Use first 8 bytes of hash as seed
        seed = int.from_bytes(hash_obj.digest()[:8], byteorder='big') % (2**31)
        return seed
    
    def _execute_with_retry(
        self,
        func,
        max_retries: int = 1,
        initial_backoff: float = 30.0,
        max_backoff: float = 120.0,
        *args,
        **kwargs
    ) -> Tuple[bool, Any, Optional[str]]:
        """
        Execute a function with retry logic and exponential backoff.
        
        Args:
            func: Function to execute
            max_retries: Maximum number of retries (default: 1)
            initial_backoff: Initial backoff time in seconds (default: 30s)
            max_backoff: Maximum backoff time in seconds (default: 120s)
            *args, **kwargs: Arguments to pass to the function
        
        Returns:
            Tuple of (success, result, error_message)
        """
        backoff = initial_backoff
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = func(*args, **kwargs)
                return (True, result, None)
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    print(f"Retrying in {backoff:.1f} seconds...")
                    time.sleep(backoff)
                    backoff = min(backoff * 2, max_backoff)
                else:
                    print(f"All {max_retries + 1} attempts failed")
        
        return (False, None, last_error)
    
    def _execute_swebench_suite(self, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute SWE-Bench benchmark suite.
        
        Args:
            suite_config: Suite configuration from tasks.yaml
        
        Returns:
            Results dictionary
        """
        dataset = suite_config.get("dataset", "Verified")
        shards = suite_config.get("shards", 1)
        shard_size = suite_config.get("shard_size", 25)
        num_workers = suite_config.get("num_workers", 1)
        image_digest = suite_config.get("image_digest", "")
        timeout = suite_config.get("timeout", 3600)
        
        # Validate image_digest format for reproducibility
        if not image_digest:
            self.logger.warning(
                "\n" + "!" * 70 + "\n"
                "SWE-Bench image_digest is not configured!\n"
                "For reproducible benchmarks, you must pin the Docker image by digest.\n"
                "See docs/SWE_BENCH_SETUP.md for instructions on obtaining the digest.\n"
                + "!" * 70
            )
        elif not self.DIGEST_PATTERN.match(image_digest):
            self.logger.warning(
                "\n" + "!" * 70 + "\n"
                f"Invalid SWE-Bench image_digest format: {image_digest}\n"
                "Expected format: sha256: followed by 64 hexadecimal characters\n"
                "Example: sha256:1234567890abcdef...(64 chars total)\n"
                "See docs/SWE_BENCH_SETUP.md for instructions on obtaining the digest.\n"
                + "!" * 70
            )
        
        results = {
            "suite": "swebench",
            "dataset": dataset,
            "shards": shards,
            "shard_size": shard_size,
            "num_workers": num_workers,
            "image_digest": image_digest,
            "timeout": timeout,
            "shard_results": [],
            "status": "not_started",
            "total_tasks": shards * shard_size
        }
        
        all_passed = True
        
        # Execute each shard sequentially
        for shard_idx in range(shards):
            seed = self._get_deterministic_seed("swebench", shard_idx)
            
            shard_result = {
                "shard_idx": shard_idx,
                "seed": seed,
                "size": shard_size,
                "status": "running",
                "start_time": datetime.now().isoformat()
            }
            
            print(f"\n{'='*60}")
            print(f"Executing SWE-Bench shard {shard_idx + 1}/{shards}")
            print(f"Dataset: {dataset}, Size: {shard_size}, Workers: {num_workers}")
            print(f"Deterministic seed: {seed}")
            print(f"{'='*60}\n")
            
            # Simulate SWE-Bench execution
            # In a real implementation, this would execute the actual benchmark
            success, shard_output, error = self._execute_with_retry(
                self._simulate_swebench_shard,
                max_retries=1,
                shard_idx=shard_idx,
                shard_size=shard_size,
                seed=seed,
                timeout=timeout
            )
            
            shard_result["end_time"] = datetime.now().isoformat()
            shard_result["status"] = "completed" if success else "failed"
            
            if success:
                shard_result["results"] = shard_output
            else:
                shard_result["error"] = error
                all_passed = False
            
            results["shard_results"].append(shard_result)
        
        results["status"] = "completed" if all_passed else "partial_failure"
        return results
    
    def _simulate_swebench_shard(
        self, shard_idx: int, shard_size: int, seed: int, timeout: int
    ) -> Dict[str, Any]:
        """Simulate SWE-Bench shard execution (placeholder for actual implementation)."""
        # This is a placeholder - real implementation would execute actual SWE-Bench tasks
        time.sleep(1)  # Simulate work
        
        return {
            "passed": shard_size - 2,  # Simulated results
            "failed": 2,
            "timeout": 0,
            "tasks_completed": shard_size,
            "seed_used": seed
        }
    
    def _execute_gpqa_suite(self, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute GPQA benchmark suite.
        
        Args:
            suite_config: Suite configuration from tasks.yaml
        
        Returns:
            Results dictionary
        """
        variant = suite_config.get("variant", "diamond")
        self_consistency_k = suite_config.get("self_consistency_k", 10)
        limit = suite_config.get("limit", 500)
        dataset_revision = suite_config.get("dataset_revision", "main")
        timeout = suite_config.get("timeout", 1800)
        
        seed = self._get_deterministic_seed("gpqa", 0)
        
        results = {
            "suite": "gpqa",
            "variant": variant,
            "self_consistency_k": self_consistency_k,
            "limit": limit,
            "dataset_revision": dataset_revision,
            "seed": seed,
            "timeout": timeout,
            "status": "running",
            "start_time": datetime.now().isoformat()
        }
        
        print(f"\n{'='*60}")
        print(f"Executing GPQA benchmark")
        print(f"Variant: {variant}, K: {self_consistency_k}, Limit: {limit}")
        print(f"Dataset revision: {dataset_revision}")
        print(f"Deterministic seed: {seed}")
        print(f"{'='*60}\n")
        
        # Execute with retry
        success, output, error = self._execute_with_retry(
            self._simulate_gpqa_execution,
            max_retries=1,
            variant=variant,
            k=self_consistency_k,
            limit=limit,
            seed=seed,
            timeout=timeout
        )
        
        results["end_time"] = datetime.now().isoformat()
        results["status"] = "completed" if success else "failed"
        
        if success:
            results["results"] = output
        else:
            results["error"] = error
        
        return results
    
    def _simulate_gpqa_execution(
        self, variant: str, k: int, limit: int, seed: int, timeout: int
    ) -> Dict[str, Any]:
        """Simulate GPQA execution (placeholder for actual implementation)."""
        time.sleep(1)  # Simulate work
        
        return {
            "accuracy": 0.847,  # Simulated accuracy
            "questions_answered": limit,
            "self_consistency_k": k,
            "variant": variant,
            "seed_used": seed
        }
    
    def _execute_kegg_suite(self, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute KEGG benchmark suite.
        
        Args:
            suite_config: Suite configuration from tasks.yaml
        
        Returns:
            Results dictionary
        """
        pathway = suite_config.get("pathway", "ko01100")
        kegg_url = suite_config.get("kegg_url", "https://rest.kegg.jp")
        timeout = suite_config.get("timeout", 600)
        
        seed = self._get_deterministic_seed("kegg", 0)
        
        # Get Biopython version if available
        biopython_version = None
        try:
            import importlib.metadata
            biopython_version = importlib.metadata.version("biopython")
        except (ImportError, Exception):
            pass
        
        results = {
            "suite": "kegg",
            "pathway": pathway,
            "kegg_url": kegg_url,
            "biopython_version": biopython_version,
            "seed": seed,
            "timeout": timeout,
            "status": "running",
            "start_time": datetime.now().isoformat()
        }
        
        print(f"\n{'='*60}")
        print(f"Executing KEGG benchmark")
        print(f"Pathway: {pathway}, URL: {kegg_url}")
        print(f"Biopython version: {biopython_version or 'not installed'}")
        print(f"Deterministic seed: {seed}")
        print(f"{'='*60}\n")
        
        # Execute with retry
        success, output, error = self._execute_with_retry(
            self._simulate_kegg_execution,
            max_retries=1,
            pathway=pathway,
            kegg_url=kegg_url,
            seed=seed,
            timeout=timeout
        )
        
        results["end_time"] = datetime.now().isoformat()
        results["status"] = "completed" if success else "failed"
        
        if success:
            results["results"] = output
        else:
            results["error"] = error
        
        return results
    
    def _simulate_kegg_execution(
        self, pathway: str, kegg_url: str, seed: int, timeout: int
    ) -> Dict[str, Any]:
        """Simulate KEGG execution (placeholder for actual implementation)."""
        time.sleep(1)  # Simulate work
        
        return {
            "pathway_retrieved": pathway,
            "compounds_analyzed": 150,  # Simulated
            "reactions_analyzed": 200,   # Simulated
            "kegg_url_used": kegg_url,
            "seed_used": seed
        }
    
    def _generate_watermark(self) -> str:
        """Generate a watermark string for the benchmark results."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        commit_sha = self.provenance.get("repository", {}).get("commit_sha", "unknown")[:8]
        
        watermark = f"Evolving-sun Benchmark Results | {timestamp} | Commit: {commit_sha}"
        return watermark
    
    def execute_all_suites(self) -> Dict[str, Any]:
        """
        Execute all benchmark suites defined in tasks.yaml.
        
        Returns:
            Consolidated results dictionary with provenance and watermark
        """
        print(f"\n{'#'*60}")
        print("# Evolving-sun Benchmark Orchestrator")
        print(f"# Started: {datetime.now().isoformat()}")
        print(f"{'#'*60}\n")
        
        suites = self.tasks.get("suites", {})
        results = {
            "watermark": self._generate_watermark(),
            "provenance": self.provenance,
            "execution": {
                "start_time": datetime.now().isoformat(),
                "tasks_file": str(self.tasks_file),
            },
            "suites": {}
        }
        
        # Execute each suite
        for suite_name, suite_config in suites.items():
            print(f"\n{'*'*60}")
            print(f"* Starting suite: {suite_name}")
            print(f"{'*'*60}")
            
            if suite_name == "swebench":
                suite_results = self._execute_swebench_suite(suite_config)
            elif suite_name == "gpqa":
                suite_results = self._execute_gpqa_suite(suite_config)
            elif suite_name == "kegg":
                suite_results = self._execute_kegg_suite(suite_config)
            else:
                print(f"Warning: Unknown suite type '{suite_name}', skipping")
                suite_results = {
                    "suite": suite_name,
                    "status": "skipped",
                    "error": f"Unknown suite type: {suite_name}"
                }
            
            results["suites"][suite_name] = suite_results
        
        results["execution"]["end_time"] = datetime.now().isoformat()
        
        print(f"\n{'#'*60}")
        print("# Benchmark Orchestration Complete")
        print(f"# Finished: {datetime.now().isoformat()}")
        print(f"{'#'*60}\n")
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> Path:
        """
        Save benchmark results to a JSON file.
        
        Args:
            results: Results dictionary to save
            filename: Optional custom filename (defaults to timestamped name)
        
        Returns:
            Path to saved results file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_orchestrated_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to: {filepath}")
        return filepath
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a summary of benchmark results."""
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}")
        print(f"\n{results['watermark']}\n")
        
        for suite_name, suite_results in results.get("suites", {}).items():
            status = suite_results.get("status", "unknown")
            status_symbol = "✓" if status in ["completed", "success"] else "✗"
            
            print(f"{status_symbol} {suite_name.upper()}: {status}")
            
            # Suite-specific summary
            if suite_name == "swebench" and "shard_results" in suite_results:
                total_passed = sum(
                    shard.get("results", {}).get("passed", 0)
                    for shard in suite_results["shard_results"]
                )
                total_tasks = suite_results.get("total_tasks", 0)
                print(f"  Tasks passed: {total_passed}/{total_tasks}")
            
            elif suite_name == "gpqa" and "results" in suite_results:
                accuracy = suite_results["results"].get("accuracy", 0)
                k = suite_results.get("self_consistency_k", 0)
                print(f"  Accuracy: {accuracy:.3f} (k={k})")
            
            elif suite_name == "kegg" and "results" in suite_results:
                pathway = suite_results.get("pathway", "")
                print(f"  Pathway: {pathway}")
        
        print(f"{'='*60}\n")


def main():
    """Main entry point for the benchmark orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Orchestrate benchmark suite execution with provenance tracking"
    )
    parser.add_argument(
        "--tasks-file",
        type=str,
        default="tasks.yaml",
        help="Path to tasks YAML configuration file (default: tasks.yaml)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for results (default: logs/benchmarks)"
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default=None,
        help="Custom output filename for results JSON"
    )
    
    args = parser.parse_args()
    
    try:
        orchestrator = BenchmarkOrchestrator(
            tasks_file=args.tasks_file,
            output_dir=args.output_dir
        )
        
        results = orchestrator.execute_all_suites()
        orchestrator.print_summary(results)
        orchestrator.save_results(results, filename=args.output_name)
        
        # Exit with success only if all suites completed successfully
        all_completed = all(
            suite.get("status") in ["completed", "success"]
            for suite in results.get("suites", {}).values()
        )
        
        return 0 if all_completed else 1
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
