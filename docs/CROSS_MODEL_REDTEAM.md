# Cross-Model Red Teaming

This document describes the cross-model red-teaming system that automatically audits every Darwin winner before promotion.

## Overview

The cross-model red-teaming system provides automated security and safety audits for code and model outputs that are selected as "Darwin winners" in the evolutionary optimization pipeline. The system uses Grok-4-Heavy style automated audits to detect:

- **Toxicity**: Harmful, offensive, or inappropriate content
- **Hallucination**: Factually incorrect or fabricated information  
- **API Misuse**: Security vulnerabilities and improper API usage patterns

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cross-Model Red Team System                   │
│                                                                  │
│  ┌────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │ Darwin Winner  │───▶│   Grok-4 Audit  │───▶│   Decision   │ │
│  │   Artifact     │    │     Engine      │    │    Engine    │ │
│  └────────────────┘    └─────────────────┘    └──────────────┘ │
│                              │                       │          │
│                              │                       ▼          │
│                              │              ┌──────────────┐   │
│                              │              │ PASS / FLAG  │   │
│                              │              │    / DENY    │   │
│                              ▼              └──────────────┘   │
│                     ┌─────────────────┐                        │
│                     │  Audit Results  │                        │
│                     │     (JSON)      │                        │
│                     └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### 1. GitHub Actions Workflow

**File**: `.github/workflows/cross-model-redteam.yml`

Triggers automatically when:
- Any workflow completes (checks for `darwin-results` artifact)
- Manual dispatch with configurable parameters

### 2. Audit Script

**File**: `tools/grok4_audit.py`

Python script that performs the actual audits:
- Pattern-based detection for toxicity, API misuse, and hallucination indicators
- Configurable thresholds and sensitivity
- JSON output with detailed findings

### 3. Kubernetes CronJob

**File**: `k8s/cron-grok4-audit.yaml`

For running audits in-cluster:
- Scheduled execution (default: every 6 hours)
- Resource limits for large-scale audits
- Persistent storage for audit results

## Running Locally

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/Teamintelxsel/Evolving-sun.git
cd Evolving-sun

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Audit a directory
python tools/grok4_audit.py --input-dir ./my-code --output-file ./results.json

# Audit a single file
python tools/grok4_audit.py --input-file ./candidate.py --output-file ./results.json

# Run in blocking mode (fails on issues)
python tools/grok4_audit.py --input-dir ./code --mode blocking

# Use external audit API
export GROK4_AUDIT_ENDPOINT="https://api.example.com/audit"
export GROK4_API_KEY="your-api-key"
python tools/grok4_audit.py --input-dir ./code --endpoint "$GROK4_AUDIT_ENDPOINT"

# Output to stdout as JSON
python tools/grok4_audit.py --input-dir ./code --json

# Quiet mode (no output except errors)
python tools/grok4_audit.py --input-dir ./code --quiet
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-dir` | Directory containing files to audit | None |
| `--input-file` | Single file to audit | None |
| `--output-file` | Output file for results | `./audit-results.json` |
| `--mode` | `audit-only` or `blocking` | `audit-only` |
| `--endpoint` | External audit API endpoint | None |
| `--json` | Output JSON to stdout | False |
| `--quiet` | Suppress non-error output | False |

## Required Compute

### Local Development

- **Minimum**: 2 CPU cores, 4GB RAM
- **Recommended**: 4 CPU cores, 8GB RAM

### GitHub Actions

- Uses `ubuntu-latest` runner
- Typical runtime: 1-5 minutes depending on artifact size

### Kubernetes In-Cluster

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 250m | 1000m |
| Memory | 512Mi | 2Gi |
| Storage | 1Gi PVC | - |

For large-scale audits, adjust resources in `k8s/cron-grok4-audit.yaml`:

```yaml
resources:
  limits:
    memory: "4Gi"
    cpu: "2000m"
  requests:
    memory: "1Gi"
    cpu: "500m"
```

## Decision Engine Integration

The audit produces three possible decisions that can be used by downstream systems:

### Decision Types

| Decision | Meaning | Action |
|----------|---------|--------|
| `pass` | No issues detected | Promotion allowed |
| `flag` | Issues detected, needs review | Promotion allowed (with warning) |
| `deny` | Critical issues detected | Promotion blocked (if configured) |

### Safety Flags

The audit result includes detailed safety flags:

```json
{
  "safety_flags": {
    "toxicity": false,
    "hallucination": false,
    "api_misuse": true,
    "toxicity_score": 0.0,
    "hallucination_score": 0.1,
    "api_misuse_score": 0.4
  }
}
```

### Using Results in Decision Engine

Example integration:

```python
import json

