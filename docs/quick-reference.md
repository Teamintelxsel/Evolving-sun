# Quick Reference Guide

## Installation

```bash
git clone --recursive https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun
pip install -r requirements.txt
```

## Running Benchmarks

### Individual Benchmarks

**GPQA (Graduate-Level Q&A)**
```bash
python scripts/gpqa_run.py --max_samples 50
```

**KEGG (Biological Pathways)**
```bash
python scripts/bio_kegg_run.py --pathways hsa00010 hsa00020
```

**SWE-Bench (Software Engineering)**
```bash
python scripts/swe_run.py --image sweagent/swe-agent:latest --max_tasks 10
```

### Unified Runner

```bash
# Run all benchmarks (except SWE which needs Docker)
python scripts/run_benchmarks.py --benchmarks all

# Run specific benchmarks
python scripts/run_benchmarks.py --benchmarks gpqa kegg

# With custom parameters
python scripts/run_benchmarks.py \
  --benchmarks gpqa kegg \
  --gpqa-max-samples 100 \
  --kegg-pathways hsa00010 hsa00020 hsa00030
```

## Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--output` | Output file path | `logs/benchmarks/{benchmark}_results.json` |
| `--max_samples` | Max samples (GPQA) | None (all) |
| `--pathways` | KEGG pathway IDs | `hsa00010 hsa00020` |
| `--max_tasks` | Max tasks (SWE-Bench) | 5 |

## Results Format

All results include watermark for verification:

```json
{
  "watermark": {
    "timestamp": "2026-01-10T00:00:00Z",
    "content_hash": "sha256...",
    "framework": "evolving-sun-benchmarks",
    "version": "1.0.0"
  },
  "data": { ... }
}
```

## CI/CD

### Manual Workflow Trigger

1. Go to: **Actions** → **Weekly Benchmark CI** → **Run workflow**
2. Select parameters:
   - Benchmarks: `gpqa,kegg` or `all`
   - Max samples: `50` (default)

### Scheduled Runs

Automatic weekly runs every Monday at 00:00 UTC

## File Structure

```
Evolving-sun/
├── .github/workflows/     # CI workflows
├── src/utils/            # Utilities (secure_logging)
├── scripts/              # Benchmark harnesses
├── vendor/SWE-bench/     # Submodule
├── logs/benchmarks/      # Output (gitignored)
├── examples/             # Usage examples
└── docs/                 # Documentation
```

## Quick Troubleshooting

**Import errors**
```bash
pip install -r requirements.txt
```

**Submodule missing**
```bash
git submodule update --init --recursive
```

**Permission denied**
```bash
chmod +x scripts/*.py
```

## Key Commands

```bash
# Run examples
python examples/usage_examples.py

# Test GPQA (quick)
python scripts/gpqa_run.py --max_samples 10

# Test KEGG (quick)
python scripts/bio_kegg_run.py --pathways hsa00010

# Validate workflow
python -c "import yaml; yaml.safe_load(open('.github/workflows/weekly-benchmarks.yml'))"
```

## Documentation

- **README.md** - Overview and setup
- **docs/ci-workflow.md** - CI/CD details
- **CONTRIBUTING.md** - Contribution guide
- **examples/** - Usage examples

## Support

- Issues: [GitHub Issues](https://github.com/Teamintelxsel/Evolving-sun/issues)
- Discussions: [GitHub Discussions](https://github.com/Teamintelxsel/Evolving-sun/discussions)
