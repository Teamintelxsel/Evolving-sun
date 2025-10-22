# Contributing to Evolving-sun

Thank you for your interest in contributing to the Evolving-sun project! This document provides guidelines and information to help you contribute effectively.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Process](#development-process)
- [Contribution Guidelines](#contribution-guidelines)
- [Community and Communication](#community-and-communication)

## Code of Conduct

### Our Principles

The Evolving-sun project is built on principles of:

- **Transparency**: All work is open and documented
- **Empathy & Ethics**: Respectful, human-centric approach
- **Collaboration**: Community-driven decision making
- **Continuous Improvement**: Always evolving and learning
- **Accountability**: Clear tracking and responsibility

### Expected Behavior

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or insults
- Trolling or inflammatory comments
- Publishing others' private information
- Other unethical or unprofessional conduct

## Getting Started

### Repository Overview

Evolving-sun is an AI agent network focused on:
- Multi-agent collaboration and coordination
- Cross-project integration (Bridge system)
- Continuous improvement and evolution
- Community-driven development

### Key Documents to Review

Before contributing, please read:

1. **[README.md](README.md)** - Project overview and agent manifest
2. **[KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)** - Project principles and architecture
3. **[AGENT_AUDIT.md](AGENT_AUDIT.md)** - Comprehensive agent analysis and improvement plans
4. **[BRIDGE_MANIFESTO.md](BRIDGE_MANIFESTO.md)** - Vision for cross-project collaboration
5. **[SECURITY.md](SECURITY.md)** - Security policies and practices

### Repository Structure

```
Evolving-sun/
├── .github/
│   └── workflows/          # GitHub Actions workflows
├── bridge/                 # Bridge system (cross-project integration)
├── issues/                 # Issue documentation
├── library/                # Documentation and research
│   ├── README.md
│   └── CHANGE_LOG.md      # All changes tracked here
├── AGENT_AUDIT.md         # Agent audit and recommendations
├── BRIDGE_MANIFESTO.md    # Bridge system vision
├── KNOWLEDGE_BASE.md      # Project knowledge and principles
├── NANO_STATUS.md         # Nano agents status
├── README.md              # Main documentation
├── SECURITY.md            # Security policy
└── WORKFLOW_STATUS.md     # Workflow documentation
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Code Contributions**
   - Agent implementations
   - Workflow improvements
   - Testing infrastructure
   - Security enhancements

2. **Documentation**
   - Improving existing docs
   - Adding examples and guides
   - Translating documentation
   - Creating tutorials

3. **Testing**
   - Writing tests
   - Testing new features
   - Reporting bugs
   - Validating fixes

4. **Ideas and Proposals**
   - New agent capabilities
   - Architecture improvements
   - Feature suggestions
   - Process enhancements

5. **Community Support**
   - Answering questions
   - Helping other contributors
   - Participating in discussions
   - Reviewing pull requests

### Finding Ways to Contribute

- **Good First Issues**: Look for issues labeled `good first issue`
- **Help Wanted**: Check issues labeled `help wanted`
- **Agent Audit**: Review [AGENT_AUDIT.md](AGENT_AUDIT.md) for improvement areas
- **Documentation**: Help improve and expand documentation
- **Testing**: Add tests for existing functionality

## Development Process

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR-USERNAME/Evolving-sun.git
cd Evolving-sun

# Add upstream remote
git add remote upstream https://github.com/enderyou-lang/Evolving-sun.git
```

### 2. Create a Branch

```bash
# Create a descriptive branch name
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Branch naming conventions:
- `feature/` - New features or enhancements
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `test/` - Testing additions or changes
- `refactor/` - Code refactoring

### 3. Make Changes

- Make focused, logical commits
- Follow existing code style and conventions
- Write clear commit messages
- Update documentation as needed
- Add tests for new functionality

### 4. Test Your Changes

```bash
# Run any existing tests
# (Test framework to be established - see AGENT_AUDIT.md)

# Verify documentation builds correctly
# Ensure workflows are valid
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "Brief description of changes

Detailed explanation of what changed and why.

Fixes #issue-number"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin your-branch-name

# Create a pull request on GitHub
```

## Contribution Guidelines

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `style`: Code style changes (formatting)
- `chore`: Maintenance tasks

Example:
```
feat(nano-agent): Add parsing capability for Python files

Implements basic Python file parsing using AST module.
Supports syntax validation and structure extraction.

Closes #42
```

### Pull Request Guidelines

1. **Title**: Clear, descriptive title summarizing the change
2. **Description**: 
   - What changes were made
   - Why the changes were necessary
   - How the changes address the issue
   - Any relevant context or screenshots
3. **Link Issues**: Reference related issues with `Fixes #123` or `Relates to #456`
4. **Small PRs**: Keep pull requests focused and reasonably sized
5. **Tests**: Include tests when applicable
6. **Documentation**: Update docs to reflect changes

### Code Style

Currently, the repository is primarily documentation-focused. When code is added:

1. **Follow Language Conventions**
   - Use language-specific style guides
   - Maintain consistency with existing code
   - Add comments for complex logic

2. **Documentation**
   - Document all functions and classes
   - Provide usage examples
   - Keep README and docs updated

3. **Quality**
   - Write clean, readable code
   - Avoid unnecessary complexity
   - Handle errors gracefully

### Documentation Standards

1. **Markdown**
   - Use proper markdown formatting
   - Include table of contents for long documents
   - Add links to related documents

2. **Clarity**
   - Write clear, concise explanations
   - Use examples when helpful
   - Define technical terms

3. **Maintenance**
   - Keep documentation up to date
   - Include last updated date
   - Note document version where applicable

## Community and Communication

### Channels

1. **GitHub Issues**: Bug reports, feature requests, and task tracking
2. **GitHub Discussions**: Questions, ideas, and general discussion
3. **Pull Requests**: Code review and collaboration
4. **CHANGE_LOG.md**: Transparent record of all changes

### Issue Guidelines

When creating an issue:

1. **Search First**: Check if similar issue already exists
2. **Clear Title**: Descriptive summary of the issue
3. **Detailed Description**:
   - What is the issue or proposal?
   - Why is it important?
   - What is the expected behavior?
   - What is the actual behavior (for bugs)?
4. **Context**: Environment details, steps to reproduce (for bugs)
5. **Labels**: Add appropriate labels if possible

### Pull Request Review Process

1. **Automated Checks**: Workflows must pass
2. **Community Review**: Other contributors may provide feedback
3. **Maintainer Review**: Final review by project maintainers
4. **Iteration**: Address feedback and make requested changes
5. **Merge**: Once approved, PR will be merged

### Getting Help

- **Questions**: Use GitHub Discussions
- **Bugs**: Create an issue with detailed information
- **Security**: See [SECURITY.md](SECURITY.md)
- **Documentation**: Check [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md)

## Recognition

Contributors are recognized through:

1. **Git History**: All commits attributed to authors
2. **CHANGE_LOG.md**: Major contributions logged
3. **Contributors Section**: Listed in project documentation
4. **Community Acknowledgment**: Mentioned in releases and updates

## Transparency and Accountability

All contributions are:
- **Publicly visible**: Open source and transparent
- **Tracked**: Logged in CHANGE_LOG.md
- **Reviewable**: Subject to community review
- **Attributed**: Properly credited to authors

This aligns with our core principle of transparency and community-driven development.

## Agent Contributions

Contributions from AI agents (like Copilot) are:
- Clearly labeled as agent contributions
- Subject to the same review process
- Logged in CHANGE_LOG.md with agent attribution
- Part of our continuous improvement process

See [AGENT_AUDIT.md](AGENT_AUDIT.md) for details on current agents and their roles.

## Next Steps After Contributing

After your contribution is merged:

1. **Update Local Repository**
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Share**: Tell others about your contribution
3. **Continue**: Look for more ways to contribute
4. **Engage**: Participate in discussions and reviews

## Questions?

If you have questions about contributing:

- Review existing [documentation](KNOWLEDGE_BASE.md)
- Check [open discussions](https://github.com/enderyou-lang/Evolving-sun/discussions)
- Create a new discussion
- Ask in issue comments

## Thank You!

Every contribution, no matter how small, helps make Evolving-sun better. We appreciate your time, effort, and ideas!

---

**Last Updated**: 2025-10-22  
**Version**: 1.0  
**Maintained By**: Evolving-sun Community

For more information about the project, see:
- [README.md](README.md) - Project overview
- [KNOWLEDGE_BASE.md](KNOWLEDGE_BASE.md) - Project principles
- [AGENT_AUDIT.md](AGENT_AUDIT.md) - Agent analysis
- [SECURITY.md](SECURITY.md) - Security policy
