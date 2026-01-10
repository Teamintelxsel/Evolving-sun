# Evolving Sun - Benchmark Harness Framework

A unified framework for running and archiving results from multiple AI/ML benchmark suites with secure logging and CI automation.

## Overview

This repository integrates three major benchmark harnesses:
- **SWE-Bench**: Software engineering tasks and code generation
- **GPQA**: Graduate-level Q&A across multiple domains
- **KEGG**: Biological pathway understanding and analysis

## Structure

```
.
├── .github/
│   └── workflows/
│       └── weekly-benchmarks.yml   # Weekly CI workflow
├── src/
│   └── utils/
│       └── secure_logging.py       # Watermarked logging utilities
├── scripts/
│   ├── swe_run.py                  # SWE-Bench harness
│   ├── gpqa_run.py                 # GPQA harness
│   ├── bio_kegg_run.py             # KEGG harness
│   └── run_benchmarks.py           # Unified runner
├── vendor/
│   └── SWE-bench/                  # Git submodule
├── logs/
│   └── benchmarks/                 # Results output directory
└── requirements.txt                # Python dependencies
```

## Setup

### Prerequisites
- Python 3.11+
- Git with submodule support
- Docker (for SWE-Bench)

### Installation

1. Clone the repository with submodules:
```bash
git clone --recursive https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize submodules (if not cloned with --recursive):
```bash
git submodule update --init --recursive
```

## Usage

### Individual Benchmarks

#### GPQA (Graduate-Level Q&A)
```bash
python scripts/gpqa_run.py --max_samples 100
```

Options:
- `--split`: Dataset split (diamond, main, extended) [default: diamond]
- `--max_samples`: Maximum samples to evaluate
- `--output`: Output path for results

#### KEGG (Biological Pathways)
```bash
python scripts/bio_kegg_run.py --pathways hsa00010 hsa00020
```

Options:
- `--pathways`: KEGG pathway IDs to analyze
- `--kgml`: Path to KGML file for parsing
- `--output`: Output path for results

#### SWE-Bench (Software Engineering)
```bash
python scripts/swe_run.py --image sweagent/swe-agent:latest --max_tasks 10
```

Options:
- `--dataset`: Dataset split/config [default: Verified]
- `--image`: Docker image (required)
- `--num_workers`: Parallel workers (1-2)
- `--max_tasks`: Maximum tasks to run
- `--output`: Output path for results

### Unified Runner

Run multiple benchmarks with a single command:

```bash
python scripts/run_benchmarks.py --benchmarks gpqa kegg
```

Options:
- `--benchmarks`: Which benchmarks to run (swe, gpqa, kegg, all)
- `--output-dir`: Output directory for results
- `--archive`: Archive results with timestamp
- `--swe-image`: Docker image for SWE-Bench
- `--swe-max-tasks`: Max tasks for SWE-Bench
- `--gpqa-max-samples`: Max samples for GPQA
- `--kegg-pathways`: KEGG pathway IDs

## CI/CD

### Weekly Benchmark Runs

The repository includes a GitHub Actions workflow that runs benchmarks weekly:
- **Schedule**: Every Monday at 00:00 UTC
- **Manual Trigger**: Via workflow_dispatch
- **Benchmarks**: GPQA and KEGG (by default)
- **Results**: Archived as artifacts for 90 days

### Workflow Features

✅ **Security Audit Fixes Applied:**
- Minimal permissions (read-only by default)
- Pinned action versions for reproducibility
- Concurrency control to prevent resource waste
- Path filters for efficient PR builds
- Dependency caching for faster builds

### Manual Workflow Trigger

Go to Actions → Weekly Benchmark CI → Run workflow

Parameters:
- `benchmarks`: Comma-separated list (swe,gpqa,kegg or all)
- `max_samples`: Maximum samples for GPQA

## Result Format

All results are written with watermarked logging for verification:

```json
{
  "watermark": {
    "timestamp": "2026-01-10T00:00:00Z",
    "content_hash": "sha256...",
    "framework": "evolving-sun-benchmarks",
    "version": "1.0.0"
  },
  "data": {
    "status": "success",
    "accuracy": 0.75,
    ...
  }
}
```

## Development

### Adding New Benchmarks

1. Create a new script in `scripts/` following the pattern
2. Import and use `src.utils.secure_logging.watermark_log`
3. Add to the unified runner in `scripts/run_benchmarks.py`
4. Update CI workflow if needed

### Testing

Test individual components:
```bash
# Test GPQA with small sample
python scripts/gpqa_run.py --max_samples 5

# Test KEGG with one pathway
python scripts/bio_kegg_run.py --pathways hsa00010

# Test unified runner
python scripts/run_benchmarks.py --benchmarks gpqa --gpqa-max-samples 5
```

## License

This framework is provided as-is for benchmark evaluation purposes. Individual benchmark datasets and tools may have their own licenses:
- SWE-Bench: MIT License (see vendor/SWE-bench/)
- GPQA: Check dataset license on HuggingFace
- KEGG: Academic use - see KEGG licensing terms

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing patterns
- New benchmarks include watermarked logging
- CI workflows maintain security best practices
- Documentation is updated

## Contact

For issues and questions, please use the GitHub issue tracker.
