"""Swarm Orchestrator - Manages coordination of 100-1000 nano agents."""

import logging
from typing import Any, Dict, List, Optional

from src.agents.nano_agent import NanoAgent

logger = logging.getLogger(__name__)


class SwarmOrchestrator:
    """Orchestrates a swarm of nano agents for distributed mutation."""

    def __init__(self, swarm_size: int = 100, specialization_diversity: bool = True) -> None:
        """Initialize the swarm orchestrator.

        Args:
            swarm_size: Number of agents in the swarm
            specialization_diversity: Whether to diversify agent specializations
        """
        self.swarm_size = swarm_size
        self.specialization_diversity = specialization_diversity
        self.agents: List[NanoAgent] = []
        self.generation = 0
        self._initialize_swarm()

    def _initialize_swarm(self) -> None:
        """Initialize the agent swarm."""
        logger.info(f"Initializing swarm with {self.swarm_size} agents")

        specializations = [
            "function_decomposition",
            "code_optimization",
            "module_combination",
            "dead_code_removal",
            "pipeline_creation",
            "abstraction_creation",
        ]

        for i in range(self.swarm_size):
            if self.specialization_diversity:
                spec = specializations[i % len(specializations)]
            else:
                spec = None

            agent = NanoAgent(
                agent_id=f"swarm_agent_{i:04d}", specialization=spec, learning_rate=0.1
            )
            self.agents.append(agent)

        logger.info(
            f"Swarm initialized: {len(self.agents)} agents, "
            f"diversity: {self.specialization_diversity}"
        )

    def distribute_mutations(
        self, mutations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Distribute mutations across the swarm.

        Args:
            mutations: List of mutations to apply

        Returns:
            List of mutation results
        """
        logger.info(f"Distributing {len(mutations)} mutations across {len(self.agents)} agents")

        results = []
        for i, mutation in enumerate(mutations):
            # Assign mutation to agent with matching specialization or round-robin
            agent = self._select_agent_for_mutation(mutation)
            result = agent.apply_mutation(mutation)
            results.append(result)

        self.generation += 1
        logger.info(f"Generation {self.generation} complete: {len(results)} mutations applied")

        return results

    def _select_agent_for_mutation(self, mutation: Dict[str, Any]) -> NanoAgent:
        """Select the best agent for a given mutation.

        Args:
            mutation: Mutation specification

        Returns:
            Selected agent
        """
        mutation_operator = mutation.get("operator")

        # Find agents with matching specialization
        matching_agents = [
            agent for agent in self.agents if agent.specialization == mutation_operator
        ]

        if matching_agents:
            # Select agent with highest fitness
            return max(matching_agents, key=lambda a: a.fitness)

        # Fallback: select agent with highest fitness overall
        return max(self.agents, key=lambda a: a.fitness)

    def get_swarm_statistics(self) -> Dict[str, Any]:
        """Get overall swarm statistics.

        Returns:
            Swarm statistics dictionary
        """
        total_mutations = sum(agent.mutations_applied for agent in self.agents)
        total_successful = sum(agent.successful_mutations for agent in self.agents)
        avg_fitness = sum(agent.fitness for agent in self.agents) / len(self.agents)

        # Get top performers
        top_agents = sorted(self.agents, key=lambda a: a.fitness, reverse=True)[:10]

        # Specialization breakdown
        spec_stats: Dict[str, Dict[str, Any]] = {}
        for agent in self.agents:
            spec = agent.specialization
            if spec not in spec_stats:
                spec_stats[spec] = {"count": 0, "avg_fitness": 0.0, "total_fitness": 0.0}
            spec_stats[spec]["count"] += 1
            spec_stats[spec]["total_fitness"] += agent.fitness

        for spec in spec_stats:
            spec_stats[spec]["avg_fitness"] = (
                spec_stats[spec]["total_fitness"] / spec_stats[spec]["count"]
            )

        return {
            "swarm_size": len(self.agents),
            "generation": self.generation,
            "total_mutations": total_mutations,
            "total_successful": total_successful,
            "success_rate": total_successful / total_mutations if total_mutations > 0 else 0.0,
            "average_fitness": avg_fitness,
            "top_agents": [
                {
                    "agent_id": agent.agent_id,
                    "fitness": agent.fitness,
                    "success_rate": agent.successful_mutations / agent.mutations_applied
                    if agent.mutations_applied > 0
                    else 0.0,
                }
                for agent in top_agents
            ],
            "specialization_breakdown": spec_stats,
        }

    def evolve_swarm(self, keep_top_percent: float = 0.2) -> None:
        """Evolve the swarm by replacing low performers.

        Args:
            keep_top_percent: Percentage of top agents to keep
        """
        logger.info("Evolving swarm...")

        # Sort agents by fitness
        sorted_agents = sorted(self.agents, key=lambda a: a.fitness, reverse=True)

        # Keep top performers
        keep_count = int(len(sorted_agents) * keep_top_percent)
        top_agents = sorted_agents[:keep_count]

        # Replace bottom performers with new agents
        new_agents = []
        for i, old_agent in enumerate(sorted_agents[keep_count:]):
            # Clone top performer's specialization
            template = top_agents[i % len(top_agents)]
            new_agent = NanoAgent(
                specialization=template.specialization, learning_rate=0.1
            )
            new_agents.append(new_agent)

        self.agents = top_agents + new_agents
        logger.info(
            f"Swarm evolved: kept {len(top_agents)} top agents, "
            f"created {len(new_agents)} new agents"
        )

    def share_knowledge_across_swarm(self) -> Dict[str, Any]:
        """Enable knowledge sharing between agents.

        Returns:
            Aggregated knowledge dictionary
        """
        logger.info("Sharing knowledge across swarm...")

        all_knowledge = [agent.share_knowledge() for agent in self.agents]

        # Aggregate best practices
        all_best_practices = []
        for knowledge in all_knowledge:
            all_best_practices.extend(knowledge.get("best_practices", []))

        # Find most common best practices
        from collections import Counter

        practice_counts = Counter(all_best_practices)
        top_practices = practice_counts.most_common(10)

        aggregated = {
            "total_agents": len(self.agents),
            "knowledge_contributions": len(all_knowledge),
            "top_best_practices": [practice for practice, count in top_practices],
            "average_fitness": sum(k["fitness"] for k in all_knowledge) / len(all_knowledge),
        }

        logger.info(f"Knowledge shared: {len(top_practices)} top practices identified")
        return aggregated

    def reset_swarm(self) -> None:
        """Reset all agents in the swarm."""
        for agent in self.agents:
            agent.reset()
        self.generation = 0
        logger.info("Swarm reset complete")

    def get_agent_by_id(self, agent_id: str) -> Optional[NanoAgent]:
        """Get an agent by ID.

        Args:
            agent_id: Agent identifier

        Returns:
            Agent or None if not found
        """
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
