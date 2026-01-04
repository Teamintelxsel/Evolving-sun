"""
Example Agent Integration for Evolving-sun
===========================================

Demonstrates how to integrate the audit system with AI agents.

Version: 1.0
"""

from comprehensive_audit import ComprehensiveAudit
from conversation_audit import ConversationAudit
from llm_audit_verifier import LLMAuditVerifier


class ExampleAgent:
    """
    Example AI agent with audit integration.
    
    This demonstrates how to integrate Evolving-sun's audit capabilities
    into custom AI agents.
    """
    
    def __init__(self, agent_id: str):
        """
        Initialize agent with audit capabilities.
        
        Args:
            agent_id: Unique identifier for this agent
        """
        self.agent_id = agent_id
        self.conversation_audit = ConversationAudit()
        self.llm_verifier = LLMAuditVerifier()
        
    def perform_task(self, task_description: str) -> dict:
        """
        Perform a task with audit logging.
        
        Args:
            task_description: Description of task to perform
            
        Returns:
            Task results with audit information
        """
        # Log the task start
        self.conversation_audit.log_conversation(
            self.agent_id,
            f"Starting task: {task_description}",
            "task-start"
        )
        
        # Simulate task execution
        result = {
            "agent_id": self.agent_id,
            "task": task_description,
            "status": "completed",
            "output": f"Task '{task_description}' completed successfully"
        }
        
        # Verify quality with LLM
        verification = self.llm_verifier.verify_code_quality(
            str(result),
            context=f"Agent {self.agent_id} task execution"
        )
        
        result["quality_verified"] = verification["verified"]
        result["quality_score"] = verification["quality_score"]
        
        # Log completion
        self.conversation_audit.log_conversation(
            self.agent_id,
            f"Completed task: {task_description}",
            "task-complete"
        )
        
        return result
    
    def get_audit_report(self) -> dict:
        """
        Get audit report for this agent's activities.
        
        Returns:
            Comprehensive audit report
        """
        return {
            "agent_id": self.agent_id,
            "conversation_quality": self.conversation_audit.analyze_quality(),
            "total_conversations": len(self.conversation_audit.conversations)
        }


def main():
    """
    Example usage of agent with audit integration.
    """
    print("="*60)
    print("EVOLVING-SUN AGENT INTEGRATION EXAMPLE")
    print("="*60)
    print()
    
    # Create example agent
    agent = ExampleAgent("example-agent-001")
    
    # Perform some tasks
    tasks = [
        "Review code changes in pull request",
        "Run security scan on repository",
        "Generate documentation for new API"
    ]
    
    for task in tasks:
        print(f"Executing: {task}")
        result = agent.perform_task(task)
        print(f"  Status: {result['status']}")
        print(f"  Quality Score: {result['quality_score']}%")
        print()
    
    # Get audit report
    print("="*60)
    print("AGENT AUDIT REPORT")
    print("="*60)
    audit_report = agent.get_audit_report()
    print(f"Agent ID: {audit_report['agent_id']}")
    print(f"Total Conversations: {audit_report['total_conversations']}")
    print(f"Conversation Quality Score: {audit_report['conversation_quality']['quality_score']}%")
    print()
    
    # Run repository-wide audit
    print("="*60)
    print("REPOSITORY AUDIT")
    print("="*60)
    repo_audit = ComprehensiveAudit()
    repo_audit.run()
    repo_audit.print_summary()


if __name__ == "__main__":
    main()
