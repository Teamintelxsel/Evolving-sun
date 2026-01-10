# Evolving-sun

Structured logging, upgrades, and conversation management system with integrated benchmarking capabilities.

## Overview

This repository provides utilities and infrastructure for:
- **Structured Logging**: Organized log directories for evolution, benchmarks, security, and agent activity
- **Upgrade Management**: Version tracking and archival system for software upgrades
- **Conversation Ingestion**: Tools to import and organize conversation exports
- **Benchmark Runners**: Unified system for running and archiving benchmark results

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
│   ├── benchmarks/          # Benchmark execution logs and results
│   ├── security/            # Security-related logs
│   └── agent-activity/      # Agent activity logs
├── scripts/
│   ├── import_conversations.py  # Conversation import utility
│   └── run_benchmarks.py        # Unified benchmark runner
├── src/
│   └── utils/               # Core utility modules (logging, etc.)
└── upgrades/
    ├── v1.0/                # Version 1.0 upgrades
    └── archive/             # Historical upgrade archives
```

## Getting Started

### Prerequisites

- Python 3.7 or higher

### Installation

Clone the repository:

```bash
git clone https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun
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

Run all benchmarks (including real benchmark harnesses):

```bash
python scripts/run_benchmarks.py
```

Run specific benchmarks:

```bash
# Simulated benchmarks
python scripts/run_benchmarks.py --benchmark performance
python scripts/run_benchmarks.py --benchmark accuracy
python scripts/run_benchmarks.py --benchmark security

# Real benchmark harnesses
python scripts/run_benchmarks.py --benchmark swe-bench  # SWE-bench Verified
python scripts/run_benchmarks.py --benchmark gpqa       # GPQA dataset
python scripts/run_benchmarks.py --benchmark kegg       # KEGG pathways
```

Results are saved to `logs/benchmarks/` as watermarked JSON files with full provenance tracking.

See [scripts/BENCHMARKS.md](scripts/BENCHMARKS.md) for detailed documentation on benchmark harness integrations.

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
- [x] Add real benchmark harness integrations (SWE-bench, GPQA, KEGG)
- [x] Implement watermarked logging with provenance tracking
- [ ] Add security scanning integration
- [ ] Enhance logging with real-time monitoring
- [ ] Replace simulated metrics with real benchmark runs
- [ ] Add more benchmark types (MATH, HumanEval, etc.)
- [ ] Add support for more benchmark types
- [ ] Integrate with external monitoring tools
