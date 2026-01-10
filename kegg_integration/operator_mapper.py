"""Operator Mapper - Maps biological operators to code mutations."""

import logging
import random
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BiologicalOperatorMapper:
    """Maps KEGG biological operators to code mutation strategies."""

    MUTATION_TYPES = {
        "branching_pathway": {
            "operator": "function_decomposition",
            "description": "Split complex functions into smaller, focused functions",
            "priority": "high",
        },
        "catalytic_reaction": {
            "operator": "code_optimization",
            "description": "Optimize code performance using catalytic patterns",
            "priority": "medium",
        },
        "metabolic_crossover": {
            "operator": "module_combination",
            "description": "Combine related modules for better cohesion",
            "priority": "medium",
        },
        "pathway_inhibition": {
            "operator": "dead_code_removal",
            "description": "Remove unused code and optimize imports",
            "priority": "low",
        },
        "linear_chain": {
            "operator": "pipeline_creation",
            "description": "Create processing pipelines from linear operations",
            "priority": "medium",
        },
        "convergence_point": {
            "operator": "abstraction_creation",
            "description": "Create abstractions for common patterns",
            "priority": "high",
        },
    }

    def __init__(self) -> None:
        """Initialize the operator mapper."""
        self.mutation_history: List[Dict[str, Any]] = []

    def map_graph_to_mutations(
        self, graph_analysis: Dict[str, Any], candidates: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Map graph structure to concrete mutation operations.

        Args:
            graph_analysis: Analysis results from KEGGGraphBuilder
            candidates: Mutation candidates from graph

        Returns:
            List of mutation operations with priorities
        """
        mutations = []

        for candidate in candidates:
            mutation_type = candidate.get("type")
            if mutation_type in self.MUTATION_TYPES:
                mutation_spec = self.MUTATION_TYPES[mutation_type]

                mutation = {
                    "id": f"mut_{len(mutations)}",
                    "type": mutation_type,
                    "operator": mutation_spec["operator"],
                    "description": mutation_spec["description"],
                    "priority": mutation_spec["priority"],
                    "source": candidate,
                    "confidence": self._calculate_confidence(candidate, graph_analysis),
                }

                mutations.append(mutation)

        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        mutations.sort(
            key=lambda m: (priority_order.get(m["priority"], 0), m["confidence"]),
            reverse=True,
        )

        logger.info(f"Mapped {len(mutations)} mutations from {len(candidates)} candidates")
        return mutations

    def _calculate_confidence(
        self, candidate: Dict[str, Any], graph_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a mutation candidate.

        Args:
            candidate: Mutation candidate
            graph_analysis: Graph analysis results

        Returns:
            Confidence score between 0 and 1
        """
        confidence = 0.5  # Base confidence

        # Increase confidence for branching pathways with many successors
        if candidate.get("type") == "branching_pathway":
            out_degree = candidate.get("out_degree", 0)
            confidence += min(out_degree * 0.1, 0.3)

        # Increase confidence for well-connected components
        if graph_analysis.get("is_dag"):
            confidence += 0.1

        # Increase confidence based on graph density
        density = graph_analysis.get("density", 0)
        if density > 0.3:
            confidence += 0.1

        return min(confidence, 1.0)

    def generate_mutation_code(self, mutation: Dict[str, Any]) -> str:
        """Generate sample mutation code for a given mutation operation.

        Args:
            mutation: Mutation specification

        Returns:
            Python code string representing the mutation
        """
        operator = mutation.get("operator")

        if operator == "function_decomposition":
            return self._generate_decomposition_code(mutation)
        elif operator == "code_optimization":
            return self._generate_optimization_code(mutation)
        elif operator == "module_combination":
            return self._generate_combination_code(mutation)
        elif operator == "dead_code_removal":
            return self._generate_removal_code(mutation)
        elif operator == "pipeline_creation":
            return self._generate_pipeline_code(mutation)
        elif operator == "abstraction_creation":
            return self._generate_abstraction_code(mutation)
        else:
            return f"# Unknown mutation operator: {operator}\npass"

    def _generate_decomposition_code(self, mutation: Dict[str, Any]) -> str:
        """Generate function decomposition code."""
        source = mutation.get("source", {})
        successors = source.get("successors", [])

        code = "# Function Decomposition Mutation\n"
        code += "# Original: Single monolithic function\n"
        code += "# Mutated: Decomposed into smaller functions\n\n"
        code += "def original_function(data):\n"
        code += "    # Complex logic here\n"
        code += "    pass\n\n"
        code += "# Decomposed functions:\n"
        for idx, successor in enumerate(successors[:3]):
            code += f"def step_{idx + 1}(data):\n"
            code += f"    # Handle {successor}\n"
            code += "    return data\n\n"
        code += "def refactored_function(data):\n"
        code += "    data = step_1(data)\n"
        code += "    data = step_2(data)\n"
        code += "    return data\n"

        return code

    def _generate_optimization_code(self, mutation: Dict[str, Any]) -> str:
        """Generate code optimization mutation."""
        code = "# Code Optimization Mutation (Catalytic Pattern)\n"
        code += "# Original: Inefficient implementation\n"
        code += "def original(items):\n"
        code += "    result = []\n"
        code += "    for item in items:\n"
        code += "        result.append(process(item))\n"
        code += "    return result\n\n"
        code += "# Optimized: Using list comprehension\n"
        code += "def optimized(items):\n"
        code += "    return [process(item) for item in items]\n"
        return code

    def _generate_combination_code(self, mutation: Dict[str, Any]) -> str:
        """Generate module combination mutation."""
        code = "# Module Combination Mutation\n"
        code += "# Original: Separate related modules\n"
        code += "# module_a.py\n"
        code += "def func_a(): pass\n\n"
        code += "# module_b.py\n"
        code += "def func_b(): pass\n\n"
        code += "# Combined: unified_module.py\n"
        code += "class UnifiedModule:\n"
        code += "    def func_a(self): pass\n"
        code += "    def func_b(self): pass\n"
        return code

    def _generate_removal_code(self, mutation: Dict[str, Any]) -> str:
        """Generate dead code removal mutation."""
        code = "# Dead Code Removal Mutation (Pathway Inhibition)\n"
        code += "# Original: Code with unused functions\n"
        code += "def used_function():\n"
        code += "    return 42\n\n"
        code += "def unused_function():  # REMOVE\n"
        code += "    return 0\n\n"
        code += "# Cleaned:\n"
        code += "def used_function():\n"
        code += "    return 42\n"
        return code

    def _generate_pipeline_code(self, mutation: Dict[str, Any]) -> str:
        """Generate pipeline creation mutation."""
        source = mutation.get("source", {})
        path_length = source.get("length", 3)

        code = "# Pipeline Creation Mutation\n"
        code += "# Original: Sequential operations\n"
        code += "data = step1(data)\n"
        code += "data = step2(data)\n"
        code += "data = step3(data)\n\n"
        code += "# Pipeline:\n"
        code += "from functools import reduce\n"
        code += f"pipeline = [step{i} for i in range(1, {path_length + 1})]\n"
        code += "result = reduce(lambda d, f: f(d), pipeline, data)\n"
        return code

    def _generate_abstraction_code(self, mutation: Dict[str, Any]) -> str:
        """Generate abstraction creation mutation."""
        code = "# Abstraction Creation Mutation (Convergence Point)\n"
        code += "# Original: Repeated patterns\n"
        code += "def process_a(data):\n"
        code += "    validate(data)\n"
        code += "    return transform_a(data)\n\n"
        code += "def process_b(data):\n"
        code += "    validate(data)\n"
        code += "    return transform_b(data)\n\n"
        code += "# Abstracted:\n"
        code += "def process_with_validation(data, transform):\n"
        code += "    validate(data)\n"
        code += "    return transform(data)\n"
        return code

    def record_mutation(self, mutation: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Record a mutation and its result for future learning.

        Args:
            mutation: Mutation specification
            result: Mutation execution result
        """
        record = {
            "mutation_id": mutation.get("id"),
            "type": mutation.get("type"),
            "operator": mutation.get("operator"),
            "confidence": mutation.get("confidence"),
            "success": result.get("success", False),
            "fitness_delta": result.get("fitness_delta", 0.0),
        }

        self.mutation_history.append(record)
        logger.info(f"Recorded mutation: {record['mutation_id']}")

    def get_mutation_statistics(self) -> Dict[str, Any]:
        """Get statistics about recorded mutations.

        Returns:
            Dictionary containing mutation statistics
        """
        if not self.mutation_history:
            return {"total": 0, "success_rate": 0.0, "by_type": {}}

        total = len(self.mutation_history)
        successful = sum(1 for m in self.mutation_history if m.get("success"))

        by_type: Dict[str, Any] = {}
        for mutation in self.mutation_history:
            mut_type = mutation.get("type", "unknown")
            if mut_type not in by_type:
                by_type[mut_type] = {"total": 0, "successful": 0}
            by_type[mut_type]["total"] += 1
            if mutation.get("success"):
                by_type[mut_type]["successful"] += 1

        return {
            "total": total,
            "successful": successful,
            "success_rate": successful / total if total > 0 else 0.0,
            "by_type": by_type,
        }
