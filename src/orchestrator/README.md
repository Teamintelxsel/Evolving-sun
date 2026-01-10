# Benchmark Orchestrator

The Benchmark Orchestrator is a comprehensive benchmarking system for Evolving-sun that executes multiple benchmark suites with full provenance tracking and reproducibility guarantees.

## Features

- **Suite Execution**: Support for SWE-Bench, GPQA, and KEGG benchmarks
- **Sharding**: Distributes large benchmarks across multiple shards for parallel execution
- **Retry Logic**: Exponential backoff retry mechanism (30s → 120s) for resilient execution
- **Deterministic Seeds**: SHA256-based seed generation for reproducible results
- **Provenance Tracking**: Comprehensive logging of:
  - Git commit SHA, branch, and remote URL
  - OS version and Python environment details
  - Library versions (PyYAML, Biopython, etc.)
  - Dataset revisions (GPQA)
  - Docker image digests (SWE-Bench)
  - KEGG API endpoints
- **Watermarked Results**: All outputs include timestamp and commit watermarks
- **Timeout Handling**: Per-task and per-suite timeout enforcement

## Usage

### Command Line

Run all benchmarks defined in `tasks.yaml`:

```bash
python src/orchestrator/bench_orchestrator.py
```

Specify a custom tasks file:

```bash
python src/orchestrator/bench_orchestrator.py --tasks-file my_tasks.yaml
```

Customize output directory and filename:

```bash
python src/orchestrator/bench_orchestrator.py \
  --output-dir ./results \
  --output-name custom_benchmark_results.json
```

### Python API

```python
from src.orchestrator import BenchmarkOrchestrator

# Initialize orchestrator
orchestrator = BenchmarkOrchestrator(
    tasks_file="tasks.yaml",
    output_dir="logs/benchmarks"
)

# Execute all suites
results = orchestrator.execute_all_suites()

# Print summary
orchestrator.print_summary(results)

# Save results
orchestrator.save_results(results)
```

## Configuration

Benchmarks are configured via `tasks.yaml` in the repository root. See the example configuration below:

```yaml
suites:
  swebench:
    dataset: "Verified"
    shards: 2
    shard_size: 25
    num_workers: 1
    image_digest: "sha256:..."
    timeout: 3600
    
  gpqa:
    variant: "diamond"
    self_consistency_k: 10
    limit: 500
    dataset_revision: "main"
    timeout: 1800
    
  kegg:
    pathway: "ko01100"
    kegg_url: "https://rest.kegg.jp"
    timeout: 600
```

### Suite Configuration Options

#### SWE-Bench
- `dataset`: Dataset variant (e.g., "Verified")
- `shards`: Number of shards to split tasks across
- `shard_size`: Number of tasks per shard
- `num_workers`: Number of parallel workers per shard
- `image_digest`: Docker image SHA256 digest
- `timeout`: Per-shard timeout in seconds

#### GPQA
- `variant`: GPQA variant (e.g., "diamond")
- `self_consistency_k`: Number of samples for self-consistency
- `limit`: Maximum number of questions to evaluate
- `dataset_revision`: Dataset version/revision to use
- `timeout`: Total timeout in seconds

#### KEGG
- `pathway`: KEGG pathway identifier (e.g., "ko01100")
- `kegg_url`: KEGG REST API base URL
- `timeout`: Timeout in seconds

## Output Format

The orchestrator produces watermarked JSON files with the following structure:

```json
{
  "watermark": "Evolving-sun Benchmark Results | 2026-01-10 03:26:26 UTC | Commit: 07934c58",
  "provenance": {
    "timestamp": "2026-01-10T03:26:26.657922",
    "environment": {
      "os": "Linux",
      "python_version": "3.12.3",
      ...
    },
    "repository": {
      "commit_sha": "07934c58...",
      "branch": "main",
      "remote_url": "https://github.com/..."
    },
    "libraries": {
      "pyyaml": "6.0.1",
      ...
    }
  },
  "execution": {
    "start_time": "2026-01-10T03:26:26.688712",
    "end_time": "2026-01-10T03:26:30.690017",
    "tasks_file": "tasks.yaml"
  },
  "suites": {
    "swebench": {
      "suite": "swebench",
      "dataset": "Verified",
      "shard_results": [...],
      "status": "completed",
      ...
    },
    ...
  }
}
```

## CI Integration

The orchestrator is integrated into the Weekly Benchmarks GitHub Actions workflow:

```yaml
- name: Run orchestrated benchmarks
  run: |
    python src/orchestrator/bench_orchestrator.py --tasks-file tasks.yaml
```

Results are:
1. Committed to the repository in `logs/benchmarks/`
2. Uploaded as workflow artifacts with 90-day retention
3. Summarized in the workflow step summary with watermark and status

## Deterministic Seeds

Seeds are generated deterministically using SHA256 hashing:

```python
seed = hash(suite_name + "_shard_" + shard_idx) % 2^31
```

This ensures:
- Reproducibility across runs
- Different seeds for different shards
- Deterministic behavior for debugging

## Retry Logic

Failed executions are retried with exponential backoff:

1. First attempt: immediate
2. Retry 1: 30 seconds wait
3. Subsequent retries: double the wait time (capped at 120s)

Maximum of 1 retry (2 total attempts) by default.

## Extending the Orchestrator

To add a new benchmark suite:

1. Add suite configuration to `tasks.yaml`
2. Implement `_execute_<suite>_suite()` method in `BenchmarkOrchestrator`
3. Add suite execution in `execute_all_suites()` method
4. Update suite summary in `print_summary()` method

Example:

```python
def _execute_mybench_suite(self, suite_config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MyBench benchmark suite."""
    seed = self._get_deterministic_seed("mybench", 0)
    
    results = {
        "suite": "mybench",
        "seed": seed,
        "status": "running",
        "start_time": datetime.now().isoformat()
    }
    
    # Execute benchmark with retry
    success, output, error = self._execute_with_retry(
        self._simulate_mybench_execution,
        max_retries=1,
        seed=seed
    )
    
    results["end_time"] = datetime.now().isoformat()
    results["status"] = "completed" if success else "failed"
    
    if success:
        results["results"] = output
    else:
        results["error"] = error
    
    return results
```

## License

This orchestrator is part of the Evolving-sun project and follows the same MIT License.
