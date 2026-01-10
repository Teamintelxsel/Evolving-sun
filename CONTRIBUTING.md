# Contributing to Evolving Sun

Thank you for your interest in contributing to Evolving Sun! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/Evolving-sun.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit and push: `git commit -m "Description" && git push origin feature/your-feature-name`
7. Open a Pull Request

## Areas for Contribution

### 1. Evolution Logs

Document improvements and changes in agent capabilities:
- New features or capabilities
- Performance improvements
- Behavioral changes
- Learning milestones

Format: See `logs/evolution/README.md` for the log entry format.

### 2. Conversation Archives

Import and archive meaningful conversations:
- Technical discussions
- Design decisions
- Problem-solving sessions

Tool: Use `scripts/import_conversations.py` to import conversations.

### 3. Benchmarks

Add performance benchmarks and metrics:
- Response time measurements
- Accuracy assessments
- Resource utilization tracking

Format: JSON files in `logs/benchmarks/`

### 4. Documentation

Improve documentation:
- Usage guides
- Examples
- Best practices
- Tool documentation

### 5. Tooling

Enhance existing tools or create new ones:
- Conversation import enhancements
- Analysis scripts
- Automation utilities
- Visualization tools

## Contribution Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Markdown**: Use consistent formatting
- **JSON**: Use 2-space indentation
- **Comments**: Add helpful comments for complex logic

### Commit Messages

Use clear, descriptive commit messages:
- Start with a verb (Add, Fix, Update, Remove)
- Keep first line under 50 characters
- Add detailed description if needed

Examples:
```
Add benchmark tracking for response times
Fix metadata parsing in import script
Update conversation import documentation
```

### Documentation

- Update relevant README files when adding features
- Add examples for new functionality
- Keep documentation in sync with code changes

### Testing

- Test your changes before submitting
- Include test cases for new features
- Verify CI passes on your PR

## Pull Request Process

1. **Update documentation** - Ensure all docs are current
2. **Test thoroughly** - Verify your changes work as expected
3. **Clean commit history** - Squash commits if needed
4. **Describe changes** - Provide clear PR description
5. **Link issues** - Reference related issues if applicable

## File Organization

### Logs
- `logs/evolution/` - Evolution tracking
- `logs/benchmarks/` - Performance metrics
- `logs/security/` - Security audits
- `logs/agent-activity/` - Agent behavior logs

### Documentation
- `docs/conversations/` - Archived conversations
- `docs/tools/` - Tool documentation

### Code
- `scripts/` - Utility scripts
- `src/utils/` - Shared utilities

### Configuration
- `.github/workflows/` - CI/CD workflows
- `requirements.txt` - Python dependencies

## Naming Conventions

### Log Files
- Evolution: `YYYY-MM-DD-description.md`
- Benchmarks: `YYYY-MM-DD-benchmark-type.json`
- Security: `YYYY-MM-DD-audit-type.md`
- Activity: `YYYY-MM-DD-activity-type.json|.md`

### Conversations
- Markdown: `YYYY-MM-DD-title.md`
- Metadata: `YYYY-MM-DD-title.meta.json`

## Security

- **Never commit secrets** - No API keys, passwords, or tokens
- **No PII** - Remove personally identifiable information
- **Review carefully** - Check all changes before committing
- **Report vulnerabilities** - Open a security issue for vulnerabilities

## Questions?

Open an issue for:
- Questions about contributing
- Clarifications on guidelines
- Feature requests
- Bug reports

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other contributors

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to Evolving Sun! 🌟
