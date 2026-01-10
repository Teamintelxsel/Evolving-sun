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

Legacy benchmark runner for executing and archiving benchmark results.

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

### unified_runner.py

Unified runner for all benchmark harnesses (legacy + new).

**Usage:**

```bash
# Run all benchmarks
python scripts/unified_runner.py

# Run specific benchmark categories
python scripts/unified_runner.py --gpqa --kegg
python scripts/unified_runner.py --swe-bench --swe-max-tasks 5

# Customize individual benchmarks
python scripts/unified_runner.py --all --gpqa-limit 100 --kegg-pathways 15
```

**Arguments:**

- `--all`: Run all benchmarks (default if no specific benchmarks selected)
- `--legacy`: Run legacy benchmarks
- `--swe-bench`: Run SWE-bench Verified
- `--gpqa`: Run GPQA Diamond
- `--kegg`: Run KEGG KGML
- `--swe-max-tasks`: Maximum tasks for SWE-bench (default: 10)
- `--swe-workers`: Workers for SWE-bench (default: 1)
- `--gpqa-limit`: Examples for GPQA (default: 500)
- `--kegg-pathways`: Pathways for KEGG (default: 10)
- `--output-dir`: Custom output directory (default: logs/benchmarks)

**Output:**

Creates a `unified_summary.json` file with execution results for all benchmarks.

### swe_run.py

SWE-bench Verified benchmark runner for software engineering task evaluation.

**Usage:**

```bash
# Run with defaults
python scripts/swe_run.py

# Customize execution
python scripts/swe_run.py --max-tasks 20 --num-workers 2
python scripts/swe_run.py --dataset verified --image sweagent/swe-agent@sha256:abc123...
```

**Arguments:**

- `--dataset`: Dataset split (default: verified)
- `--image`: Docker image name (use digest for reproducibility)
- `--num-workers`: Parallel workers, 1-2 for CI (default: 1)
- `--max-tasks`: Maximum tasks to run (default: 10)
- `--output-dir`: Output directory (default: logs/benchmarks)

**Features:**

- Integrates with vendor/SWE-bench submodule
- Falls back to simulation mode if vendor script unavailable
- Captures provenance: commit SHA, image digest, dataset config
- Watermarked logging for result integrity

**Output:**

```
logs/benchmarks/swe_results.json
```

### gpqa_run.py

GPQA Diamond benchmark runner for graduate-level science questions.

**Usage:**

```bash
# Run with defaults (500 examples)
python scripts/gpqa_run.py

# Limit examples
python scripts/gpqa_run.py --limit 100
```

**Arguments:**

- `--limit`: Maximum examples to process (default: 500)
- `--output-dir`: Output directory (default: logs/benchmarks)

**Features:**

- Loads GPQA diamond dataset via HuggingFace datasets library
- Falls back to simulation mode if datasets library not installed
- Baseline tally mode for initial runs (no model inference)
- Watermarked logging with dataset version hash

**Output:**

```
logs/benchmarks/gpqa_results.json
```

### bio_kegg_run.py

KEGG KGML biological pathway benchmark runner.

**Usage:**

```bash
# Run with defaults (10 human pathways)
python scripts/bio_kegg_run.py

# Customize organism and pathway count
python scripts/bio_kegg_run.py --organism hsa --max-pathways 20
python scripts/bio_kegg_run.py --organism mmu --max-pathways 5  # Mouse pathways
```

**Arguments:**

- `--organism`: Organism code (default: hsa for human)
- `--max-pathways`: Maximum pathways to process (default: 10)
- `--output-dir`: Output directory (default: logs/benchmarks)

**Features:**

- Fetches KGML via KEGG REST API (http://rest.kegg.jp)
- Parses pathway elements (entries, relations, reactions)
- Falls back to simulation when API unavailable
- Rate limiting to be respectful to KEGG API
- Watermarked logging with API endpoint provenance

**Output:**

```
logs/benchmarks/kegg_results.json
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

## Watermarked Logging

All new benchmark scripts use secure watermarked logging via `src/utils/secure_logging.py`:

**Features:**
- Cryptographic integrity hashes for result verification
- Provenance tracking (commit SHA, timestamps, configurations)
- Metadata preservation for reproducibility
- Tamper detection via `verify_log_integrity()`

**Example Watermarked Output:**

```json
{
  "timestamp": "2026-01-10T02:00:00.000000",
  "data": {
    "benchmark": "gpqa-diamond",
    "metrics": {...}
  },
  "provenance": {
    "commit_sha": "abc123...",
    "dataset": "Idavidrein/gpqa",
    "script": "gpqa_run.py"
  },
  "metadata": {
    "logged_by": "secure_logging.watermark_log",
    "version": "1.0"
  },
  "integrity_hash": "sha256:def456..."
}
```

## Integration with CI/CD

All scripts are designed to work seamlessly with CI/CD pipelines:

- **import_conversations.py**: Automatically import conversation logs
- **run_benchmarks.py**: Legacy benchmarks in weekly workflow
- **unified_runner.py**: Single command for all benchmarks
- **swe_run.py, gpqa_run.py, bio_kegg_run.py**: Individual harnesses with simulation fallback

See `.github/workflows/weekly-benchmarks.yml` for CI integration examples.

## Development

When adding new scripts:

1. Include comprehensive help text and docstrings
2. Use argparse for CLI arguments
3. Provide meaningful error messages
4. Follow the existing code structure
5. Add documentation here
6. Make scripts executable: `chmod +x scripts/yourscript.py`
