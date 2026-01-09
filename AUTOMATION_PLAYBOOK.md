# Automation Playbook

## Overview

This playbook defines the autonomous capabilities of the Evolving-sun repository, including automated tasks, human approval requirements, and escalation procedures.

## Autonomous Tasks

### Daily Operations

#### 1. Issue Triage (Continuous)
**Workflow:** `issue-triage-automation.yml`
**Trigger:** Issue creation or update
**Actions:**
- Auto-label based on content analysis
- Assign priority levels
- Link related issues
- Detect and mark duplicates
- Welcome first-time contributors
- Request clarification when needed

**No Human Approval Required**

#### 2. Daily Task Review (Daily at 00:00 UTC)
**Workflow:** `daily-task-review.yml`
**Trigger:** Scheduled daily
**Actions:**
- Scan all open issues and PRs
- Categorize by priority
- Identify stale items (>30 days)
- Generate summary report
- Alert on critical items

**No Human Approval Required**

#### 3. Issue Cleanup (Daily at 06:00 UTC)
**Workflow:** `issue-cleanup.yml`
**Trigger:** Scheduled daily
**Actions:**
- Mark inactive issues as stale
- Request clarification on unclear issues
- Auto-close issues stale for 44+ days
- Close duplicate issues after 7 days

**No Human Approval Required**

### Security Operations

#### 4. Security Monitoring (On Every Push/PR)
**Workflow:** `security-monitoring.yml`
**Trigger:** Push or pull request
**Actions:**
- Scan for secrets and credentials
- Run bandit security analysis
- Execute CodeQL analysis
- Check for common vulnerabilities
- Create security issues for findings
- Block PRs with critical issues

**Auto-blocks PRs with critical security issues**

#### 5. Cross-Model Audit (Weekly on Friday)
**Workflow:** `cross-model-audit.yml`
**Trigger:** Scheduled weekly
**Actions:**
- Execute multi-model auditing
- Toxicity scoring
- Hallucination detection
- API misuse detection
- Generate audit reports

**No Human Approval Required**

### Quality Assurance

#### 6. Benchmark Automation (Weekly on Sunday)
**Workflow:** `benchmark-automation.yml`
**Trigger:** Scheduled weekly
**Actions:**
- Execute KEGG pathway benchmarks
- Run SWE-bench tests
- Verify GPQA accuracy
- Generate SHA256 hashes
- Create Merkle roots for verification
- Update BENCHMARKS.md
- Commit results to repository

**Auto-commits to main branch**

### Monitoring and Analysis

#### 7. Dashboard Updates (Every 6 Hours)
**Workflow:** `update-dashboard.yml`
**Trigger:** Scheduled every 6 hours
**Actions:**
- Collect repository metrics
- Generate health dashboard
- Update docs/dashboard.html
- Alert on significant changes
- Commit dashboard updates

**Auto-commits to main branch**

#### 8. Feedback Loop (Monthly on 1st)
**Workflow:** `feedback-loop.yml`
**Trigger:** Scheduled monthly
**Actions:**
- Analyze workflow performance
- Identify improvement opportunities
- Generate recommendations
- Create improvement issues
- Commit analysis reports

**Auto-creates issues for improvements**

## Human-Required Approvals

### Critical Decisions

1. **PR Merges to Main Branch**
   - All pull requests require human review
   - Approval from at least one maintainer
   - All CI checks must pass
   - Security scans must be clean

2. **Security Policy Changes**
   - Modifications to security workflows
   - Changes to secret scanning configuration
   - Updates to CodeQL queries
   - Requires security team review

3. **Benchmark Baseline Updates**
   - Changes to benchmark targets
   - Modifications to verification logic
   - Updates to acceptance criteria
   - Requires maintainer approval

4. **External API Integrations**
   - Adding new external services
   - Modifying API credentials
   - Changing rate limits
   - Requires security and architecture review

5. **Workflow Modifications**
   - Adding new automation workflows
   - Modifying existing workflow logic
   - Changing schedule or triggers
   - Requires DevOps review

### Administrative Actions

1. **Repository Settings**
   - Branch protection rules
   - Collaborator permissions
   - Webhook configurations
   - Requires admin approval

2. **Label Management**
   - Creating new label categories
   - Modifying label colors/descriptions
   - Requires maintainer approval

3. **Release Management**
   - Creating new releases
   - Publishing packages
   - Requires release manager approval

## Escalation Procedures

### Level 1: Automated Response
**Trigger:** Low-priority issues, routine tasks
**Action:** Automated workflows handle completely
**Timeline:** Immediate to 24 hours
**Example:** Auto-labeling, stale issue marking

### Level 2: Notification
**Trigger:** Medium-priority issues, workflow warnings
**Action:** Notify via issue comment or summary
**Timeline:** Next business day
**Example:** Stale issue warnings, benchmark variations

### Level 3: Alert
**Trigger:** High-priority issues, workflow failures
**Action:** Create issue with high priority label
**Timeline:** Within 6 hours
**Example:** Workflow failures, benchmark degradation >5%

### Level 4: Critical Escalation
**Trigger:** Critical security findings, system failures
**Action:** Immediate notification + issue creation
**Timeline:** Immediate
**Example:** Secret leaks, critical vulnerabilities

### Escalation Matrix

| Finding Type | Severity | Auto-Action | Human Review | Timeline |
|--------------|----------|-------------|--------------|----------|
| Secret detected | Critical | Block PR, Create issue | Required | Immediate |
| High-severity vulnerability | Critical | Create issue | Required | <1 hour |
| Benchmark degradation >10% | High | Create issue | Required | <6 hours |
| Workflow failure | High | Create issue | Recommended | <24 hours |
| Stale issue (>30 days) | Medium | Add label, Comment | Optional | 14 days |
| Duplicate issue | Low | Mark duplicate | Optional | 7 days |

