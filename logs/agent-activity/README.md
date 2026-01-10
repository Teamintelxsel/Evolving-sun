# Agent Activity Logs

This directory tracks agent behaviors, interactions, and activity patterns.

## Purpose

Agent activity logs document:
- Interaction patterns
- Decision-making processes
- Task execution sequences
- Error and recovery scenarios
- Learning events

## Log Format

Activity logs can be structured (JSON) or narrative (Markdown):

### JSON Format
```json
{
  "timestamp": "2026-01-10T01:00:00Z",
  "agent_id": "agent-001",
  "activity_type": "task_execution",
  "task": "code_review",
  "duration_ms": 5000,
  "outcome": "success",
  "details": {
    "files_reviewed": 5,
    "issues_found": 2
  }
}
```

### Markdown Format
```markdown
# Agent Activity Log

**Date**: YYYY-MM-DD HH:MM:SS UTC
**Agent ID**: agent-001
**Activity Type**: [Task Execution|Learning|Error Recovery|Interaction]

## Context
What was the agent trying to accomplish?

## Actions Taken
Sequence of actions the agent performed

## Outcome
Result of the activity

## Observations
Notable patterns or behaviors
```

## Naming Convention

Files should be named: `YYYY-MM-DD-activity-type.md` or `.json`

Example: `2026-01-10-code-review-session.json`
