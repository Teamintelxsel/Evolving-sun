# Security Policy

## Overview

The Evolving-sun project takes security seriously. We appreciate your efforts to responsibly disclose your findings and will make every effort to acknowledge your contributions.

## Supported Versions

We currently support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest| :x:                |

**Note:** As this repository is in active development, we recommend always using the latest version from the main branch.

## Reporting a Vulnerability

We strongly encourage you to report security vulnerabilities to us privately to help protect the community.

### Where to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security vulnerabilities through one of the following methods:

1. **GitHub Security Advisories** (Preferred)
   - Navigate to the [Security Advisories](https://github.com/Teamintelxsel/Evolving-sun/security/advisories) page
   - Click "Report a vulnerability"
   - Fill in the details

2. **Email**
   - Send an email to: **enderyou@gmail.com**
   - Use the subject line: `[SECURITY] Evolving-sun Vulnerability Report`
   - Include as much detail as possible (see below)

### What to Include in Your Report

To help us understand and address the issue quickly, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What an attacker could achieve by exploiting this vulnerability
- **Affected Components**: Which parts of the codebase are affected
- **Reproduction Steps**: Step-by-step instructions to reproduce the issue
- **Proof of Concept**: Code snippets, screenshots, or logs demonstrating the vulnerability
- **Suggested Fix**: If you have ideas for how to fix the issue (optional)
- **CVE Identifiers**: If applicable

### What to Expect

After you submit a vulnerability report:

1. **Acknowledgment**: We will acknowledge receipt of your report within **48 hours**
2. **Initial Assessment**: We will provide an initial assessment within **5 business days**
3. **Status Updates**: We will keep you informed of our progress
4. **Fix Timeline**: We aim to release a fix within **30 days** for critical issues
5. **Disclosure**: We will work with you to determine an appropriate disclosure timeline

## Responsible Disclosure Policy

We kindly ask that you:

- **Give us reasonable time** to address the vulnerability before public disclosure
- **Avoid exploiting the vulnerability** beyond what is necessary to demonstrate it
- **Do not access, modify, or delete data** belonging to others
- **Keep details confidential** until we have addressed the issue
- **Act in good faith** to avoid privacy violations and service disruption

## Recognition

We believe in recognizing security researchers who help us improve our security:

- We will publicly acknowledge your contribution (unless you prefer to remain anonymous)
- You will be credited in our security advisories and release notes
- We maintain a [Security Hall of Fame](https://github.com/Teamintelxsel/Evolving-sun/security) for contributors

## Security Update Process

When a security vulnerability is confirmed:

1. **Triage**: We assess the severity and impact
2. **Development**: We develop and test a fix
3. **Review**: The fix undergoes security review
4. **Release**: We release a patched version
5. **Advisory**: We publish a security advisory
6. **Notification**: We notify affected users

## Security Best Practices for Contributors

If you're contributing to this project:

- **Never commit secrets**: Use environment variables and `.env` files (which are gitignored)
- **Review dependencies**: Check for known vulnerabilities before adding dependencies
- **Follow secure coding practices**: Validate inputs, sanitize outputs, use parameterized queries
- **Run security scans**: Use our automated security scanning workflows
- **Sign commits** (recommended): Use GPG to sign your commits

## Security Tools and Workflows

This repository uses automated security scanning:

- **Secret Scanning**: Detect-secrets runs on every push and pull request
- **Dependency Scanning**: Dependabot monitors for vulnerable dependencies
- **Code Scanning**: CodeQL analyzes code for security vulnerabilities (when enabled)

## Contact

For security-related questions or concerns:
- **Security Issues**: enderyou@gmail.com
- **General Questions**: Create a discussion in our [GitHub Discussions](https://github.com/Teamintelxsel/Evolving-sun/discussions)

## Policy Updates

This security policy may be updated from time to time. Please check back periodically for changes.

**Last Updated**: January 3, 2026
**Version**: 1.0
