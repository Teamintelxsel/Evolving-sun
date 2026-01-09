#!/usr/bin/env python3
"""
Feedback Analyzer

Analyzes repository performance and generates recommendations for improvement.

Analyzes:
- Which workflows succeed/fail most
- Which issues resolve fastest
- Which agents perform best
- Which automations provide most value

Generates recommendations:
- Workflow optimization suggestions
- Resource allocation adjustments
- Priority recalibrations
- New automation opportunities

Posts monthly analysis to GitHub Discussions.
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

try:
    from github import Github
except ImportError:
    print("PyGithub not installed. Installing...")
    os.system("pip install PyGithub")
    from github import Github


def analyze_workflows(repo):
    """Analyze workflow performance."""
    print("Analyzing workflow performance...")
    
    workflows = list(repo.get_workflows())
    workflow_analysis = []
    
    for workflow in workflows:
        runs = list(workflow.get_runs()[:50])  # Last 50 runs
        
        if not runs:
            continue
        
        success_count = sum(1 for run in runs if run.conclusion == 'success')
        failure_count = sum(1 for run in runs if run.conclusion == 'failure')
        total = len(runs)
        
        # Calculate average duration
        durations = [run.run_started_at and (run.updated_at - run.run_started_at).total_seconds() 
                    for run in runs if run.run_started_at]
        avg_duration = sum(d for d in durations if d) / len([d for d in durations if d]) if durations else 0
        
        workflow_analysis.append({
            'name': workflow.name,
            'success_rate': round(success_count / total * 100, 2) if total > 0 else 0,
            'total_runs': total,
            'avg_duration_seconds': round(avg_duration, 2),
            'failure_count': failure_count
        })
    
    # Sort by failure count
    workflow_analysis.sort(key=lambda x: x['failure_count'], reverse=True)
    
    return workflow_analysis


def analyze_issues(repo):
    """Analyze issue resolution patterns."""
    print("Analyzing issue resolution patterns...")
    
    # Get closed issues from last 30 days
    since = datetime.now() - timedelta(days=30)
    issues = list(repo.get_issues(state='closed', since=since))[:100]
    
    resolution_times = []
    by_label = defaultdict(list)
    
    for issue in issues:
        if issue.created_at and issue.closed_at:
            resolution_time = (issue.closed_at - issue.created_at).total_seconds() / 3600  # hours
            resolution_times.append(resolution_time)
            
            # Track by label
            for label in issue.labels:
                by_label[label.name].append(resolution_time)
    
    avg_resolution = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    label_stats = {}
    for label, times in by_label.items():
        if len(times) >= 3:  # At least 3 issues
            label_stats[label] = {
                'count': len(times),
                'avg_resolution_hours': round(sum(times) / len(times), 2)
            }
    
    return {
        'avg_resolution_hours': round(avg_resolution, 2),
        'total_resolved': len(resolution_times),
        'by_label': label_stats
    }


def analyze_security(repo):
    """Analyze security scan results."""
    print("Analyzing security performance...")
    
    # Look for security workflow runs
    workflows = list(repo.get_workflows())
    security_workflow = None
    
    for workflow in workflows:
        if 'security' in workflow.name.lower():
            security_workflow = workflow
            break
    
    if security_workflow:
        runs = list(security_workflow.get_runs()[:20])
        success_count = sum(1 for run in runs if run.conclusion == 'success')
        total = len(runs)
        
        return {
            'scan_success_rate': round(success_count / total * 100, 2) if total > 0 else 0,
            'total_scans': total,
            'issues_found': 0  # Would parse from workflow logs
        }
    
    return {
        'scan_success_rate': 0,
        'total_scans': 0,
        'issues_found': 0
    }


def generate_recommendations(workflow_analysis, issue_analysis, security_analysis):
    """Generate improvement recommendations."""
    print("Generating recommendations...")
    
    recommendations = []
    
    # Workflow recommendations
    failing_workflows = [w for w in workflow_analysis if w['success_rate'] < 90]
    if failing_workflows:
        for workflow in failing_workflows[:3]:
            recommendations.append({
                'title': f"Improve {workflow['name']} reliability",
                'priority': 'High' if workflow['success_rate'] < 70 else 'Medium',
                'category': 'Workflow Optimization',
                'description': f"Workflow has {workflow['success_rate']}% success rate",
                'rationale': f"Low success rate indicates potential issues with workflow logic or dependencies",
                'actions': f"- Review recent failures\n- Add error handling\n- Improve dependency management\n- Add retry logic",
                'impact': f"Could improve overall workflow success rate by reducing {workflow['failure_count']} failures"
            })
    
    # Issue resolution recommendations
    if issue_analysis['avg_resolution_hours'] > 168:  # 7 days
        recommendations.append({
            'title': 'Reduce average issue resolution time',
            'priority': 'High',
            'category': 'Process Improvement',
            'description': f"Average resolution time is {round(issue_analysis['avg_resolution_hours']/24, 1)} days",
            'rationale': 'Long resolution times may indicate bottlenecks or resource constraints',
            'actions': '- Improve issue triage\n- Add more automation\n- Better resource allocation\n- Clearer issue templates',
            'impact': 'Faster resolution improves contributor satisfaction and project velocity'
        })
    
    # Slow label categories
    slow_labels = {k: v for k, v in issue_analysis['by_label'].items() 
                   if v['avg_resolution_hours'] > 200}  # >8 days
    if slow_labels:
        for label, stats in list(slow_labels.items())[:2]:
            recommendations.append({
                'title': f"Optimize handling of '{label}' issues",
                'priority': 'Medium',
                'category': 'Process Improvement',
                'description': f"Issues with '{label}' take {round(stats['avg_resolution_hours']/24, 1)} days on average",
                'rationale': 'This category takes longer than average to resolve',
                'actions': f"- Review {stats['count']} recent {label} issues\n- Identify common patterns\n- Add specialized automation\n- Improve documentation",
                'impact': 'Could reduce resolution time by 30-50% for this category'
            })
    
    # Security recommendations
    if security_analysis['scan_success_rate'] < 95:
        recommendations.append({
            'title': 'Improve security scan reliability',
            'priority': 'High',
            'category': 'Security',
            'description': f"Security scans have {security_analysis['scan_success_rate']}% success rate",
            'rationale': 'Reliable security scanning is critical for repository safety',
            'actions': '- Review scan failures\n- Update security tools\n- Improve error handling\n- Add fallback mechanisms',
            'impact': 'Ensures consistent security coverage for all code changes'
        })
    
    # Resource optimization recommendations
    slow_workflows = [w for w in workflow_analysis if w['avg_duration_seconds'] > 600]  # >10 minutes
    if slow_workflows:
        for workflow in slow_workflows[:2]:
            recommendations.append({
                'title': f"Optimize {workflow['name']} execution time",
                'priority': 'Low',
                'category': 'Performance',
                'description': f"Average execution time is {round(workflow['avg_duration_seconds']/60, 1)} minutes",
                'rationale': 'Long-running workflows consume resources and slow feedback',
                'actions': '- Add caching\n- Parallelize steps\n- Optimize dependencies\n- Consider workflow splitting',
                'impact': 'Could reduce CI/CD time by 20-40%'
            })
    
    # Always add a general monitoring recommendation
    recommendations.append({
        'title': 'Enhance monitoring and metrics collection',
        'priority': 'Low',
        'category': 'Observability',
        'description': 'Expand metrics collection for better insights',
        'rationale': 'Better metrics enable data-driven decisions',
        'actions': '- Add custom metrics\n- Improve dashboard visualizations\n- Track additional KPIs\n- Set up alerting thresholds',
        'impact': 'Enables proactive issue detection and faster troubleshooting'
    })
    
    return recommendations


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze repository feedback and generate recommendations')
    parser.add_argument('--output', default='reports/feedback_analysis.json', help='Output file path')
    args = parser.parse_args()
    
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print("Error: GITHUB_TOKEN not set")
        sys.exit(1)
    
    repo_name = os.environ.get('GITHUB_REPOSITORY', 'Teamintelxsel/Evolving-sun')
    
    print(f"Analyzing repository: {repo_name}")
    g = Github(token)
    repo = g.get_repo(repo_name)
    
    # Perform analyses
    workflow_analysis = analyze_workflows(repo)
    issue_analysis = analyze_issues(repo)
    security_analysis = analyze_security(repo)
    
    # Generate recommendations
    recommendations = generate_recommendations(workflow_analysis, issue_analysis, security_analysis)
    
    # Compile analysis report
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'period': '30 days',
        'workflow_analysis': workflow_analysis,
        'issue_analysis': issue_analysis,
        'security_analysis': security_analysis,
        'recommendations': recommendations,
        'summary': {
            'total_workflows_analyzed': len(workflow_analysis),
            'avg_workflow_success_rate': round(sum(w['success_rate'] for w in workflow_analysis) / len(workflow_analysis), 2) if workflow_analysis else 0,
            'issues_resolved': issue_analysis['total_resolved'],
            'avg_resolution_hours': issue_analysis['avg_resolution_hours'],
            'total_recommendations': len(recommendations)
        }
    }
    
    # Save report
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete!")
    print(f"Report saved to: {output_path}")
    print(f"\nSummary:")
    print(f"  - Workflows analyzed: {report['summary']['total_workflows_analyzed']}")
    print(f"  - Avg workflow success: {report['summary']['avg_workflow_success_rate']}%")
    print(f"  - Issues resolved: {report['summary']['issues_resolved']}")
    print(f"  - Avg resolution time: {round(report['summary']['avg_resolution_hours']/24, 1)} days")
    print(f"  - Recommendations generated: {report['summary']['total_recommendations']}")


if __name__ == '__main__':
    main()
