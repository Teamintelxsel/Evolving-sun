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
├── docs/
│   └── conversations/          # Imported conversation archives
├── logs/
│   ├── evolution/              # Evolution tracking logs
│   ├── benchmarks/             # Benchmark execution logs
│   ├── security/               # Security-related logs
│   └── agent-activity/         # Agent activity logs
├── scripts/
│   └── import_conversations.py # Conversation import utility
├── src/
│   └── utils/                  # Utility modules
└── upgrades/
    ├── v1.0/                   # Version 1.0 upgrades
    └── archive/                # Historical upgrade archives
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

(Benchmark runners will be added in future updates)

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

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project is open source and available under the MIT License.

## Related Issues

For tracking and organization of issues related to this project, please refer to the GitHub Issues page.

## Roadmap

- [x] Establish directory structure
- [x] Create conversation import utility
- [ ] Add unified benchmark runners
- [ ] Implement weekly CI for benchmark archival
- [ ] Add security scanning integration
- [ ] Enhance logging utilities
