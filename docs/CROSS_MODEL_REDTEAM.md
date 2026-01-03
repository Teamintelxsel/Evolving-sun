# Cross-Model Red-Team Audit

This document describes the cross-model red-teaming pipeline that runs safety
audits on model outputs using Grok-4-Heavy.

## Overview

The cross-model red-teaming pipeline provides:

- **Toxicity scoring** - Detects potentially harmful or toxic content
- **Hallucination detection** - Identifies factually incorrect or ungrounded claims
- **API misuse detection** - Flags suspicious patterns like injection attempts
- **Prompt safety checks** - Validates prompts follow safety guidelines

**Important**: This pipeline is **audit-only by default**. It will not block
builds or deployments unless explicitly configured to do so. Policy enforcement
must be configured separately.

## Quick Start

### Running Locally

```bash
# The audit script uses only Python standard library (no external dependencies)
# Install requirements.txt only if you want to run tests or linting
pip install -r requirements.txt  # Optional: only for testing/linting

# Run audit on a sample file
python tools/grok4_audit.py \
  --input path/to/darwin-results.json \
  --output audit_report.json \
  --mode audit-only

# Run in verbose mode
python tools/grok4_audit.py -i data.json -o report.json -v
```

### Running via GitHub Actions

The workflow triggers automatically when:
- A `darwin-results` artifact is produced by another workflow
- Manually via `workflow_dispatch`

To trigger manually:
1. Go to Actions → "Cross-Model Red-Team Audit"
2. Click "Run workflow"
3. Optionally specify an image reference to audit
4. Select audit mode (default: audit-only)

### Running In-Cluster (Kubernetes)

The CronJob is disabled by default. To enable:

```bash
# Review the CronJob configuration
kubectl get cronjob grok4-audit-cronjob -n evo-fast -o yaml

# Enable the CronJob (admin opt-in required)
kubectl patch cronjob grok4-audit-cronjob -n evo-fast \
  -p '{"spec":{"suspend":false}}'

# Check status
kubectl get cronjobs -n evo-fast
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROK_AUDIT_ENDPOINT` | API endpoint for Grok audits | `https://api.grok.example.com/v1/audit` |
| `GROK_API_KEY` | API key for authentication | (none) |
| `AUDIT_MODE` | `audit-only` or `blocking` | `audit-only` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Audit Modes

| Mode | Description | Exit Code |
|------|-------------|-----------|
| `audit-only` | Reports issues but does not block | Always 0 |
| `blocking` | Returns non-zero exit if issues found | 0 or 1 |

## Compute Requirements

### Local Execution

- Python 3.9+
- ~256MB RAM minimum
- No GPU required for default checks

### In-Cluster (Kubernetes)

Default resource requests/limits:
- **Memory**: 256Mi request, 1Gi limit
- **CPU**: 100m request, 500m limit

For large-scale audits, adjust resources in `k8s/cron-grok4-audit.yaml`.

## Output Format

The audit produces a JSON report with the following structure:

```json
{
  "timestamp": "2025-01-01T00:00:00.123456+00:00",
  "input_path": "darwin-results.json",
  "mode": "audit-only",
  "verdict": "audit-only",
  "toxicity_score": 0.0,
  "hallucination_score": 0.0,
  "api_misuse_flags": [],
  "prompt_safety_flags": [],
  "summary": "Completed 4 checks. 4/4 passed.",
  "checks": [...],
  "metadata": {
    "version": "1.0.0",
    "pipeline": "grok4_audit"
  }
}
```

### Verdict Values

| Verdict | Meaning |
|---------|---------|
| `audit-only` | Audit completed, no blocking action taken |
| `flagged` | Issues detected (only in blocking mode) |

## Integration with Decision Engine

The audit report can feed into a decision engine for policy enforcement:

1. **Audit Phase**: This pipeline produces `audit_report.json`
2. **Policy Phase**: A separate policy engine evaluates the report
3. **Enforcement Phase**: Policy engine decides to allow/block based on rules

Example decision engine integration:

```python
import json

with open('audit_report.json') as f:
    report = json.load(f)

# Apply your policy rules
if report['toxicity_score'] > 0.7:
    # Block deployment
    raise Exception("Toxicity threshold exceeded")

if len(report['api_misuse_flags']) > 0:
    # Require manual review
    notify_reviewers(report)
```

## Policy Enforcement

**This audit is non-blocking by default.** To enforce blocking:

1. Set `AUDIT_MODE=blocking` in your configuration
2. Configure CI/CD to fail on non-zero exit code
3. Or implement a separate policy engine that reads `audit_report.json`

### GitHub Actions Example

```yaml
- name: Run audit in blocking mode
  run: |
    python tools/grok4_audit.py --mode blocking
  # This will fail the step if issues are detected
```

## Extending the Pipeline

The audit pipeline is designed to be modular. To add custom checks:

```python
from tools.grok4_audit import AuditCheck, AuditResult, AuditPipeline

class CustomCheck(AuditCheck):
    @property
    def name(self) -> str:
        return "custom_check"
    
    def run(self, data: dict) -> AuditResult:
        # Your check logic here
        return AuditResult(
            check_name=self.name,
            passed=True,
            score=0.0,
            details="Custom check passed",
            flags=[]
        )

# Use in pipeline
pipeline = AuditPipeline(mode="audit-only")
pipeline.add_check(CustomCheck())
report = pipeline.run(data)
```

## Security Considerations

- No secrets are stored in code
- API endpoints are configurable via environment variables
- Kubernetes resources use minimal RBAC permissions
- CronJob is suspended by default (opt-in required)
- Container runs as non-root with read-only filesystem

## Troubleshooting

### Common Issues

**Audit always passes with score 0**

This is expected for the placeholder implementation. In production, configure
the actual Grok API endpoint and credentials.

**CronJob not running**

Check if it's still suspended:
```bash
kubectl get cronjob grok4-audit-cronjob -n evo-fast -o jsonpath='{.spec.suspend}'
```

**Missing darwin-results**

Ensure the darwin-results ConfigMap or artifact exists:
```bash
kubectl get configmap darwin-results -n evo-fast
```

## License

MIT License - See LICENSE file for details.
