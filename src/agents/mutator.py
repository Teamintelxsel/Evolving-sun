"""Core KEGG Mutation Engine - Bio-inspired self-evolution system."""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from kegg_integration.graph_builder import KEGGGraphBuilder
from kegg_integration.operator_mapper import BiologicalOperatorMapper
from kegg_integration.pathway_fetcher import KEGGPathwayFetcher

logger = logging.getLogger(__name__)


class KEGGMutator:
    """Core mutation engine using KEGG metabolic pathways."""

    def __init__(
        self,
        pathway_fetcher: Optional[KEGGPathwayFetcher] = None,
        mutation_log_path: str = "mutations.jsonl",
    ) -> None:
        """Initialize the KEGG mutator.

        Args:
            pathway_fetcher: KEGG pathway fetcher instance
            mutation_log_path: Path to mutation log file
        """
        self.pathway_fetcher = pathway_fetcher or KEGGPathwayFetcher()
        self.graph_builder = KEGGGraphBuilder()
        self.operator_mapper = BiologicalOperatorMapper()
        self.mutation_log_path = Path(mutation_log_path)
        self.generation = 0
        self.mutation_history: List[Dict[str, Any]] = []

    def evolve(
        self,
        generations: int = 10,
        pathway_ids: Optional[List[str]] = None,
        target_mutations_per_gen: int = 10,
    ) -> Dict[str, Any]:
        """Run evolution for specified number of generations.

        Args:
            generations: Number of generations to evolve
            pathway_ids: List of pathway IDs to use (defaults to metabolic pathways)
            target_mutations_per_gen: Target number of mutations per generation

        Returns:
            Evolution results dictionary
        """
        if pathway_ids is None:
            pathway_ids = ["ko01100"]  # Metabolic pathways

        logger.info(f"Starting evolution for {generations} generations")
        logger.info(f"Using pathways: {pathway_ids}")

        results = {
            "generations": generations,
            "pathways": pathway_ids,
            "mutations": [],
            "successful_mutations": 0,
            "failed_mutations": 0,
            "fitness_improvements": [],
        }

        for gen in range(generations):
            self.generation = gen + 1
            logger.info(f"=== Generation {self.generation} ===")

            gen_results = self._run_generation(pathway_ids, target_mutations_per_gen)
            results["mutations"].extend(gen_results["mutations"])
            results["successful_mutations"] += gen_results["successful"]
            results["failed_mutations"] += gen_results["failed"]

            if gen_results["fitness_delta"] != 0:
                results["fitness_improvements"].append(gen_results["fitness_delta"])

            # Log generation summary
            logger.info(
                f"Generation {self.generation} complete: "
                f"{gen_results['successful']} successful, "
                f"{gen_results['failed']} failed, "
                f"fitness delta: {gen_results['fitness_delta']:.4f}"
            )

        # Calculate overall statistics
        results["total_mutations"] = len(results["mutations"])
        results["success_rate"] = (
            results["successful_mutations"] / results["total_mutations"]
            if results["total_mutations"] > 0
            else 0.0
        )
        results["avg_fitness_improvement"] = (
            sum(results["fitness_improvements"]) / len(results["fitness_improvements"])
            if results["fitness_improvements"]
            else 0.0
        )

        logger.info("=== Evolution Complete ===")
        logger.info(f"Total mutations: {results['total_mutations']}")
        logger.info(f"Success rate: {results['success_rate']:.2%}")
        logger.info(f"Avg fitness improvement: {results['avg_fitness_improvement']:.4f}")

        return results

    def _run_generation(
        self, pathway_ids: List[str], target_mutations: int
    ) -> Dict[str, Any]:
        """Run a single generation of evolution.

        Args:
            pathway_ids: List of pathway IDs to use
            target_mutations: Target number of mutations

        Returns:
            Generation results dictionary
        """
        gen_results = {
            "generation": self.generation,
            "mutations": [],
            "successful": 0,
            "failed": 0,
            "fitness_delta": 0.0,
        }

        # Fetch and analyze pathways
        all_candidates = []
        for pathway_id in pathway_ids:
            candidates = self._analyze_pathway(pathway_id)
            all_candidates.extend(candidates)

        if not all_candidates:
            logger.warning(f"No mutation candidates found for generation {self.generation}")
            return gen_results

        # Map candidates to mutations
        mutations = self.operator_mapper.map_graph_to_mutations(
            {"is_dag": True, "density": 0.5}, all_candidates
        )

        # Select top mutations
        selected_mutations = mutations[:target_mutations]

        # Apply mutations
        for mutation in selected_mutations:
            result = self._apply_mutation(mutation)
            gen_results["mutations"].append(result)

            if result["success"]:
                gen_results["successful"] += 1
                gen_results["fitness_delta"] += result.get("fitness_delta", 0.0)
            else:
                gen_results["failed"] += 1

            # Record mutation
            self.operator_mapper.record_mutation(mutation, result)
            self._log_mutation(result)

        return gen_results

    def _analyze_pathway(self, pathway_id: str) -> List[Dict[str, Any]]:
        """Analyze a pathway and identify mutation candidates.

        Args:
            pathway_id: KEGG pathway identifier

        Returns:
            List of mutation candidates
        """
        # Try to fetch KGML for detailed analysis
        kgml = self.pathway_fetcher.fetch_pathway_kgml(pathway_id)

        if kgml:
            graph = self.graph_builder.build_from_kgml(kgml, pathway_id)
            if graph:
                analysis = self.graph_builder.analyze_graph_structure(graph)
                candidates = self.graph_builder.find_mutation_candidates(graph)
                logger.info(
                    f"Analyzed {pathway_id}: {analysis['num_nodes']} nodes, "
                    f"{len(candidates)} candidates"
                )
                return candidates

        # Fallback to simplified analysis
        pathway_data = self.pathway_fetcher.fetch_pathway(pathway_id)
        if pathway_data:
            graph = self.graph_builder.build_from_pathway_data(pathway_data)
            # Generate simple candidates
            candidates = [
                {
                    "type": "catalytic_reaction",
                    "mutation_operator": "code_optimization",
                    "node": f"gene_{i}",
                }
                for i in range(min(5, len(pathway_data.get("genes", []))))
            ]
            return candidates

        return []

    def _apply_mutation(self, mutation: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a mutation and evaluate its fitness.

        Args:
            mutation: Mutation specification

        Returns:
            Mutation result dictionary
        """
        mutation_id = mutation.get("id")
        logger.info(f"Applying mutation: {mutation_id} ({mutation.get('operator')})")

        # Generate mutation code
        code = self.operator_mapper.generate_mutation_code(mutation)

        # Simulate fitness evaluation (in production, this would run SWE-bench)
        import random

        success = random.random() > 0.3  # 70% success rate simulation
        fitness_delta = random.uniform(-0.1, 0.5) if success else 0.0

        result = {
            "mutation_id": mutation_id,
            "generation": self.generation,
            "type": mutation.get("type"),
            "operator": mutation.get("operator"),
            "confidence": mutation.get("confidence"),
            "code": code,
            "success": success,
            "fitness_delta": fitness_delta,
            "timestamp": time.time(),
        }

        self.mutation_history.append(result)
        return result

    def _log_mutation(self, mutation_result: Dict[str, Any]) -> None:
        """Log mutation to JSONL file.

        Args:
            mutation_result: Mutation result dictionary
        """
        try:
            with open(self.mutation_log_path, "a") as f:
                f.write(json.dumps(mutation_result) + "\n")
        except IOError as e:
            logger.error(f"Failed to log mutation: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get mutation statistics.

        Returns:
            Statistics dictionary
        """
        stats = self.operator_mapper.get_mutation_statistics()
        stats["total_generations"] = self.generation
        stats["mutations_per_generation"] = (
            len(self.mutation_history) / self.generation if self.generation > 0 else 0
        )
        return stats

    def save_state(self, filepath: str) -> None:
        """Save mutator state to file.

        Args:
            filepath: Path to save state
        """
        state = {
            "generation": self.generation,
            "mutation_history": self.mutation_history,
            "statistics": self.get_statistics(),
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"Saved state to {filepath}")

    def load_state(self, filepath: str) -> None:
        """Load mutator state from file.

        Args:
            filepath: Path to load state from
        """
        with open(filepath) as f:
            state = json.load(f)

        self.generation = state.get("generation", 0)
        self.mutation_history = state.get("mutation_history", [])

        logger.info(f"Loaded state from {filepath}")
