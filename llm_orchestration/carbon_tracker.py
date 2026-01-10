"""Carbon Tracker - Track CO2 emissions per query."""

import logging
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class CarbonTracker:
    """Track carbon emissions from LLM usage."""

    def __init__(self) -> None:
        """Initialize carbon tracker."""
        # CO2 emissions in grams per 1000 tokens (estimates based on model size and provider)
        self.emission_factors = {
            "grok-4": 2.5,  # Large model, optimized datacenter
            "claude-opus-4.5": 3.0,  # Large model
            "gemini-3-flash": 0.5,  # Optimized for efficiency
            "llama-4": 1.5,  # Self-hosted efficiency depends on setup
            "qwen-3": 1.8,
            "deepseek": 2.0,
        }
        self.emissions_history: List[Dict[str, Any]] = []

    def calculate_emissions(
        self, model: str, tokens_used: int
    ) -> Dict[str, Any]:
        """Calculate CO2 emissions for a query.

        Args:
            model: Model name
            tokens_used: Number of tokens processed

        Returns:
            Emissions data
        """
        emission_factor = self.emission_factors.get(model, 2.0)
        co2_grams = (tokens_used / 1000) * emission_factor

        # Convert to different units
        co2_kg = co2_grams / 1000
        co2_tonnes = co2_kg / 1000

        # Carbon offset equivalents
        trees_needed = co2_kg / 21  # 21kg CO2 absorbed per tree per year
        km_driven = co2_kg / 0.12  # 0.12kg CO2 per km driven

        emission_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "model": model,
            "tokens_used": tokens_used,
            "co2_grams": co2_grams,
            "co2_kg": co2_kg,
            "co2_tonnes": co2_tonnes,
            "trees_equivalent": trees_needed,
            "km_driven_equivalent": km_driven,
        }

        self.emissions_history.append(emission_data)

        logger.info(
            f"Emissions for {tokens_used} tokens on {model}: "
            f"{co2_grams:.2f}g CO2"
        )

        return emission_data

    def get_total_emissions(self) -> Dict[str, Any]:
        """Get total emissions across all queries.

        Returns:
            Total emissions summary
        """
        if not self.emissions_history:
            return {
                "total_queries": 0,
                "total_co2_kg": 0.0,
                "total_trees_needed": 0.0,
            }

        total_co2_grams = sum(e["co2_grams"] for e in self.emissions_history)
        total_co2_kg = total_co2_grams / 1000

        return {
            "total_queries": len(self.emissions_history),
            "total_tokens": sum(e["tokens_used"] for e in self.emissions_history),
            "total_co2_grams": total_co2_grams,
            "total_co2_kg": total_co2_kg,
            "total_co2_tonnes": total_co2_kg / 1000,
            "total_trees_needed": total_co2_kg / 21,
            "total_km_driven_equivalent": total_co2_kg / 0.12,
            "avg_co2_per_query": total_co2_grams / len(self.emissions_history),
        }

    def get_emissions_by_model(self) -> Dict[str, Dict[str, float]]:
        """Get emissions breakdown by model.

        Returns:
            Emissions by model
        """
        by_model: Dict[str, Dict[str, float]] = {}

        for emission in self.emissions_history:
            model = emission["model"]
            if model not in by_model:
                by_model[model] = {"queries": 0, "co2_kg": 0.0, "tokens": 0}

            by_model[model]["queries"] += 1
            by_model[model]["co2_kg"] += emission["co2_kg"]
            by_model[model]["tokens"] += emission["tokens_used"]

        return by_model

    def generate_esg_report(self) -> str:
        """Generate ESG (Environmental, Social, Governance) report.

        Returns:
            Markdown report
        """
        total = self.get_total_emissions()
        by_model = self.get_emissions_by_model()

        report = f"""# Carbon Emissions Report

## Total Emissions
- **Total Queries:** {total['total_queries']:,}
- **Total Tokens:** {total['total_tokens']:,}
- **Total CO2:** {total['total_co2_kg']:.2f} kg ({total['total_co2_tonnes']:.6f} tonnes)
- **Trees Needed for Offset:** {total['total_trees_needed']:.2f}
- **Equivalent to Driving:** {total['total_km_driven_equivalent']:.2f} km

## Emissions by Model
"""

        for model, stats in sorted(
            by_model.items(), key=lambda x: x[1]["co2_kg"], reverse=True
        ):
            report += f"\n### {model}\n"
            report += f"- Queries: {stats['queries']:,}\n"
            report += f"- Tokens: {stats['tokens']:,}\n"
            report += f"- CO2: {stats['co2_kg']:.2f} kg\n"
            report += f"- Avg per query: {stats['co2_kg']/stats['queries']:.4f} kg\n"

        return report

    def suggest_reductions(self) -> List[Dict[str, Any]]:
        """Suggest ways to reduce carbon emissions.

        Returns:
            List of suggestions
        """
        suggestions = []

        by_model = self.get_emissions_by_model()

        # Suggest switching to more efficient models
        if "claude-opus-4.5" in by_model:
            claude_emissions = by_model["claude-opus-4.5"]["co2_kg"]
            potential_savings = claude_emissions * 0.83  # 83% reduction with Gemini
            suggestions.append(
                {
                    "type": "model_switch",
                    "suggestion": "Switch from Claude Opus to Gemini Flash for simple tasks",
                    "potential_co2_reduction_kg": potential_savings,
                }
            )

        # Suggest prompt optimization
        total = self.get_total_emissions()
        if total["total_queries"] > 0:
            avg_tokens = total["total_tokens"] / total["total_queries"]
            if avg_tokens > 2000:
                suggestions.append(
                    {
                        "type": "prompt_optimization",
                        "suggestion": "Reduce prompt length by 30% through compression",
                        "potential_co2_reduction_kg": total["total_co2_kg"] * 0.3,
                    }
                )

        # Suggest caching
        suggestions.append(
            {
                "type": "caching",
                "suggestion": "Implement response caching to reduce redundant queries",
                "potential_co2_reduction_kg": total["total_co2_kg"] * 0.4,
            }
        )

        return suggestions
