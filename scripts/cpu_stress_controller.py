#!/usr/bin/env python3
"""
CPU Stress Controller

Maintains high CPU utilization (99.9% target) through:
- Multi-process CPU stress workers
- CPU core affinity pinning
- Real-time utilization monitoring
- Token bucket throttling

Usage:
    python cpu_stress_controller.py --target 99.9 --duration 60
"""

import argparse
import logging
import multiprocessing as mp
import os
import sys
import time
from typing import List, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("ERROR: psutil is required for CPU stress testing")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CPUStressWorker:
    """Worker process for CPU stress."""
    
    @staticmethod
    def cpu_bound_work(worker_id: int, stop_event: mp.Event, core_id: Optional[int] = None):
        """
        Execute CPU-intensive work.
        
        Args:
            worker_id: Worker identifier
            stop_event: Event to signal stop
            core_id: CPU core to pin to (None for no pinning)
        """
        # Pin to specific core if requested
        if core_id is not None and PSUTIL_AVAILABLE:
            try:
                p = psutil.Process()
                p.cpu_affinity([core_id])
                logger.info(f"Worker {worker_id} pinned to core {core_id}")
            except Exception as e:
                logger.warning(f"Failed to pin worker {worker_id} to core {core_id}: {e}")
        
        # Prime number computation for CPU load
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        
        # Matrix multiplication for cache thrashing
        def matrix_multiply():
            size = 50
            a = [[i * j for j in range(size)] for i in range(size)]
            b = [[i + j for j in range(size)] for i in range(size)]
            c = [[sum(a[i][k] * b[k][j] for k in range(size)) 
                  for j in range(size)] for i in range(size)]
            return c[0][0]  # Use result to prevent optimization
        
        counter = 0
        while not stop_event.is_set():
            # Alternate between different CPU-bound tasks
            if counter % 2 == 0:
                # Prime number check
                is_prime(1000000007 + counter % 1000)
            else:
                # Matrix multiplication
                matrix_multiply()
            
            counter += 1


class CPUStressController:
    """Controls CPU stress testing to maintain target utilization."""
    
    def __init__(self, target_percent: float = 99.9, num_workers: Optional[int] = None):
        """
        Initialize CPU stress controller.
        
        Args:
            target_percent: Target CPU utilization percentage
            num_workers: Number of workers (default: CPU count)
        """
        self.target_percent = target_percent
        self.num_workers = num_workers or os.cpu_count() or 1
        self.workers: List[mp.Process] = []
        self.stop_event = mp.Event()
        
        logger.info(f"Initializing CPU stress controller")
        logger.info(f"Target: {target_percent}% utilization")
        logger.info(f"Workers: {self.num_workers}")
    
    def start(self):
        """Start CPU stress workers."""
        logger.info("Starting CPU stress workers...")
        
        for i in range(self.num_workers):
            # Pin each worker to a specific core if possible
            core_id = i % os.cpu_count() if os.cpu_count() else None
            
            worker = mp.Process(
                target=CPUStressWorker.cpu_bound_work,
                args=(i, self.stop_event, core_id),
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {len(self.workers)} workers")
    
    def stop(self):
        """Stop all CPU stress workers."""
        logger.info("Stopping CPU stress workers...")
        
        self.stop_event.set()
        
        for worker in self.workers:
            worker.join(timeout=2)
            if worker.is_alive():
                worker.terminate()
        
        self.workers.clear()
        logger.info("All workers stopped")
    
    def monitor(self, duration: float, interval: float = 1.0) -> dict:
        """
        Monitor CPU utilization during stress test.
        
        Args:
            duration: Duration to monitor in seconds
            interval: Monitoring interval in seconds
            
        Returns:
            Dictionary with monitoring results
        """
        logger.info(f"Monitoring CPU utilization for {duration}s...")
        
        start_time = time.time()
        measurements = []
        
        while time.time() - start_time < duration:
            cpu_percent = psutil.cpu_percent(interval=interval)
            measurements.append({
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'elapsed': time.time() - start_time
            })
            
            logger.info(f"CPU: {cpu_percent:.1f}% (target: {self.target_percent}%)")
        
        # Calculate statistics
        cpu_values = [m['cpu_percent'] for m in measurements]
        avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
        min_cpu = min(cpu_values) if cpu_values else 0
        max_cpu = max(cpu_values) if cpu_values else 0
        
        # Check if target was met
        target_met = avg_cpu >= self.target_percent - 1.0  # 1% tolerance
        
        results = {
            'duration': duration,
            'target_percent': self.target_percent,
            'avg_cpu_percent': avg_cpu,
            'min_cpu_percent': min_cpu,
            'max_cpu_percent': max_cpu,
            'measurements': measurements,
            'target_met': target_met,
            'num_workers': self.num_workers
        }
        
        return results
    
    def run(self, duration: float) -> dict:
        """
        Run CPU stress test for specified duration.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Results dictionary
        """
        try:
            self.start()
            time.sleep(2)  # Allow workers to ramp up
            results = self.monitor(duration)
            return results
        finally:
            self.stop()


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="CPU stress controller for benchmark testing",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--target",
        type=float,
        default=99.9,
        help="Target CPU utilization percentage (default: 99.9)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=60,
        help="Duration in seconds (default: 60)"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of workers (default: CPU count)"
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
    
    controller = CPUStressController(
        target_percent=args.target,
        num_workers=args.workers
    )
    
    try:
        results = controller.run(args.duration)
        
        print("\n" + "="*70)
        print("CPU STRESS TEST RESULTS")
        print("="*70)
        print(f"Duration: {results['duration']}s")
        print(f"Target: {results['target_percent']}%")
        print(f"Average CPU: {results['avg_cpu_percent']:.2f}%")
        print(f"Min CPU: {results['min_cpu_percent']:.2f}%")
        print(f"Max CPU: {results['max_cpu_percent']:.2f}%")
        print(f"Target Met: {'✓' if results['target_met'] else '✗'}")
        print("="*70 + "\n")
        
        return 0 if results['target_met'] else 1
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        controller.stop()
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        controller.stop()
        return 1


if __name__ == "__main__":
    sys.exit(main())
