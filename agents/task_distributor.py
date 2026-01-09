#!/usr/bin/env python3
"""
Multi-Agent Task Distributor

Assigns tasks to specialized agents:
- SecurityAgent: monitors security workflows
- QualityAgent: runs code quality checks
- DocAgent: maintains documentation
- BenchmarkAgent: validates benchmarks
- TriageAgent: manages issue lifecycle

Each agent has:
- Assigned responsibilities
- Escalation triggers
- Performance metrics
- Learning feedback loop
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class Agent:
    """Base class for specialized agents."""
    
    def __init__(self, name: str, priority: str, responsibilities: List[str]):
        self.name = name
        self.priority = priority
        self.responsibilities = responsibilities
        self.metrics = {
            'tasks_assigned': 0,
            'tasks_completed': 0,
            'escalations': 0,
            'avg_completion_time': 0
        }
    
    def assign_task(self, task: Dict) -> bool:
        """Assign a task to this agent."""
        if self._can_handle(task):
            self.metrics['tasks_assigned'] += 1
            return True
        return False
    
    def _can_handle(self, task: Dict) -> bool:
        """Check if agent can handle this task."""
        task_type = task.get('type', '')
        return any(resp in task_type for resp in self.responsibilities)
    
    def complete_task(self, task: Dict, success: bool = True):
        """Mark a task as completed."""
        if success:
            self.metrics['tasks_completed'] += 1
    
    def escalate(self, task: Dict, reason: str):
        """Escalate a task."""
        self.metrics['escalations'] += 1
        print(f"[{self.name}] Escalating task: {task.get('id')} - Reason: {reason}")
    
    def get_metrics(self) -> Dict:
        """Get agent performance metrics."""
        success_rate = 0
        if self.metrics['tasks_assigned'] > 0:
            success_rate = (self.metrics['tasks_completed'] / self.metrics['tasks_assigned'] * 100)
        
        return {
            'name': self.name,
            'priority': self.priority,
            'metrics': self.metrics,
            'success_rate': round(success_rate, 2)
        }


class SecurityAgent(Agent):
    """Agent responsible for security monitoring."""
    
    def __init__(self):
        super().__init__(
            name='SecurityAgent',
            priority='critical',
            responsibilities=['security', 'vulnerability', 'audit', 'secret']
        )
        self.escalation_threshold = 'any_critical_finding'


class QualityAgent(Agent):
    """Agent responsible for code quality."""
    
    def __init__(self):
        super().__init__(
            name='QualityAgent',
            priority='high',
            responsibilities=['quality', 'review', 'triage', 'issue']
        )
        self.escalation_threshold = 'benchmark_degradation_5pct'


class DocAgent(Agent):
    """Agent responsible for documentation."""
    
    def __init__(self):
        super().__init__(
            name='DocAgent',
            priority='medium',
            responsibilities=['documentation', 'docs', 'readme', 'guide']
        )
        self.escalation_threshold = 'outdated_docs_30days'


class BenchmarkAgent(Agent):
    """Agent responsible for benchmarks."""
    
    def __init__(self):
        super().__init__(
            name='BenchmarkAgent',
            priority='high',
            responsibilities=['benchmark', 'test', 'performance', 'metric']
        )
        self.escalation_threshold = 'failed_verification'


class TriageAgent(Agent):
    """Agent responsible for issue management."""
    
    def __init__(self):
        super().__init__(
            name='TriageAgent',
            priority='medium',
            responsibilities=['triage', 'label', 'assign', 'close']
        )
        self.escalation_threshold = 'stale_critical_issue'


class TaskDistributor:
    """Distributes tasks to appropriate agents."""
    
    def __init__(self):
        self.agents = [
            SecurityAgent(),
            QualityAgent(),
            DocAgent(),
            BenchmarkAgent(),
            TriageAgent()
        ]
    
    def distribute_task(self, task: Dict) -> Agent:
        """Distribute a task to the most appropriate agent."""
        # Sort agents by priority
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_agents = sorted(
            self.agents,
            key=lambda a: priority_order.get(a.priority, 99)
        )
        
        # Find first agent that can handle the task
        for agent in sorted_agents:
            if agent.assign_task(task):
                print(f"Task {task.get('id')} assigned to {agent.name}")
                return agent
        
        # Default to TriageAgent if no specific match
        print(f"Task {task.get('id')} assigned to default TriageAgent")
        self.agents[-1].assign_task(task)
        return self.agents[-1]
    
    def get_all_metrics(self) -> Dict:
        """Get metrics for all agents."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'agents': [agent.get_metrics() for agent in self.agents]
        }
    
    def save_metrics(self, filepath: str = 'agents/metrics.json'):
        """Save agent metrics to file."""
        metrics = self.get_all_metrics()
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        print(f"Metrics saved to {filepath}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Multi-Agent Task Distribution System")
    print("=" * 60)
    
    distributor = TaskDistributor()
    
    # Example tasks
    tasks = [
        {'id': 1, 'type': 'security_scan', 'priority': 'critical'},
        {'id': 2, 'type': 'benchmark_run', 'priority': 'high'},
        {'id': 3, 'type': 'documentation_update', 'priority': 'medium'},
        {'id': 4, 'type': 'issue_triage', 'priority': 'medium'},
        {'id': 5, 'type': 'quality_check', 'priority': 'high'},
    ]
    
    print("\nDistributing tasks to agents...")
    for task in tasks:
        agent = distributor.distribute_task(task)
        agent.complete_task(task, success=True)
    
    print("\n" + "=" * 60)
    print("Agent Performance Metrics")
    print("=" * 60)
    
    metrics = distributor.get_all_metrics()
    for agent_metrics in metrics['agents']:
        print(f"\n{agent_metrics['name']}:")
        print(f"  Priority: {agent_metrics['priority']}")
        print(f"  Tasks Assigned: {agent_metrics['metrics']['tasks_assigned']}")
        print(f"  Tasks Completed: {agent_metrics['metrics']['tasks_completed']}")
        print(f"  Success Rate: {agent_metrics['success_rate']}%")
        print(f"  Escalations: {agent_metrics['metrics']['escalations']}")
    
    # Save metrics
    distributor.save_metrics()
    
    print("\n✅ Task distribution complete!")


if __name__ == '__main__':
    main()