## Workflow Success Metrics

### Performance Targets

| Workflow | Success Rate | Execution Time | Action Required |
|----------|--------------|----------------|-----------------|
| issue-triage-automation | >99% | <30 seconds | If <95% |
| daily-task-review | >98% | <2 minutes | If <95% |
| security-monitoring | >95% | <5 minutes | If <90% |
| benchmark-automation | >90% | <30 minutes | If <85% |
| cross-model-audit | >85% | <15 minutes | If <80% |
| update-dashboard | >98% | <1 minute | If <95% |
| feedback-loop | >95% | <5 minutes | If <90% |

### Monitoring

- Track success/failure rate for each workflow
- Monitor execution time trends
- Alert on degradation >10%
- Monthly review of all metrics
- Quarterly optimization review

## Agent Responsibilities

### Security Agent
**Priority:** Critical
**Workflows:** 
- security-monitoring.yml
- cross-model-audit.yml

**Responsibilities:**
- Monitor all security scans
- Triage security findings
- Escalate critical vulnerabilities
- Track remediation progress

**Escalation Threshold:** Any critical finding

### Quality Agent
**Priority:** High
**Workflows:**
- daily-task-review.yml
- issue-triage-automation.yml

**Responsibilities:**
- Manage issue lifecycle
- Ensure proper labeling
- Track resolution times
- Identify bottlenecks

**Escalation Threshold:** Benchmark degradation >5%

### Documentation Agent
**Priority:** Medium
**Workflows:**
- update-dashboard.yml

**Responsibilities:**
- Maintain documentation currency
- Update dashboards and reports
- Track documentation coverage
- Identify gaps

**Escalation Threshold:** Outdated docs >30 days

### Benchmark Agent
**Priority:** High
**Workflows:**
- benchmark-automation.yml

**Responsibilities:**
- Execute benchmark tests
- Verify result integrity
- Track performance trends
- Report regressions

**Escalation Threshold:** Failed verification or >5% degradation

## Rate Limiting and Resource Management

### GitHub API Rate Limits
- Maximum 5,000 requests per hour
- Workflows implement exponential backoff
- Critical operations prioritized
- Non-critical operations batched

### Workflow Concurrency
- Maximum 5 concurrent workflow runs
- Critical workflows take priority
- Queue management for scheduled jobs
- Manual trigger always available

### Storage Management
- Artifacts retained for 90 days (critical) or 30 days (routine)
- Dashboard data: 12 months rolling
- Benchmark results: Permanent
- Audit reports: 24 months

## Dry-Run and Testing

### Dry-Run Mode
All workflows support dry-run mode via workflow_dispatch with inputs:
```yaml
workflow_dispatch:
  inputs:
    dry_run:
      description: 'Run in dry-run mode (no actual changes)'
      required: false
      default: 'false'
```

### Testing Procedures
1. Test new workflows in dry-run mode
2. Validate with sample data
3. Review outputs for correctness
4. Monitor first 3 live runs
5. Enable full automation

### Rollback Procedures
1. Disable workflow via workflow settings
2. Revert to previous workflow version
3. Create incident report issue
4. Fix and test in dry-run mode
5. Gradual re-enablement

## Maintenance Windows

### Scheduled Maintenance
- First Sunday of each month: 02:00-04:00 UTC
- Workflow updates and testing
- Infrastructure maintenance
- Performance optimization

### Emergency Maintenance
- Critical security updates: Immediate
- Workflow failures: <4 hours
- Infrastructure issues: <8 hours

## Support and Troubleshooting

### Workflow Failures
1. Check workflow run logs
2. Review recent changes
3. Check GitHub status
4. Validate credentials and permissions
5. Create issue if unresolved

### Common Issues

**Issue:** Workflow not triggering
- Check schedule syntax
- Verify branch protection rules
- Check workflow permissions

**Issue:** API rate limit exceeded
- Implement request batching
- Add delays between calls
- Use conditional execution

**Issue:** Authentication failures
- Verify GITHUB_TOKEN scope
- Check secret expiration
- Validate repository permissions

## Contributing to Automation

### Adding New Workflows
1. Create workflow in `.github/workflows/`
2. Follow naming convention: `kebab-case.yml`
3. Include dry-run capability
4. Add comprehensive comments
5. Document in this playbook
6. Test in dry-run mode
7. Submit PR for review

### Modifying Existing Workflows
1. Document reason for change
2. Test in dry-run mode
3. Monitor first 3 runs after deployment
4. Update documentation
5. Add to changelog

### Best Practices
- Use safe-by-default approach
- Implement comprehensive error handling
- Add logging for all operations
- Use secrets for credentials
- Minimize API calls
- Batch operations when possible
- Include rollback capability

## Audit and Compliance

### Automated Audit Trail
- All automated actions logged
- Issue comments track automation
- Workflow runs archived
- Changes committed with clear messages

### Compliance Requirements
- Security scans on all code changes
- Benchmark verification for all results
- Documentation for all automations
- Human approval for critical changes

### Regular Reviews
- Weekly: Security findings
- Monthly: Workflow performance
- Quarterly: Automation effectiveness
- Annually: Complete playbook review

---

**Last Updated:** 2026-01-09  
**Next Review:** 2026-02-09  
**Owner:** DevOps Team

*This playbook is a living document and should be updated as automation evolves.*
