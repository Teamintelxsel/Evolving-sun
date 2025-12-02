# Cross-Model Red Teaming - Maintainer Guide

This README is for maintainers of the cross-model red-teaming system.

## Quick Start

```bash
# Run tests
pytest tests/test_grok4_audit.py -v

# Run the audit tool locally
python tools/grok4_audit.py --input-dir ./tools --output-file /tmp/test-audit.json

# Deploy Kubernetes resources
kubectl apply -f k8s/cron-grok4-audit.yaml
```

## Repository Structure

```
Evolving-sun/
├── .github/workflows/
│   └── cross-model-redteam.yml   # GitHub Actions workflow
├── tools/
│   └── grok4_audit.py            # Main audit script
├── k8s/
│   └── cron-grok4-audit.yaml     # Kubernetes CronJob
├── docs/
│   └── CROSS_MODEL_REDTEAM.md    # User documentation
└── tests/
    └── test_grok4_audit.py       # Unit tests
```

## Maintenance Tasks

### Updating Detection Patterns

Edit `tools/grok4_audit.py`:

```python
# Add new toxicity patterns
TOXICITY_PATTERNS = [
    (r'your_new_pattern', 'pattern_name'),
    ...
]

# Add new API misuse patterns
API_MISUSE_PATTERNS = [
    (r'your_new_pattern', 'pattern_name'),
    ...
]
```

After updating patterns:
1. Add corresponding tests in `tests/test_grok4_audit.py`
2. Run the test suite: `pytest tests/test_grok4_audit.py -v`
3. Test locally with sample code

### Updating the Workflow

The workflow is in `.github/workflows/cross-model-redteam.yml`.

Key sections:
- **Triggers**: `on:` section controls when the workflow runs
- **Environment**: `env:` section for default configuration
- **Jobs**: `check-artifact` and `audit-darwin-winner` are the main jobs

### Updating Kubernetes Resources

The K8s manifest is in `k8s/cron-grok4-audit.yaml`.

To update the schedule:
```yaml
spec:
  schedule: "0 */6 * * *"  # Every 6 hours
```

To update resources:
```yaml
resources:
  limits:
    memory: "4Gi"   # Increase for larger audits
    cpu: "2000m"
```

## Testing

### Running Tests

```bash
# All tests
pytest tests/test_grok4_audit.py -v

# Specific test class
pytest tests/test_grok4_audit.py::TestCheckApiMisuse -v

# With coverage
pytest tests/test_grok4_audit.py --cov=tools/grok4_audit
```

### Manual Testing

```bash
# Create test file with known issues
echo 'password = "secret123"' > /tmp/test.py

# Run audit
python tools/grok4_audit.py --input-file /tmp/test.py --json

# Expected output includes api_misuse flag
```

### Integration Testing

1. Create a test workflow that uploads a `darwin-results` artifact
2. Verify the cross-model-redteam workflow triggers
3. Check the `grok4-audit-results` artifact

## Troubleshooting

### Workflow Not Triggering

1. Verify the artifact name matches `darwin-results`
2. Check workflow permissions in repository settings
3. Ensure the triggering workflow completed (not cancelled)

### False Positives

1. Review the patterns in `grok4_audit.py`
2. Consider adding exceptions for legitimate use cases
3. Adjust score thresholds if needed

### Kubernetes Issues

```bash
# Check CronJob status
kubectl get cronjobs -n evolving-sun

# Check job history
kubectl get jobs -n evolving-sun

# View pod logs
kubectl logs -n evolving-sun -l app.kubernetes.io/name=grok4-audit --tail=100

# Describe for errors
kubectl describe pod -n evolving-sun -l app.kubernetes.io/name=grok4-audit
```

## Security Considerations

1. **Never commit secrets**: All API keys must use GitHub secrets or K8s secrets
2. **Audit results privacy**: Results may contain sensitive code snippets
3. **External API trust**: Validate endpoints before enabling external audits
4. **RBAC**: K8s service account has minimal required permissions

## Release Process

1. Update version in `tools/grok4_audit.py`
2. Update version in `docs/CROSS_MODEL_REDTEAM.md`
3. Run full test suite
4. Update CHANGELOG
5. Create PR and request review

## Dependencies

- Python 3.9+
- pytest 7.0+ (for testing)
- No external Python packages required for core functionality

## Contact

For questions or issues:
- Create an issue in this repository
- Reference `CROSS_MODEL_REDTEAM.md` for user-facing questions
- See `CONTRIBUTING.md` for contribution guidelines

---

**Last Updated**: 2025-12-02
