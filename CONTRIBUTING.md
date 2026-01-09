# Contributing to Evolving-sun

Thank you for your interest in contributing to Evolving-sun! This document provides guidelines and information for contributors.

---

## 🎯 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and professional in all interactions.

---

## 📋 Before Contributing

### Intellectual Property Assignment

**IMPORTANT**: All contributors must sign our **Contributor License Agreement (CLA)** before any contributions can be accepted.

By contributing to Evolving-sun, you agree that:
1. All contributions become the property of Evolving-sun
2. Contributions may be used in commercial products
3. You have the right to make the contribution
4. Contributions are provided under the project's license

[**Sign the CLA →**](https://evolving-sun.ai/cla)

### Non-Disclosure Agreement (NDA)

For contributions involving:
- Core algorithms
- Training data
- Model architectures
- Business logic

You must sign an NDA. Contact legal@evolving-sun.ai for the NDA template.

---

## 🚀 Getting Started

### 1. Fork the Repository

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/Evolving-sun.git
cd Evolving-sun
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming conventions**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

---

## 💻 Development Guidelines

### Code Style

We use:
- **Black** for Python formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black .
isort .

# Lint
flake8 .

# Type check
mypy ai/ benchmarks/ simulations/
```

### Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer description if needed.

Refs: #123
```

**Types**:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `style:` - Code style (formatting, not behavior)
- `refactor:` - Code restructuring
- `test:` - Test additions/changes
- `chore:` - Build process, dependencies

**Examples**:
```
feat(router): add cost optimization for model selection

Implements dynamic model selection based on cost constraints.
Uses weighted scoring: accuracy (50%), cost (30%), latency (20%).

Refs: #42
```

```
fix(benchmark): handle timeout in GPQA benchmark

Adds 60-second timeout to prevent hanging on slow models.
Fallback to cached results if available.

Refs: #58
```

### Testing

All contributions must include tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_model_router.py

# Run with coverage
pytest --cov=ai --cov=benchmarks --cov=simulations
```

**Test requirements**:
- Unit tests for new functions/classes
- Integration tests for multi-component features
- Minimum 80% code coverage
- All tests must pass before PR approval

### Documentation

Update documentation for any user-facing changes:

- **Code comments**: Explain complex logic
- **Docstrings**: All public functions/classes
- **README updates**: For new features
- **Changelog**: Add entry to CHANGELOG.md

**Docstring format** (Google style):

```python
def select_model(
    task_type: TaskType,
    cost_limit: Optional[float] = None
) -> Optional[ModelMetadata]:
    """
    Select optimal model based on task requirements.
    
    Args:
        task_type: Type of task (reasoning, coding, etc.)
        cost_limit: Maximum cost per 1K tokens (optional)
    
    Returns:
        Selected model metadata, or None if no suitable model
    
    Raises:
        ValueError: If task_type is invalid
    
    Example:
        >>> model = select_model(TaskType.REASONING, cost_limit=0.01)
        >>> print(model.model_id)
        'gpt4_turbo'
    """
```

---

## 🔐 Security Guidelines

### Secret Management

**NEVER commit**:
- API keys
- Passwords
- Tokens
- Private keys
- Customer data

Use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

### Security Review

All PRs undergo security review:
1. Automated secret scanning (TruffleHog)
2. Dependency vulnerability checks (Safety)
3. Manual code review for security issues

---

## 📝 Pull Request Process

### 1. Create Pull Request

1. Push your branch to GitHub
2. Open a Pull Request against `main`
3. Fill out the PR template completely
4. Link related issues

### 2. PR Requirements

Your PR must:
- ✅ Pass all CI checks
- ✅ Include tests (80%+ coverage)
- ✅ Update documentation
- ✅ Follow code style guidelines
- ✅ Have descriptive commit messages
- ✅ Be signed (CLA)

### 3. Review Process

1. **Automated checks** run first (CI/CD)
2. **Code review** by maintainer (1-3 days)
3. **Address feedback** (you may need to make changes)
4. **Approval** by 2 maintainers required
5. **Merge** (squash and merge preferred)

### 4. After Merge

- Your contribution appears in next release
- You're added to CONTRIBUTORS.md
- Thank you! 🎉

---

## 🎯 Contribution Areas

### High Priority

Looking for contributions in:
- 🔧 **Model provider integrations** (OpenAI, Anthropic, Google, Meta)
- 🧪 **Benchmark implementations** (GPQA, SWE-bench)
- 🛡️ **Security features** (DID/VC, semantic inspection)
- 📊 **Simulation systems** (digital twin, red team, evolutionary)
- 📚 **Documentation** (tutorials, examples, API docs)

### Good First Issues

Start here:
- [Issues labeled "good first issue"](https://github.com/Teamintelxsel/Evolving-sun/labels/good%20first%20issue)
- Documentation improvements
- Test coverage improvements
- Bug fixes

---

## 🤝 Community

### Getting Help

- 💬 [GitHub Discussions](https://github.com/Teamintelxsel/Evolving-sun/discussions)
- 🐛 [Issue Tracker](https://github.com/Teamintelxsel/Evolving-sun/issues)
- 📧 Email: support@evolving-sun.ai

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md (all contributors)
- Release notes (significant contributions)
- README.md (top contributors)

---

## ⚖️ Licensing

### Open Source (Academic)
- Contributions under Apache 2.0 + Commons Clause
- Free for non-commercial research
- Cannot be sold commercially

### Commercial
- Enterprise features are proprietary
- Contributions to enterprise features require special agreement
- Contact legal@evolving-sun.ai

---

## 📚 Resources

### Documentation
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [API Reference](./docs/API.md)
- [Developer Guide](./docs/DEVELOPER.md)

### Code Examples
- [Model Router Examples](./examples/model_router.py)
- [Benchmark Examples](./examples/benchmarks.py)
- [Simulation Examples](./examples/simulations.py)

---

## 📞 Questions?

Don't hesitate to ask:
- Create a [Discussion](https://github.com/Teamintelxsel/Evolving-sun/discussions)
- Email: contributors@evolving-sun.ai
- Join our Slack (request invite)

---

Thank you for contributing to Evolving-sun! Your contributions help build the future of enterprise AI. 🌟
