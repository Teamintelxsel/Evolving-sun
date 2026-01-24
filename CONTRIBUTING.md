# Contributing to Evolving-sun

Thank you for your interest in contributing to Evolving-sun! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Evolving-sun.git`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun

# Test the utilities
python scripts/run_benchmarks.py --no-save
python examples/complete_workflow.py
```

## Project Structure

```
Evolving-sun/
├── .github/workflows/   # CI/CD workflows
├── docs/                # Documentation and conversations
├── examples/            # Usage examples
├── logs/                # Log directories (content ignored by git)
├── scripts/             # Utility scripts
├── src/utils/           # Core utility modules
└── upgrades/            # Version upgrade tracking
```

## Coding Standards

### Python Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to all modules, classes, and functions
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Documentation

- Update README.md when adding new features
- Add docstrings to new modules and functions
- Create examples for new utilities
- Update relevant documentation in docs/

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Longer description if needed

Examples:
feat(logging): add support for custom log formats
fix(benchmarks): correct throughput calculation
docs(readme): update installation instructions
chore(deps): update dependencies
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `perf`: Performance improvements

## Adding New Features

### New Scripts

When adding a new script to `scripts/`:

1. Add a shebang: `#!/usr/bin/env python3`
2. Include comprehensive docstring
3. Use argparse for CLI arguments
4. Provide --help documentation
5. Make it executable: `chmod +x scripts/your_script.py`
6. Document in `scripts/README.md`
7. Add usage example to `docs/EXAMPLES.md`

### New Utilities

When adding utilities to `src/utils/`:

1. Create module with clear purpose
2. Add comprehensive docstrings
3. Export public API in `__init__.py`
4. Document in `src/utils/README.md`
5. Create example in `examples/`

### New Benchmarks

When adding benchmarks to `scripts/run_benchmarks.py`:

1. Add method to BenchmarkRunner class
2. Follow existing benchmark structure
3. Return consistent result format
4. Include appropriate metrics
5. Add to --benchmark choices
6. Document expected output

## Testing

Before submitting a PR:

1. Test all modified scripts
2. Verify examples run without errors
3. Check that documentation is accurate
4. Ensure no log files are committed (except benchmark results)

```bash
# Test scripts
python scripts/run_benchmarks.py --benchmark all --no-save
python scripts/import_conversations.py --help

# Test examples
python examples/complete_workflow.py

# Verify logging
python -c "from src.utils import get_logger; logger = get_logger('evolution'); logger.info('test')"
```

## Pull Request Process

1. Update documentation for any changed functionality
2. Add examples if introducing new features
3. Ensure your code follows the style guidelines
4. Write clear PR description explaining changes
5. Reference any related issues
6. Wait for review and address feedback

## Code Review

All submissions require review. We look for:

- Code quality and style
- Proper documentation
- Working examples
- No breaking changes (unless justified)
- Clear commit messages

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- Questions about contributing

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
