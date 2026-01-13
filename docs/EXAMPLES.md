# Examples

This directory contains usage examples for the Evolving-sun utilities.

## Example 1: Running Benchmarks

Run all benchmarks and save results:

```bash
python scripts/run_benchmarks.py
```

Run a specific benchmark:

```bash
python scripts/run_benchmarks.py --benchmark performance
```

Run benchmarks without saving (for testing):

```bash
python scripts/run_benchmarks.py --no-save
```

## Example 2: Importing Conversations

Import a conversation file:

```bash
python scripts/import_conversations.py path/to/conversation.txt
```

Import with custom name:

```bash
python scripts/import_conversations.py discussion.md --output-name team_meeting
```

## Example 3: Using Structured Logging

```python
from src.utils import get_logger, log_benchmark_event

# Get a logger for evolution tracking
logger = get_logger("evolution")
logger.info("System upgrade initiated")
logger.info("Upgrading to version 1.1", metadata={"from": "1.0", "to": "1.1"})

# Log a structured event
logger.log_event("version_change", {
    "previous_version": "1.0",
    "new_version": "1.1",
    "timestamp": "2026-01-10T01:00:00"
})

# Use convenience functions
log_benchmark_event("performance_test", {
    "latency_ms": 42.5,
    "throughput_rps": 1200,
    "status": "passed"
})
```

## Example 4: Complete Workflow

This example shows a complete workflow using all components:

```python
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
    # Initialize loggers
    evolution_logger = get_logger("evolution")
    security_logger = get_logger("security")
    
    # Log system startup
    evolution_logger.info("System starting up")
    log_evolution_event("system_start", {"version": "1.0"})
    
    # Simulate a security scan
    security_logger.info("Running security scan")
    scan_results = {
        "vulnerabilities": 0,
        "warnings": 3,
        "scan_duration_seconds": 45.2
    }
    log_security_event("security_scan_complete", scan_results)
    
    # Run benchmarks
    evolution_logger.info("Running performance benchmarks")
    benchmark_results = {
        "latency_ms": 42.1,
        "throughput_rps": 1250,
        "status": "passed"
    }
    log_benchmark_event("performance_benchmark", benchmark_results)
    
    # Log completion
    evolution_logger.info("Workflow completed successfully")
    log_evolution_event("workflow_complete", {
        "duration_seconds": 120,
        "status": "success"
    })

if __name__ == "__main__":
    main()
```

Save this as `examples/complete_workflow.py` and run:

```bash
python examples/complete_workflow.py
```

This will create log entries in:
- `logs/evolution/evolution_YYYYMMDD.log`
- `logs/evolution/events_YYYYMMDD.json`
- `logs/security/security_YYYYMMDD.log`
- `logs/security/events_YYYYMMDD.json`
- `logs/benchmarks/benchmarks_YYYYMMDD.log`
- `logs/benchmarks/events_YYYYMMDD.json`

## Example 5: CI/CD Integration

The weekly benchmark workflow runs automatically every Sunday. You can also trigger it manually:

1. Go to Actions tab in GitHub
2. Select "Weekly Benchmark Archive"
3. Click "Run workflow"

The workflow will:
- Run all benchmarks
- Save results to `logs/benchmarks/`
- Archive results as GitHub artifacts
- Commit results to the repository
