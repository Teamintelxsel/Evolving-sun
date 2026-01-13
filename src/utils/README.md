# Utilities Documentation

This directory contains utility modules for the Evolving-sun system.

## Modules

### logging_utils.py

Structured logging utilities for different subsystems.

#### StructuredLogger

A logging class that provides structured logging capabilities with support for different log categories.

**Categories:**
- `evolution`: Track system evolution and changes
- `benchmarks`: Log benchmark execution and results
- `security`: Security-related logs and events
- `agent-activity`: Agent operation logs

**Usage:**

```python
from src.utils import get_logger, log_benchmark_event

# Get a logger for a specific category
logger = get_logger("benchmarks")

# Log simple messages
logger.info("Starting benchmark run")
logger.warning("Performance degradation detected")
logger.error("Benchmark failed", metadata={"error": "timeout"})

# Log structured events
log_benchmark_event("benchmark_complete", {
    "name": "performance_test",
    "duration": 45.2,
    "status": "passed"
})
```

**Event Logging:**

Events are logged as JSON lines to enable easy parsing and analysis:

```python
logger.log_event("security_scan", {
    "scanner": "dependency_check",
    "vulnerabilities_found": 0,
    "warnings": 3
})
```

This creates entries in both:
- Text log: `logs/{category}/{category}_YYYYMMDD.log`
- JSON log: `logs/{category}/events_YYYYMMDD.json`

#### Convenience Functions

Quick logging functions for each category:

```python
from src.utils import (
    log_evolution_event,
    log_benchmark_event,
    log_security_event,
    log_agent_event
)

# Log events directly without creating logger instances
log_evolution_event("version_upgrade", {"from": "v1.0", "to": "v1.1"})
log_security_event("scan_complete", {"issues": 0})
```

## Best Practices

1. **Use appropriate log levels:**
   - `debug()`: Detailed diagnostic information
   - `info()`: General informational messages
   - `warning()`: Warning messages for potentially problematic situations
   - `error()`: Error messages for failures

2. **Include metadata:**
   ```python
   logger.error("Process failed", metadata={
       "process_id": 1234,
       "exit_code": 1,
       "duration": 120.5
   })
   ```

3. **Use structured events for important milestones:**
   ```python
   logger.log_event("benchmark_milestone", {
       "benchmark": "accuracy",
       "score": 0.95,
       "improvement": 0.05
   })
   ```

4. **Choose the right category:**
   - Use `evolution` for system changes and version tracking
   - Use `benchmarks` for performance and test results
   - Use `security` for security scans and vulnerability reports
   - Use `agent-activity` for AI agent operations and decisions
