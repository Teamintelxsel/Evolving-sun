# Scripts Documentation

This directory contains utility scripts for the Evolving-sun system.

## Available Scripts

### import_conversations.py

Import plaintext or markdown conversation exports into the `docs/conversations/` directory.

**Usage:**

```bash
# Basic import
python scripts/import_conversations.py conversation.txt

# Custom output name
python scripts/import_conversations.py chat.txt --output-name meeting_notes

# Specify format
python scripts/import_conversations.py discussion.txt --format markdown

# Overwrite existing file
python scripts/import_conversations.py chat.txt --overwrite
```

**Arguments:**

- `input_file`: Path to the conversation file to import (required)
- `--output-name`: Custom output filename without extension (optional)
- `--format`: Output format - `markdown` (default) or `plaintext`
- `--overwrite`: Overwrite existing file if it exists

**Features:**

- Automatically adds metadata headers (timestamp, source file)
- Preserves original formatting
- Validates input files
- Creates output directory if needed

**Example Output:**

```markdown
---
title: Imported Conversation
source: /path/to/original.txt
imported_at: 2026-01-10 01:15:00
---

# Conversation

[Original conversation content here]
```

### run_benchmarks.py

Unified benchmark runner for executing and archiving benchmark results.

**Usage:**

```bash
# Run all benchmarks
python scripts/run_benchmarks.py

# Run specific benchmark
python scripts/run_benchmarks.py --benchmark performance

# Custom output directory
python scripts/run_benchmarks.py --output-dir /custom/path

# Print results without saving
python scripts/run_benchmarks.py --no-save
```

**Arguments:**

- `--benchmark`: Benchmark to run - `performance`, `accuracy`, `security`, or `all` (default: all)
- `--output-dir`: Custom output directory for results (default: logs/benchmarks)
- `--no-save`: Print results without saving to file

**Available Benchmarks:**

1. **Performance Benchmark**
   - Response time
   - Throughput (requests per second)
   - CPU and memory usage
   - Latency percentiles (p50, p95, p99)

2. **Accuracy Benchmark**
   - Precision, recall, F1 score
   - Overall accuracy
   - False positive/negative rates
   - Test case results

3. **Security Benchmark**
   - Vulnerability scanning
   - Dependency checks
   - Code analysis results

**Output Format:**

Results are saved as JSON files with timestamps:

```
logs/benchmarks/benchmark_all_20260110_011538.json
```

**Example Output:**

```json
[
  {
    "benchmark_name": "performance",
    "timestamp": "2026-01-10T01:15:38.123456",
    "metrics": {
      "response_time_ms": 45.2,
      "throughput_rps": 1250.5,
      "cpu_usage_percent": 23.4,
      "memory_usage_mb": 512.8
    },
    "status": "passed",
    "duration_seconds": 0.001
  }
]
```

## Integration with CI/CD

Both scripts are designed to work seamlessly with CI/CD pipelines:

- **import_conversations.py**: Can be used in workflows to automatically import conversation logs
- **run_benchmarks.py**: Integrated with the weekly benchmark GitHub Actions workflow

See `.github/workflows/weekly-benchmarks.yml` for CI integration examples.

## Development

When adding new scripts:

1. Include comprehensive help text and docstrings
2. Use argparse for CLI arguments
3. Provide meaningful error messages
4. Follow the existing code structure
5. Add documentation here
6. Make scripts executable: `chmod +x scripts/yourscript.py`
