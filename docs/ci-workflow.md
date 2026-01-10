# CI/CD Workflow Documentation

## Weekly Benchmark CI

### Overview

The `weekly-benchmarks.yml` workflow automates the execution of benchmark harnesses on a weekly schedule. This ensures continuous monitoring of model performance and catches any regressions.

### Workflow Triggers

1. **Scheduled Run**: Every Monday at 00:00 UTC
   - Automatically runs GPQA and KEGG benchmarks
   - Results are archived for 90 days

2. **Manual Trigger**: Via GitHub Actions UI
   - Allows custom benchmark selection
   - Configurable sample sizes
   - Useful for ad-hoc testing

### Security Audit Fixes Applied

The workflow incorporates industry best practices for CI/CD security:

#### ✅ Minimal Permissions
```yaml
permissions:
  contents: read
  actions: read
```
- Only read access to repository and actions
- Follows principle of least privilege
- Prevents accidental/malicious modifications

#### ✅ Version Pinning
All actions are pinned to specific versions:
- `actions/checkout@v4.2.2`
- `actions/setup-python@v5.3.0`
- `actions/cache@v4.2.0`
- `actions/upload-artifact@v4.5.0`

Benefits:
- Reproducible builds
- Protection against supply chain attacks
- Controlled updates

#### ✅ Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```
- Prevents multiple simultaneous runs
- Saves CI resources
- Avoids result conflicts

#### ✅ Dependency Caching
```yaml
- uses: actions/cache@v4.2.0
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```
- Faster builds (30-60% speedup)
- Reduced network usage
- More reliable in case of registry issues

#### ✅ Timeouts
```yaml
timeout-minutes: 120
```
- Prevents runaway jobs
- Ensures resource cleanup
- Protects against infinite loops

### Workflow Steps

1. **Checkout**: Clone repository with submodules
2. **Setup Python**: Install Python 3.11 with pip caching
3. **Install Dependencies**: Install from requirements.txt
4. **Run Benchmarks**: Execute selected harnesses
5. **Archive Results**: Upload artifacts for 90 days
6. **Display Summary**: Show key metrics

### Benchmark Orchestration

#### Scale Constraints

To ensure realistic and sustainable CI runs:

- **GPQA**: Default 50 samples (configurable)
- **KEGG**: 2-3 pathways (glycolysis, TCA cycle)
- **SWE-Bench**: Disabled by default (requires Docker setup)

These limits keep execution time under 30 minutes while providing meaningful results.

### Results Archiving

All results are:
1. **Watermarked** with secure hash
2. **Timestamped** with UTC timestamp
3. **Archived** as GitHub Actions artifacts
4. **Retained** for 90 days

Access archived results:
- Go to Actions → Weekly Benchmark CI
- Select a workflow run
- Download artifacts from "Summary" page

### Manual Trigger Parameters

When manually triggering the workflow:

**benchmarks** (string):
- Comma-separated list: `swe,gpqa,kegg` or `all`
- Default: `gpqa,kegg`
- Examples:
  - `gpqa` - Run only GPQA
  - `kegg` - Run only KEGG
  - `gpqa,kegg` - Run both
  - `all` - Run all available

**max_samples** (number):
- Maximum samples for GPQA
- Default: 50
- Range: 1-1000 (higher values increase runtime)

### Extending the Workflow

#### Adding a New Benchmark

1. Add a new step in the workflow:
```yaml
- name: Run New Benchmark
  id: new_benchmark
  run: |
    python scripts/new_benchmark_run.py \
      --output logs/benchmarks/new_results.json
  continue-on-error: true
```

2. Update the summary step to include new metrics

3. (Optional) Add manual trigger parameters

#### Adding Path Filters for PR Triggers

To run benchmarks on PRs when specific files change:

```yaml
on:
  pull_request:
    paths:
      - 'scripts/**'
      - 'src/**'
      - 'requirements.txt'
      - '.github/workflows/weekly-benchmarks.yml'
```

This prevents unnecessary runs when only docs change.

### Troubleshooting

**Workflow fails immediately**:
- Check action versions are accessible
- Verify Python version availability
- Check submodule initialization

**Benchmark times out**:
- Reduce sample sizes
- Increase timeout-minutes
- Check for network issues

**Results not archived**:
- Verify `logs/benchmarks/` directory exists
- Check file paths in upload-artifact step
- Ensure JSON files are generated

**Dependencies fail to install**:
- Check requirements.txt syntax
- Verify package availability on PyPI
- Check for conflicting versions

### Monitoring and Alerts

To set up alerts for failed runs:

1. Go to repository Settings → Notifications
2. Enable "Actions" notifications
3. Choose notification method (email/app)

Or use GitHub's workflow status API:
```bash
gh api repos/Teamintelxsel/Evolving-sun/actions/workflows/weekly-benchmarks.yml/runs
```

### Cost Optimization

The workflow is optimized for cost:
- Caching reduces redundant downloads
- Timeouts prevent runaway costs
- Concurrency control limits parallel runs
- Artifact retention limited to 90 days
- Compression level 9 for artifact storage

Estimated usage:
- ~30 minutes/week for scheduled runs
- ~100 MB storage for artifacts
- Well within free tier limits

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [Usage Examples](../examples/usage_examples.py) - Example scripts
- [GitHub Actions Docs](https://docs.github.com/en/actions)
