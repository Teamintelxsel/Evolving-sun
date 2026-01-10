# Evolving-sun

Structured logging, upgrades, and conversation management system with integrated benchmarking capabilities.

## Overview

This repository provides utilities and infrastructure for:
- **Structured Logging**: Organized log directories for evolution, benchmarks, security, and agent activity with watermarking and provenance tracking
- **Upgrade Management**: Version tracking and archival system for software upgrades
- **Conversation Ingestion**: Tools to import and organize conversation exports
- **Benchmark Runners**: Unified system for running and archiving benchmark results
  - **Legacy Benchmarks**: Performance, accuracy, and security metrics
  - **SWE-bench Verified**: Software engineering task evaluation
  - **GPQA Diamond**: Graduate-level science question answering
  - **KEGG KGML**: Biological pathway analysis

## Repository Structure

```
Evolving-sun/
├── .github/workflows/       # CI/CD workflows (weekly benchmarks)
├── docs/
│   ├── conversations/       # Imported conversation archives
│   └── EXAMPLES.md          # Detailed usage examples
├── examples/                # Example scripts demonstrating utilities
├── logs/
│   ├── evolution/           # Evolution tracking logs
│   ├── benchmarks/          # Benchmark execution logs and results (watermarked)
│   ├── security/            # Security-related logs
│   └── agent-activity/      # Agent activity logs
├── scripts/
│   ├── import_conversations.py  # Conversation import utility
│   ├── run_benchmarks.py        # Legacy benchmark runner
│   ├── unified_runner.py        # Unified benchmark harness runner
│   ├── swe_run.py              # SWE-bench Verified runner
│   ├── gpqa_run.py             # GPQA Diamond runner
│   └── bio_kegg_run.py         # KEGG KGML runner
├── src/
│   └── utils/               # Core utility modules (logging, secure_logging)
├── upgrades/
│   ├── v1.0/                # Version 1.0 upgrades
│   └── archive/             # Historical upgrade archives
└── vendor/
    └── SWE-bench/           # SWE-bench submodule (for real evaluations)
```

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git (for submodules)
- Docker (optional, for SWE-bench evaluations)

### Installation

Clone the repository with submodules:

```bash
git clone --recurse-submodules https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun
```

If you've already cloned without submodules:

```bash
cd Evolving-sun
git submodule update --init --recursive
```

Optional: Install Python dependencies for enhanced features:

```bash
pip install datasets  # For real GPQA dataset access
# Docker is required for real SWE-bench evaluations
```

## Usage

### Importing Conversations

Use the conversation import utility to ingest plaintext or markdown conversation exports:

```bash
# Basic usage
python scripts/import_conversations.py path/to/conversation.txt

# Specify custom output name
python scripts/import_conversations.py chat.txt --output-name meeting_notes

# Overwrite existing file
python scripts/import_conversations.py chat.txt --overwrite

# Specify output format
python scripts/import_conversations.py chat.txt --format markdown
```

The script will:
1. Read the input conversation file
2. Add metadata headers (timestamp, source)
3. Save to `docs/conversations/` with proper formatting

### Running Benchmarks

#### Unified Benchmark Runner

Run all benchmarks with a single command:

```bash
# Run all benchmarks (legacy + new harnesses)
python scripts/unified_runner.py

# Run specific benchmark categories
python scripts/unified_runner.py --gpqa --kegg
python scripts/unified_runner.py --swe-bench --swe-max-tasks 5
```

#### Individual Benchmark Harnesses

**Legacy Benchmarks** (Performance, Accuracy, Security):

```bash
# Run all legacy benchmarks
python scripts/run_benchmarks.py

# Run specific legacy benchmarks
python scripts/run_benchmarks.py --benchmark performance
python scripts/run_benchmarks.py --benchmark accuracy
python scripts/run_benchmarks.py --benchmark security
```

**SWE-bench Verified** (Software Engineering Benchmarks):

```bash
# Run with default settings
python scripts/swe_run.py

# Customize execution
python scripts/swe_run.py --max-tasks 20 --num-workers 2 --dataset verified
```

**GPQA Diamond** (Graduate-Level Science Questions):

```bash
# Run with default settings (500 examples)
python scripts/gpqa_run.py

# Limit number of examples
python scripts/gpqa_run.py --limit 100
```

**KEGG KGML** (Biological Pathway Benchmarks):

```bash
# Run with default settings (10 pathways, human organism)
python scripts/bio_kegg_run.py

# Customize organism and pathway count
python scripts/bio_kegg_run.py --organism hsa --max-pathways 20
```

All benchmark results are saved to `logs/benchmarks/` as watermarked JSON files with provenance information.

### Using Structured Logging

```python
from src.utils import get_logger, log_benchmark_event

# Get a logger
logger = get_logger("evolution")
logger.info("System started")

# Log structured events
log_benchmark_event("test_complete", {"status": "passed", "duration": 45.2})
```

See [examples/](examples/) for more detailed usage examples.

## Directory Purposes

### Logs
- **evolution/**: Track system evolution and changes over time
- **benchmarks/**: Store benchmark execution results and performance data
- **security/**: Security audit logs and vulnerability reports
- **agent-activity/**: Agent operation logs and activity tracking

### Upgrades
- **v1.0/**: Current version upgrade scripts and documentation
- **archive/**: Historical upgrade records for reference

### Documentation
- **conversations/**: Archived conversation exports for knowledge retention

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Documentation

- [Examples](docs/EXAMPLES.md) - Detailed usage examples
- [Scripts Documentation](scripts/README.md) - Script usage and reference
- [Utilities Documentation](src/utils/README.md) - API documentation for utilities
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## License

This project is open source and available under the MIT License.

## Related Issues

For tracking and organization of issues related to this project, please refer to the GitHub Issues page.

## Roadmap

- [x] Establish directory structure
- [x] Create conversation import utility
- [x] Add unified benchmark runners
- [x] Implement weekly CI for benchmark archival
- [x] Add structured logging utilities
- [x] Create comprehensive documentation and examples
- [x] Integrate real benchmark harnesses (SWE-bench, GPQA, KEGG)
- [x] Add secure logging with watermarking and provenance tracking
- [x] Implement vendor submodule for SWE-bench
- [x] Add workflow audit improvements (permissions, concurrency, pinning, caching)
- [ ] Add security scanning integration
- [ ] Enhance logging with real-time monitoring
- [ ] Replace simulated metrics with real benchmark results (after first runs)
- [ ] Integrate with external monitoring tools
