# Benchmark Harness Integration

This directory contains integration scripts for real benchmark harnesses including SWE-Bench Verified, GPQA, and KEGG pathway analysis.

## Available Benchmarks

### 1. SWE-bench Verified (`swe_run.py`)

Integration with SWE-bench Verified via Docker for software engineering benchmarks.

**Usage:**
```bash
python scripts/swe_run.py \
  --dataset "princeton-nlp/SWE-bench_Verified" \
  --image "sha256:abc123..." \
  --max-tasks 10 \
  --num-workers 2
```

**Features:**
- Provenance tracking (commit SHA, image digest, dataset config, seeds)
- Watermarked logging for data integrity
- Docker-based evaluation
- Configurable task limits for CI

**Requirements:**
- Git submodule: `vendor/SWE-bench` (initialized automatically)
- Docker (for actual evaluation)

### 2. GPQA (`gpqa_run.py`)

Integration with Graduate-Level Google-Proof Q&A benchmark via HuggingFace datasets.

**Usage:**
```bash
python scripts/gpqa_run.py \
  --split diamond \
  --limit 500
```

**Features:**
- Baseline tallying (no model inference initially)
- Dataset version hashing for provenance
- Watermarked logging
- Configurable question limits

**Requirements:**
- `datasets` library (install via `pip install datasets`)

### 3. KEGG Pathway Analysis (`bio_kegg_run.py`)

Integration with KEGG database via Biopython KGML/REST API.

**Usage:**
```bash
python scripts/bio_kegg_run.py \
  --pathways 00010 00020 \
  --organism hsa \
  --fetch-kgml
```

**Features:**
- KEGG REST API integration
- Optional KGML format parsing
- Multiple pathway analysis
- Watermarked logging

**Requirements:**
- `biopython` library (install via `pip install biopython`)
- Network access to KEGG REST API

## Unified Benchmark Runner

The updated `run_benchmarks.py` script now integrates all benchmarks:

```bash
# Run all benchmarks
python scripts/run_benchmarks.py --benchmark all

# Run specific benchmark
python scripts/run_benchmarks.py --benchmark gpqa
python scripts/run_benchmarks.py --benchmark swe-bench
python scripts/run_benchmarks.py --benchmark kegg
```

## Provenance and Watermarking

All benchmark results are watermarked using SHA-256 cryptographic hashing for data integrity:

```python
from src.utils.secure_logging import watermark_log, verify_watermark

# Write watermarked results
watermark_log(
    filepath="logs/benchmarks/results.json",
    data=results,
    provenance={"commit_sha": "abc123", "timestamp": "..."}
)

# Verify watermark
is_valid = verify_watermark("logs/benchmarks/results.json")
```

### Provenance Information

Each benchmark result includes:
- **commit_sha**: Git commit SHA at time of execution
- **timestamp**: ISO 8601 timestamp
- **dataset_config**: Dataset configuration/version
- **script_version**: Version of the benchmark script
- **Additional metadata**: Specific to each benchmark type

## CI Integration

The weekly CI workflow (`.github/workflows/weekly-benchmarks.yml`) now:
- Initializes SWE-bench submodule
- Installs dependencies from `requirements.txt`
- Runs all benchmarks weekly
- Archives results as artifacts (90-day retention)
- Commits verified results to repository

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize submodules
git submodule update --init --recursive
```

## Result Files

All benchmark results are saved to `logs/benchmarks/` with watermarked JSON format:

```json
{
  "data": { /* benchmark results */ },
  "provenance": { /* provenance metadata */ },
  "watermark": "sha256_hash...",
  "watermark_algorithm": "sha256",
  "created_at": "2026-01-10T..."
}
```

## Notes

- **SWE-bench**: Runs in simulation mode until Docker environment is fully configured
- **GPQA**: Falls back to simulation if `datasets` library not available
- **KEGG**: Requires network access to KEGG REST API; may be skipped in restricted environments
- All benchmarks support custom output paths via `--output` flag
