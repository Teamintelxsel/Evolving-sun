#!/usr/bin/env python3
"""
Distributed Executor for Multi-GPU Benchmark Execution

Runs benchmark iterations in parallel across multiple GPUs using Ray.

Usage:
    python distributed_executor.py --iterations 500 --workers 10
    python distributed_executor.py --dry-run
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False
    print("WARNING: Ray not available. Falling back to serial execution.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DistributedExecutor:
    """Distributed benchmark executor using Ray."""
    
    def __init__(
        self,
        num_workers: int = 10,
        batch_size: int = 10,
        use_ray: bool = True
    ):
        """
        Initialize distributed executor.
        
        Args:
            num_workers: Number of parallel workers
            batch_size: Iterations per batch
            use_ray: Whether to use Ray (falls back to serial if False)
        """
        self.num_workers = num_workers
        self.batch_size = batch_size
        self.use_ray = use_ray and RAY_AVAILABLE
        
        if self.use_ray:
            self._initialize_ray()
        else:
            logger.warning("Ray not available. Running in serial mode.")
    
    def _initialize_ray(self):
        """Initialize Ray cluster."""
        try:
            # Check if Ray is already initialized
            if not ray.is_initialized():
                # Detect available GPUs
                num_gpus = self._detect_gpus()
                
                # Initialize Ray
                ray.init(
                    num_gpus=num_gpus,
                    num_cpus=os.cpu_count() or self.num_workers * 3,
                    ignore_reinit_error=True
                )
                
                logger.info(f"Ray initialized with {num_gpus} GPUs")
            else:
                logger.info("Ray already initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Ray: {e}")
            self.use_ray = False
    
    def _detect_gpus(self) -> int:
        """Detect number of available GPUs."""
        try:
            import subprocess
            result = subprocess.run(
                ['nvidia-smi', '--list-gpus'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                gpu_count = len(result.stdout.strip().split('\n'))
                return gpu_count
        except Exception:
            pass
        
        # Fallback: check CUDA_VISIBLE_DEVICES
        cuda_visible = os.getenv('CUDA_VISIBLE_DEVICES', '')
        if cuda_visible:
            return len(cuda_visible.split(','))
        
        return 0  # No GPUs detected
    
    def run_iteration(self, iteration: int) -> Dict[str, Any]:
        """
        Run a single benchmark iteration.
        
        In production, this would call the actual benchmark.
        For now, simulates work.
        
        Args:
            iteration: Iteration number
            
        Returns:
            Iteration result
        """
        # Simulate benchmark work
        time.sleep(0.1)  # Simulate 100ms work
        
        # Calculate metrics (simplified)
        accuracy = 0.85 + (iteration / 1000) * 0.15  # Progressive improvement
        latency_ms = 50 + (iteration % 20)
        
        return {
            'iteration': iteration,
            'accuracy': min(0.999, accuracy),
            'latency_ms': latency_ms,
            'throughput_rps': 100 + (iteration % 50),
            'cpu_utilization': 95 + (iteration % 10) / 2,
            'timestamp': time.time(),
            'worker_id': 0  # Will be set by worker
        }
    
    def run_distributed(
        self,
        total_iterations: int,
        resume_from: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Run iterations in distributed mode using Ray.
        
        Args:
            total_iterations: Total iterations to run
            resume_from: Iteration to resume from
            
        Returns:
            List of all iteration results
        """
        start_iteration = resume_from or 1
        
        if not self.use_ray:
            logger.warning("Running in serial mode (Ray not available)")
            return self.run_serial(total_iterations, start_iteration)
        
        logger.info(f"Starting distributed execution: {self.num_workers} workers")
        
        # Define remote worker
        @ray.remote(num_gpus=1 if self._detect_gpus() > 0 else 0)
        def run_iteration_remote(iteration):
            return self.run_iteration(iteration)
        
        # Submit all tasks
        futures = []
        for i in range(start_iteration, total_iterations + 1):
            future = run_iteration_remote.remote(i)
            futures.append((i, future))
        
        # Collect results with progress tracking
        results = []
        completed = 0
        
        logger.info(f"Submitted {len(futures)} tasks")
        
        while futures:
            # Wait for any task to complete
            ready_futures = [f[1] for f in futures]
            ready, not_ready = ray.wait(ready_futures, num_returns=1, timeout=1.0)
            
            # Process completed tasks
            for ready_ref in ready:
                # Find the iteration number for this future
                for i, (iteration, future) in enumerate(futures):
                    if future == ready_ref:
                        try:
                            result = ray.get(ready_ref)
                            results.append(result)
                            completed += 1
                            
                            if completed % 10 == 0:
                                logger.info(
                                    f"Progress: {completed}/{total_iterations} "
                                    f"({completed/total_iterations*100:.1f}%)"
                                )
                            
                            # Remove from futures list
                            futures.pop(i)
                            break
                        except Exception as e:
                            logger.error(f"Task failed for iteration {iteration}: {e}")
                            futures.pop(i)
                            break
        
        # Sort results by iteration
        results.sort(key=lambda x: x['iteration'])
        
        return results
    
    def run_serial(
        self,
        total_iterations: int,
        start_iteration: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Run iterations in serial mode (fallback).
        
        Args:
            total_iterations: Total iterations
            start_iteration: Starting iteration
            
        Returns:
            List of results
        """
        results = []
        
        logger.info(f"Running {total_iterations} iterations in serial mode")
        
        for i in range(start_iteration, total_iterations + 1):
            result = self.run_iteration(i)
            results.append(result)
            
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{total_iterations}")
        
        return results
    
    def aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from all iterations.
        
        Args:
            results: List of iteration results
            
        Returns:
            Aggregated results
        """
        if not results:
            return {"error": "No results to aggregate"}
        
        # Calculate statistics
        accuracies = [r['accuracy'] for r in results]
        latencies = [r['latency_ms'] for r in results]
        
        final_accuracy = accuracies[-1] if accuracies else 0
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        return {
            'total_iterations': len(results),
            'final_accuracy': final_accuracy,
            'average_accuracy': avg_accuracy,
            'average_latency_ms': avg_latency,
            'iterations': results
        }
    
    def save_results(
        self,
        results: Dict[str, Any],
        output_path: Path
    ):
        """Save results to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {output_path}")
    
    def shutdown(self):
        """Shutdown Ray if initialized."""
        if self.use_ray and ray.is_initialized():
            ray.shutdown()
            logger.info("Ray shutdown complete")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Distributed benchmark executor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=500,
        help="Total iterations (default: 500)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of workers (default: 10)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size (default: 10)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run only 10 iterations for testing"
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="Force serial execution (no Ray)"
    )
    parser.add_argument(
        "--resume",
        type=int,
        default=None,
        help="Resume from iteration N"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path"
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
    
    # Determine iterations
    iterations = 10 if args.dry_run else args.iterations
    
    # Initialize executor
    executor = DistributedExecutor(
        num_workers=args.workers,
        batch_size=args.batch_size,
        use_ray=not args.serial
    )
    
    try:
        start_time = time.time()
        
        # Run iterations
        if executor.use_ray:
            results = executor.run_distributed(iterations, args.resume)
        else:
            results = executor.run_serial(iterations, args.resume or 1)
        
        duration = time.time() - start_time
        
        # Aggregate results
        aggregated = executor.aggregate_results(results)
        aggregated['duration_seconds'] = duration
        aggregated['mode'] = 'distributed' if executor.use_ray else 'serial'
        aggregated['num_workers'] = args.workers
        
        # Print summary
        print("\n" + "="*70)
        print("DISTRIBUTED EXECUTION RESULTS")
        print("="*70)
        print(f"Mode: {aggregated['mode']}")
        print(f"Workers: {args.workers}")
        print(f"Iterations: {aggregated['total_iterations']}")
        print(f"Duration: {duration:.2f}s")
        print(f"Final Accuracy: {aggregated['final_accuracy']:.4f}")
        print(f"Average Accuracy: {aggregated['average_accuracy']:.4f}")
        print(f"Average Latency: {aggregated['average_latency_ms']:.2f}ms")
        print("="*70 + "\n")
        
        # Save results
        if args.output:
            output_path = Path(args.output)
        else:
            script_dir = Path(__file__).parent
            repo_root = script_dir.parent
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = repo_root / "logs" / "benchmarks" / f"distributed_{timestamp}.json"
        
        executor.save_results(aggregated, output_path)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1
    finally:
        executor.shutdown()


if __name__ == "__main__":
    sys.exit(main())
