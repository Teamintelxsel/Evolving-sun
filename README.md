# Evolving Sun

A repository for tracking AI agent evolution, logging, and conversation archival.

## Purpose

This repository serves as a central hub for:
- **Evolution Logging**: Track changes and improvements in AI agent capabilities over time
- **Conversation Archival**: Store and organize meaningful conversations for analysis and reference
- **Benchmark Tracking**: Monitor performance metrics and improvements
- **Security Monitoring**: Log security-related events and audits
- **Agent Activity**: Track agent behaviors and interactions

## Repository Structure

```
Evolving-sun/
├── logs/                       # Centralized logging
│   ├── evolution/             # Evolution tracking logs
│   ├── benchmarks/            # Performance benchmark logs
│   ├── security/              # Security audit logs
│   └── agent-activity/        # Agent activity logs
├── upgrades/                   # Upgrade documentation and history
│   ├── v1.0/                  # Version 1.0 upgrades
│   └── archive/               # Archived upgrades
├── docs/                       # Documentation
│   └── conversations/         # Archived conversations
├── scripts/                    # Utility scripts
│   └── import_conversations.py # Conversation import tool
└── src/                        # Source code utilities
    └── utils/                 # Helper utilities
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Tools

### Conversation Import

Import plaintext or markdown conversation exports into the conversation archive:

```bash
python scripts/import_conversations.py --input conversation.txt --title "My Conversation" --tags "ai,development"
```

For more details, see [Conversation Import Documentation](docs/tools/conversation-import.md).

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting pull requests.

## License

This project is open source. Please check the LICENSE file for details.

## Contact

For questions or suggestions, please open an issue in this repository.
