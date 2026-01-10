# Contributing to Evolving Sun

Thank you for your interest in contributing to Evolving Sun! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our Code of Conduct.

### Our Pledge

- **Be Respectful**: Treat everyone with respect. Disagreements are fine, but be civil.
- **Be Inclusive**: Welcome newcomers and help them get started.
- **Be Collaborative**: Work together to achieve the best outcomes.
- **Be Professional**: Maintain professionalism in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Evolving-sun.git
   cd Evolving-sun
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Teamintelxsel/Evolving-sun.git
   ```

## Development Setup

### Prerequisites

- Python 3.12 or higher
- Git
- Docker (optional, for testing)

### Installation

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,all]"

# Install pre-commit hooks
pre-commit install
```

### Verify Setup

```bash
# Run tests
pytest

# Run linters
black --check .
ruff check .
mypy src/
```

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check the [issue tracker](https://github.com/Teamintelxsel/Evolving-sun/issues)
2. Check if the issue has already been reported
3. Try to reproduce the issue with the latest version

When filing a bug report, include:
- Clear title and description
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check if the enhancement has already been suggested
2. Provide a clear use case
3. Explain why this enhancement would be useful
4. Consider providing a proof of concept

### Your First Contribution

Looking for a good first issue? Check for issues labeled:
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `documentation` - Documentation improvements

## Pull Request Process

### Before Submitting

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Test your changes**:
   ```bash
   pytest
   black .
   ruff check .
   mypy src/
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "feat: add amazing feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test additions or changes
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting the PR

1. Go to the [repository](https://github.com/Teamintelxsel/Evolving-sun)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill in the PR template:
   - Clear description of changes
   - Link to related issues
   - Testing performed
   - Screenshots (if UI changes)

### PR Review Process

1. **Automated checks** must pass (tests, linters, security scans)
2. **Code review** by at least one maintainer
3. **Address feedback** and update your PR
4. **Squash commits** if requested
5. **Merge** once approved

## Coding Standards

### Python Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use **Black** for formatting (line length: 100)
- Use **Ruff** for linting
- Use **mypy** for type checking

### Code Organization

```python
"""Module docstring explaining purpose."""

import standard_library
import third_party_library

from project import module


class MyClass:
    """Class docstring."""

    def __init__(self, param: str) -> None:
        """Initialize with parameter."""
        self.param = param

    def method(self, arg: int) -> str:
        """Method docstring.

        Args:
            arg: Argument description

        Returns:
            Return value description
        """
        return f"{self.param}: {arg}"
```

### Type Hints

Always use type hints:

```python
from typing import Any, Dict, List, Optional

def process_data(
    data: List[Dict[str, Any]],
    config: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Process data with optional config."""
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def complex_function(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    ...
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Mirror the structure of `src/`
- Use pytest for testing
- Aim for >80% code coverage

Example:

```python
import pytest
from src.agents.mutator import KEGGMutator


def test_mutator_initialization():
    """Test mutator initializes correctly."""
    mutator = KEGGMutator()
    assert mutator.generation == 0


def test_mutator_evolve():
    """Test evolution runs without errors."""
    mutator = KEGGMutator()
    results = mutator.evolve(generations=1)
    assert results["total_mutations"] > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mutator.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_mutator.py::test_mutator_initialization
```

## Documentation

### Code Documentation

- All public modules, classes, and functions must have docstrings
- Use clear, concise language
- Include examples for complex functions

### User Documentation

- Update README.md for user-facing changes
- Update ARCHITECTURE.md for architectural changes
- Add examples to `examples/` directory

### API Documentation

We use automated API documentation generation. Ensure your docstrings are complete and accurate.

## Security

### Reporting Security Issues

**DO NOT** create a public issue for security vulnerabilities.

Instead:
1. Email security@evolving-sun.ai
2. Provide detailed description
3. Include steps to reproduce
4. Allow 90 days for fix before disclosure

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Follow OWASP security guidelines
- Run security scans before submitting PR

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open a [Discussion](https://github.com/Teamintelxsel/Evolving-sun/discussions)
- Join our [Discord](https://discord.gg/evolving-sun)
- Email: team@evolving-sun.ai

---

**Thank you for contributing to Evolving Sun! 🌞**