def evaluate_promotion(audit_result_path: str, policy: dict) -> bool:
    """
    Evaluate whether to allow promotion based on audit results.
    
    Args:
        audit_result_path: Path to audit-results.json
        policy: Policy configuration dict
    
    Returns:
        True if promotion is allowed, False otherwise
    """
    with open(audit_result_path) as f:
        result = json.load(f)
    
    decision = result.get('decision', 'pass')
    
    # Deny blocks promotion if policy requires it
    if decision == 'deny' and policy.get('block_on_deny', False):
        return False
    
    # Flag may block based on specific flag types
    if decision == 'flag':
        flags = result.get('safety_flags', {})
        if flags.get('toxicity') and policy.get('block_on_toxicity', False):
            return False
        if flags.get('api_misuse') and policy.get('block_on_api_misuse', False):
            return False
    
    return True
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GROK4_AUDIT_ENDPOINT` | External audit API endpoint | None |
| `GROK4_API_KEY` | API key for external service | None |
| `AUDIT_TIMEOUT` | API call timeout (seconds) | 30 |
| `AUDIT_MODE` | Default audit mode | `audit-only` |
| `BLOCK_ON_VIOLATION` | Block promotion on violations | `false` |

### GitHub Repository Variables

Set these in your repository settings under Settings → Secrets and variables → Actions → Variables:

- `GROK4_AUDIT_ENDPOINT`: External audit endpoint URL
- `BLOCK_ON_VIOLATION`: Set to `true` to enable blocking mode

### Kubernetes ConfigMap

Edit `k8s/cron-grok4-audit.yaml` ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grok4-audit-config
  namespace: evolving-sun
data:
  AUDIT_MODE: "blocking"  # Change from audit-only
  BLOCK_ON_VIOLATION: "true"
```

## Safe-by-Default Design

The system is designed to be **safe by default**:

1. **Audit-Only Mode**: Default mode does not block any promotions
2. **Opt-In Blocking**: Blocking must be explicitly enabled via policy
3. **Transparent Results**: All audit results are stored and accessible
4. **Manual Override**: Human reviewers can override audit decisions

To enable blocking:

```bash
# GitHub Actions
# Set repository variable: BLOCK_ON_VIOLATION=true

# Kubernetes
kubectl patch configmap grok4-audit-config -n evolving-sun \
  --type merge -p '{"data":{"BLOCK_ON_VIOLATION":"true"}}'

# Local
python tools/grok4_audit.py --mode blocking --input-dir ./code
```

## Troubleshooting

### Common Issues

**Audit not triggering on workflow completion**

Check that the triggering workflow produces an artifact named `darwin-results`:

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: darwin-results
    path: ./results/
```

**High false positive rate**

Adjust detection patterns in `tools/grok4_audit.py`:

```python
# Lower sensitivity for API misuse detection
API_MISUSE_PATTERNS = [
    # Comment out patterns that cause false positives
    # (r'eval\s*\(', 'dangerous_eval_usage'),
]
```

**Kubernetes job failing**

Check pod logs:

```bash
kubectl logs -n evolving-sun -l app.kubernetes.io/name=grok4-audit --tail=100
```

### Debug Mode

Enable verbose logging:

```bash
# Local
python tools/grok4_audit.py --input-dir ./code 2>&1 | tee debug.log

# GitHub Actions - check workflow run logs

# Kubernetes
kubectl logs -n evolving-sun job/grok4-audit-xxxxx -f
```

## Security Considerations

1. **API Keys**: Never commit API keys to the repository. Use secrets management.
2. **Audit Results**: Results may contain sensitive information. Control access appropriately.
3. **External APIs**: Validate that external audit endpoints are trusted.
4. **Resource Limits**: Set appropriate limits to prevent resource exhaustion attacks.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to this system.

## Related Documentation

- [SECURITY.md](../SECURITY.md) - Security policy
- [ARCHITECTURE.md](../ARCHITECTURE.md) - System architecture
- [AGENT_AUDIT.md](../AGENT_AUDIT.md) - Agent audit report

---

**Last Updated**: 2025-12-02  
**Version**: 1.0  
**Maintainer**: Evolving-sun Security Team
