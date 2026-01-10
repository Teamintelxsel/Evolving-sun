# Contributing to Evolving Sun

Thank you for your interest in contributing to the Evolving Sun benchmark framework! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git with submodule support
- (Optional) Docker for SWE-Bench benchmarks

### Setup Development Environment

1. Fork and clone the repository:
```bash
git clone --recursive https://github.com/YOUR_USERNAME/Evolving-sun.git
cd Evolving-sun
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install development dependencies (if any):
```bash
pip install pytest black flake8  # Example dev tools
```

## Project Structure

```
.
├── .github/workflows/    # CI/CD workflows
├── src/utils/           # Core utilities (secure_logging, etc.)
├── scripts/             # Benchmark harness scripts
├── vendor/              # Git submodules (SWE-bench)
├── examples/            # Usage examples
├── docs/                # Documentation
└── logs/                # Output directory (gitignored)
```

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

Example:
```python
def watermark_log(data: Dict[str, Any], output_path: str) -> None:
    """
    Write benchmark results to a JSON file with security watermark.
    
    Args:
        data: Dictionary containing benchmark results
        output_path: Path to write the watermarked JSON file
    """
    # Implementation
```

### Adding a New Benchmark

1. Create a new script in `scripts/`:
```bash
touch scripts/new_benchmark_run.py
chmod +x scripts/new_benchmark_run.py
```

2. Follow the existing pattern:
   - Import `src.utils.secure_logging.watermark_log`
   - Use argparse for CLI arguments
   - Write results with watermarking
   - Return appropriate exit codes

3. Example template:
```python
#!/usr/bin/env python3
"""New benchmark harness."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.secure_logging import watermark_log

def run_benchmark():
    """Run the benchmark."""
    # Implementation
    results = {"status": "success"}
    return results

def main():
    parser = argparse.ArgumentParser(description="New benchmark")
    parser.add_argument("--output", default="logs/benchmarks/new_results.json")
    args = parser.parse_args()
    
    results = run_benchmark()
    watermark_log(results, args.output)
    
    sys.exit(0 if results.get("status") == "success" else 1)

if __name__ == "__main__":
    main()
```

4. Add to unified runner (`scripts/run_benchmarks.py`)

5. Update CI workflow if needed

6. Update documentation

### Testing

Before submitting changes:

1. Test your benchmark script:
```bash
python scripts/your_benchmark.py --output /tmp/test.json
```

2. Verify watermarked output:
```python
import json
with open('/tmp/test.json') as f:
    data = json.load(f)
    assert 'watermark' in data
    assert 'data' in data
```

3. Test unified runner:
```bash
python scripts/run_benchmarks.py --benchmarks your_benchmark
```

4. Check code style:
```bash
flake8 scripts/your_benchmark.py
black --check scripts/your_benchmark.py
```

### Commit Guidelines

- Use clear, descriptive commit messages
- Reference issue numbers when applicable
- Keep commits focused on single changes

Good commit messages:
```
Add MMLU benchmark harness

- Implement mmlu_run.py with HuggingFace integration
- Add to unified runner
- Update CI workflow
- Add documentation

Fixes #123
```

### Pull Request Process

1. **Create a branch**:
```bash
git checkout -b feature/add-mmlu-benchmark
```

2. **Make your changes** following the guidelines above

3. **Test thoroughly**:
   - Run your benchmark script
   - Check for Python errors
   - Verify watermarked output

4. **Update documentation**:
   - Update README.md if needed
   - Add examples to examples/
   - Update docs/ci-workflow.md for CI changes

5. **Commit and push**:
```bash
git add .
git commit -m "Add MMLU benchmark harness"
git push origin feature/add-mmlu-benchmark
```

6. **Open Pull Request**:
   - Use descriptive title
   - Explain what and why
   - Link related issues
   - Include test results

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] All scripts are executable (`chmod +x`)
- [ ] Watermarked logging is used for all results
- [ ] Documentation is updated
- [ ] Examples are added/updated if needed
- [ ] Scripts tested locally
- [ ] No sensitive data in commits
- [ ] .gitignore updated if needed

## CI/CD Contributions

### Workflow Changes

When modifying `.github/workflows/`:

1. **Maintain security best practices**:
   - Pin action versions
   - Use minimal permissions
   - Add timeouts
   - Enable caching

2. **Test locally** (if possible):
```bash
# Use act for local testing (https://github.com/nektos/act)
act -W .github/workflows/weekly-benchmarks.yml
```

3. **Document changes** in `docs/ci-workflow.md`

### Security Audit Requirements

All CI workflows must include:
- ✅ Minimal permissions
- ✅ Version pinning
- ✅ Concurrency control
- ✅ Timeouts
- ✅ Caching (where applicable)

## Documentation

### Updating Documentation

- Keep README.md concise and high-level
- Add detailed docs to `docs/` directory
- Include examples in `examples/`
- Update docstrings for code changes

### Documentation Style

- Use Markdown for all documentation
- Include code examples
- Add screenshots for UI changes
- Keep language clear and concise

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check `docs/` directory

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Report unacceptable behavior

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

## Questions?

Feel free to open an issue with the "question" label or start a discussion!

---

Thank you for contributing to Evolving Sun! 🌟
