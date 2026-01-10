"""Nano Agent - Individual agent in the mutation swarm."""

import logging
import random
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class NanoAgent:
    """Individual agent that applies mutations and learns from results."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        specialization: Optional[str] = None,
        learning_rate: float = 0.1,
    ) -> None:
        """Initialize a nano agent.

        Args:
            agent_id: Unique agent identifier (auto-generated if None)
            specialization: Agent specialization type
            learning_rate: Learning rate for fitness adaptation
        """
        self.agent_id = agent_id or f"agent_{uuid.uuid4().hex[:8]}"
        self.specialization = specialization or random.choice(
            [
                "function_decomposition",
                "code_optimization",
                "module_combination",
                "dead_code_removal",
            ]
        )
        self.learning_rate = learning_rate
        self.fitness = 0.5  # Initial fitness
        self.mutations_applied = 0
        self.successful_mutations = 0
        self.experience: list[Dict[str, Any]] = []

    def apply_mutation(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a mutation and learn from the result.

        Args:
            mutation: Mutation specification

        Returns:
            Mutation result
        """
        logger.info(f"Agent {self.agent_id} applying mutation: {mutation.get('id')}")

        # Simulate mutation application
        success = random.random() < self.fitness
        fitness_delta = random.uniform(-0.1, 0.3) if success else -0.05

        result = {
            "agent_id": self.agent_id,
            "mutation_id": mutation.get("id"),
            "success": success,
            "fitness_delta": fitness_delta,
            "specialization_match": mutation.get("operator") == self.specialization,
        }

        # Update agent state
        self.mutations_applied += 1
        if success:
            self.successful_mutations += 1

        # Learn from experience
        self._update_fitness(result)
        self.experience.append(result)

        return result

    def _update_fitness(self, result: Dict[str, Any]) -> None:
        """Update agent fitness based on mutation result.

        Args:
            result: Mutation result
        """
        fitness_delta = result.get("fitness_delta", 0.0)

        # Boost learning if specialization matches
        if result.get("specialization_match"):
            fitness_delta *= 1.5

        # Update fitness with learning rate
        self.fitness += self.learning_rate * fitness_delta
        self.fitness = max(0.1, min(1.0, self.fitness))  # Clamp to [0.1, 1.0]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics.

        Returns:
            Performance metrics dictionary
        """
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "fitness": self.fitness,
            "mutations_applied": self.mutations_applied,
            "successful_mutations": self.successful_mutations,
            "success_rate": (
                self.successful_mutations / self.mutations_applied
                if self.mutations_applied > 0
                else 0.0
            ),
            "experience_count": len(self.experience),
        }

    def share_knowledge(self) -> Dict[str, Any]:
        """Share knowledge with other agents.

        Returns:
            Shareable knowledge dictionary
        """
        return {
            "agent_id": self.agent_id,
            "specialization": self.specialization,
            "fitness": self.fitness,
            "best_practices": self._extract_best_practices(),
        }

    def _extract_best_practices(self) -> list[str]:
        """Extract best practices from successful experiences.

        Returns:
            List of best practice descriptions
        """
        successful_experiences = [e for e in self.experience if e.get("success")]

        if not successful_experiences:
            return []

        # Simple heuristic: mutations with high fitness delta
        high_value = [
            e.get("mutation_id", "unknown")
            for e in successful_experiences
            if e.get("fitness_delta", 0) > 0.2
        ]

        return high_value[:5]  # Top 5 best practices

    def reset(self) -> None:
        """Reset agent to initial state."""
        self.fitness = 0.5
        self.mutations_applied = 0
        self.successful_mutations = 0
        self.experience.clear()
        logger.info(f"Agent {self.agent_id} reset")

    def __repr__(self) -> str:
        """String representation of agent."""
        return (
            f"NanoAgent(id={self.agent_id}, spec={self.specialization}, "
            f"fitness={self.fitness:.3f}, success_rate="
            f"{self.successful_mutations}/{self.mutations_applied})"
        )
