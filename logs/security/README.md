# Security Logs

This directory contains security audit logs, vulnerability assessments, and security-related events.

## Purpose

Security logs track:
- Security audits and assessments
- Vulnerability scans
- Access control events
- Security patches and fixes
- Compliance checks

## Log Format

Security logs should include:

```markdown
# Security Audit Log

**Date**: YYYY-MM-DD HH:MM:SS UTC
**Audit Type**: [Vulnerability Scan|Access Review|Code Audit|Compliance Check]
**Severity**: [Critical|High|Medium|Low|Info]

## Summary
Brief description of the security event or audit

## Findings
Detailed findings from the audit or event

## Actions Taken
Steps taken to address any issues

## Status
[Open|In Progress|Resolved|Mitigated]

## References
- CVE-YYYY-XXXXX
- Related PR #XXX
```

## Important Notes

- **DO NOT** commit sensitive information (credentials, tokens, keys)
- Use references to external secure systems for sensitive data
- Redact any PII or confidential information

## Naming Convention

Files should be named: `YYYY-MM-DD-audit-type.md`

Example: `2026-01-10-vulnerability-scan.md`
