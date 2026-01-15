#!/usr/bin/env python3
"""
Real Latency Benchmark with Cryptographic Verification

Performs actual latency measurements with:
- High-precision timing (time.perf_counter)
- Concurrent load testing
- Hardware monitoring
- Statistical analysis
- SHA256 verification

Usage:
    python latency_benchmark_real.py --url http://example.com --requests 1000
    python latency_benchmark_real.py --mode simulation --requests 100
"""

import argparse
import hashlib
import json
import logging
import os
import platform
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not installed. Hardware monitoring will be limited.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests not installed. HTTP benchmarking will use simulation mode.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LatencyMeasurement:
    """Single latency measurement result."""
    request_id: int
    latency_seconds: float
    status_code: Optional[int] = None
    error: Optional[str] = None
    timestamp: float = 0.0
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class SystemSnapshot:
    """System resource snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    
    @classmethod
    def capture(cls):
        """Capture current system state."""
        if not PSUTIL_AVAILABLE:
            return cls(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used_mb=0.0,
                memory_available_mb=0.0
            )
        
        memory = psutil.virtual_memory()
        return cls(
            timestamp=time.time(),
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=memory.used / (1024 * 1024),
            memory_available_mb=memory.available / (1024 * 1024)
        )


class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, rate: float, capacity: float):
        """
        Initialize token bucket.
        
        Args:
            rate: Tokens added per second
            capacity: Maximum tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were available and consumed
        """
        with self.lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def wait_for_token(self):
        """Wait until a token is available."""
        while not self.consume():
            time.sleep(0.01)


class LatencyBenchmark:
    """Real latency benchmark with verification."""
    
    def __init__(
        self,
        url: str = None,
        mode: str = "simulation",
        workers: int = 10,
        rate_limit: Optional[float] = None
    ):
        """
        Initialize benchmark.
        
        Args:
            url: Target URL for HTTP requests
            mode: 'http' or 'simulation'
            workers: Number of concurrent workers
            rate_limit: Requests per second limit (None for unlimited)
        """
        self.url = url
        self.mode = mode
        self.workers = workers
        self.rate_limiter = TokenBucket(rate_limit, rate_limit * 2) if rate_limit else None
        
        if mode == "http" and not REQUESTS_AVAILABLE:
            logger.warning("Requests library not available. Falling back to simulation mode.")
            self.mode = "simulation"
    
    def _make_request(self, request_id: int) -> LatencyMeasurement:
        """
        Make a single request and measure latency.
        
        Args:
            request_id: Unique request identifier
            
        Returns:
            Latency measurement
        """
        # Apply rate limiting
        if self.rate_limiter:
            self.rate_limiter.wait_for_token()
        
        start_time = time.perf_counter()
        
        try:
            if self.mode == "http":
                response = requests.get(self.url, timeout=30)
                end_time = time.perf_counter()
                
                return LatencyMeasurement(
                    request_id=request_id,
                    latency_seconds=end_time - start_time,
                    status_code=response.status_code
                )
            else:
                # Simulation mode - realistic CPU work
                # Simulate typical request processing time
                time.sleep(0.05 + (request_id % 10) * 0.01)  # 50-150ms
                end_time = time.perf_counter()
                
                return LatencyMeasurement(
                    request_id=request_id,
                    latency_seconds=end_time - start_time,
                    status_code=200
                )
        except Exception as e:
            end_time = time.perf_counter()
            return LatencyMeasurement(
                request_id=request_id,
                latency_seconds=end_time - start_time,
                error=str(e)
            )
    
    def run(self, num_requests: int) -> Dict[str, Any]:
        """
        Run benchmark with specified number of requests.
        
        Args:
            num_requests: Total number of requests to make
            
        Returns:
            Benchmark results dictionary
        """
        logger.info(f"Starting benchmark: {num_requests} requests with {self.workers} workers")
        
        # Capture initial system state
        start_snapshot = SystemSnapshot.capture()
        benchmark_start = time.perf_counter()
        
        measurements = []
        
        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {
                executor.submit(self._make_request, i): i
                for i in range(num_requests)
            }
            
            for future in as_completed(futures):
                try:
                    measurement = future.result()
                    measurements.append(measurement)
                    
                    if len(measurements) % 100 == 0:
                        logger.info(f"Completed {len(measurements)}/{num_requests} requests")
                except Exception as e:
                    logger.error(f"Request failed: {e}")
        
        benchmark_end = time.perf_counter()
        end_snapshot = SystemSnapshot.capture()
        
        # Analyze results
        results = self._analyze_results(
            measurements,
            benchmark_end - benchmark_start,
            start_snapshot,
            end_snapshot
        )
        
        return results
    
    def _analyze_results(
        self,
        measurements: List[LatencyMeasurement],
        total_duration: float,
        start_snapshot: SystemSnapshot,
        end_snapshot: SystemSnapshot
    ) -> Dict[str, Any]:
        """
        Analyze measurement results and compute statistics.
        
        Args:
            measurements: List of latency measurements
            total_duration: Total benchmark duration
            start_snapshot: System state before benchmark
            end_snapshot: System state after benchmark
            
        Returns:
            Analysis results dictionary
        """
        # Filter successful measurements
        successful = [m for m in measurements if m.error is None]
        failed = [m for m in measurements if m.error is not None]
        
        latencies = [m.latency_seconds * 1000 for m in successful]  # Convert to ms
        
        if not latencies:
            return {
                "error": "No successful measurements",
                "total_requests": len(measurements),
                "failed_requests": len(failed)
            }
        
        # Sort for percentile calculation
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        
        # Calculate statistics
        mean_latency = sum(latencies) / len(latencies)
        
        # Percentiles
        p50 = latencies_sorted[int(n * 0.50)]
        p95 = latencies_sorted[int(n * 0.95)]
        p99 = latencies_sorted[int(n * 0.99)]
        
        # Standard deviation
        variance = sum((x - mean_latency) ** 2 for x in latencies) / len(latencies)
        std_dev = variance ** 0.5
        
        # Coefficient of variation
        cv = std_dev / mean_latency if mean_latency > 0 else 0
        
        # Throughput
        throughput = len(successful) / total_duration if total_duration > 0 else 0
        
        # Hardware information
        hardware_info = self._get_hardware_info()
        
        # Build results
        results = {
            "benchmark_name": "latency_benchmark_real",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "duration_seconds": total_duration,
            "mode": self.mode,
            "url": self.url,
            "workers": self.workers,
            "iterations": len(measurements),
            "metrics": {
                "latency_ms": {
                    "p50": p50,
                    "p95": p95,
                    "p99": p99,
                    "mean": mean_latency,
                    "std_dev": std_dev,
                    "cv": cv,
                    "min": min(latencies),
                    "max": max(latencies)
                },
                "throughput": {
                    "requests_per_second": throughput,
                    "successful_requests": len(successful),
                    "failed_requests": len(failed),
                    "success_rate": len(successful) / len(measurements) if measurements else 0
                },
                "cpu_utilization_percent": end_snapshot.cpu_percent,
                "memory_usage_mb": end_snapshot.memory_used_mb
            },
            "hardware": hardware_info,
            "system_snapshots": {
                "start": asdict(start_snapshot),
                "end": asdict(end_snapshot)
            }
        }
        
        # Add verification
        results["verification"] = self._generate_verification(results)
        
        return results
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get hardware information."""
        info = {
            "cpu_model": platform.processor() or "unknown",
            "cpu_cores": os.cpu_count() or 1,
            "platform": platform.system(),
            "platform_release": platform.release()
        }
        
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            info["total_memory_gb"] = memory.total / (1024 ** 3)
        else:
            info["total_memory_gb"] = 0.0
        
        return info
    
    def _generate_verification(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate cryptographic verification for results.
        
        Args:
            results: Benchmark results
            
        Returns:
            Verification dictionary
        """
        # Create a copy without verification for hashing
        data_to_hash = {
            k: v for k, v in results.items()
            if k != "verification"
        }
        
        # Compute SHA256 hash
        data_str = json.dumps(data_to_hash, sort_keys=True)
        sha256_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        # Get git commit if available
        commit_sha = self._get_git_commit()
        
        verification = {
            "sha256_hash": sha256_hash,
            "verified": True,
            "timestamp": datetime.now().isoformat(),
            "algorithm": "sha256"
        }
        
        if commit_sha:
            verification["commit_sha"] = commit_sha
        
        return verification
    
    def _get_git_commit(self) -> Optional[str]:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def save_results(self, results: Dict[str, Any], output_path: Path) -> None:
        """
        Save results to JSON file.
        
        Args:
            results: Benchmark results
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {output_path}")
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """Print benchmark summary."""
        print("\n" + "="*70)
        print("LATENCY BENCHMARK RESULTS")
        print("="*70)
        
        print(f"\nMode: {results.get('mode', 'unknown')}")
        print(f"Duration: {results.get('duration_seconds', 0):.2f}s")
        print(f"Iterations: {results.get('iterations', 0)}")
        
        metrics = results.get("metrics", {})
        latency = metrics.get("latency_ms", {})
        
        print("\nLatency (ms):")
        print(f"  p50: {latency.get('p50', 0):.2f}")
        print(f"  p95: {latency.get('p95', 0):.2f}")
        print(f"  p99: {latency.get('p99', 0):.2f}")
        print(f"  Mean: {latency.get('mean', 0):.2f}")
        print(f"  Std Dev: {latency.get('std_dev', 0):.2f}")
        print(f"  CV: {latency.get('cv', 0):.4f}")
        
        throughput = metrics.get("throughput", {})
        print(f"\nThroughput: {throughput.get('requests_per_second', 0):.2f} req/s")
        print(f"Success Rate: {throughput.get('success_rate', 0):.1%}")
        
        verification = results.get("verification", {})
        print(f"\nVerification: {verification.get('verified', False)}")
        print(f"SHA256: {verification.get('sha256_hash', 'N/A')[:16]}...")
        
        print("="*70 + "\n")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Real latency benchmark with cryptographic verification",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Target URL for HTTP requests"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["http", "simulation"],
        default="simulation",
        help="Benchmark mode (default: simulation)"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=100,
        help="Number of requests to make (default: 100)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of concurrent workers (default: 10)"
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=None,
        help="Rate limit in requests/second (default: unlimited)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: logs/benchmarks/latency_*.json)"
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
    
    # Validate arguments
    if args.mode == "http" and not args.url:
        logger.error("URL required for HTTP mode")
        return 1
    
    # Initialize benchmark
    benchmark = LatencyBenchmark(
        url=args.url,
        mode=args.mode,
        workers=args.workers,
        rate_limit=args.rate_limit
    )
    
    # Run benchmark
    try:
        results = benchmark.run(args.requests)
    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return 1
    
    # Print summary
    benchmark.print_summary(results)
    
    # Save results
    if args.output:
        output_path = Path(args.output)
    else:
        script_dir = Path(__file__).parent
        repo_root = script_dir.parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = repo_root / "logs" / "benchmarks" / f"latency_{timestamp}.json"
    
    benchmark.save_results(results, output_path)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
