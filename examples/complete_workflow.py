#!/usr/bin/env python3
"""Example workflow demonstrating all Evolving-sun utilities."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import (
    get_logger,
    log_evolution_event,
    log_benchmark_event,
    log_security_event
)

def main():
    """Run a complete example workflow."""
    print("Starting Evolving-sun Example Workflow")
    print("=" * 60)
    
    # Initialize loggers
    evolution_logger = get_logger("evolution")
    security_logger = get_logger("security")
    
    # Log system startup
    print("\n1. System Startup")
    evolution_logger.info("System starting up")
    log_evolution_event("system_start", {"version": "1.0"})
    
    # Simulate a security scan
    print("\n2. Security Scan")
    security_logger.info("Running security scan")
    scan_results = {
        "vulnerabilities": 0,
        "warnings": 3,
        "scan_duration_seconds": 45.2
    }
    log_security_event("security_scan_complete", scan_results)
    security_logger.info("Security scan completed", metadata=scan_results)
    
    # Run benchmarks
    print("\n3. Performance Benchmarks")
    evolution_logger.info("Running performance benchmarks")
    benchmark_results = {
        "latency_ms": 42.1,
        "throughput_rps": 1250,
        "status": "passed"
    }
    log_benchmark_event("performance_benchmark", benchmark_results)
    
    # Log completion
    print("\n4. Workflow Complete")
    evolution_logger.info("Workflow completed successfully")
    log_evolution_event("workflow_complete", {
        "duration_seconds": 120,
        "status": "success"
    })
    
    print("\n" + "=" * 60)
    print("Workflow completed! Check logs/ directory for output.")
    print("\nLog files created:")
    print("  - logs/evolution/evolution_*.log")
    print("  - logs/evolution/events_*.json")
    print("  - logs/security/security_*.log")
    print("  - logs/security/events_*.json")
    print("  - logs/benchmarks/benchmarks_*.log")
    print("  - logs/benchmarks/events_*.json")

if __name__ == "__main__":
    main()
