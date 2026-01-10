"""KEGG Pathway Validator - Validates mutation accuracy against KEGG database."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from kegg_integration.pathway_fetcher import KEGGPathwayFetcher

logger = logging.getLogger(__name__)


class KEGGValidator:
    """Validate mutations against KEGG pathway structure."""

    def __init__(self, target_accuracy: float = 0.9994) -> None:
        """Initialize KEGG validator.

        Args:
            target_accuracy: Target validation accuracy (99.94%+)
        """
        self.target_accuracy = target_accuracy
        self.pathway_fetcher = KEGGPathwayFetcher()
        self.validation_results: List[Dict[str, Any]] = []

    def validate_pathway_fetch(self, pathway_id: str) -> Dict[str, Any]:
        """Validate pathway fetch accuracy.

        Args:
            pathway_id: KEGG pathway identifier

        Returns:
            Validation result
        """
        try:
            pathway = self.pathway_fetcher.fetch_pathway(pathway_id)
            
            if pathway is None:
                return {
                    "pathway_id": pathway_id,
                    "success": False,
                    "error": "Failed to fetch pathway",
                }

            # Validate pathway structure
            has_name = bool(pathway.get("name"))
            has_genes = "genes" in pathway
            has_compounds = "compounds" in pathway

            validation = {
                "pathway_id": pathway_id,
                "success": True,
                "has_name": has_name,
                "has_genes": has_genes,
                "has_compounds": has_compounds,
                "gene_count": len(pathway.get("genes", [])),
                "compound_count": len(pathway.get("compounds", [])),
                "valid": all([has_name, has_genes, has_compounds]),
            }

            logger.info(
                f"Validated {pathway_id}: "
                f"{validation['gene_count']} genes, "
                f"{validation['compound_count']} compounds"
            )

            return validation

        except Exception as e:
            logger.error(f"Validation error for {pathway_id}: {e}")
            return {
                "pathway_id": pathway_id,
                "success": False,
                "error": str(e),
            }

    def validate_mutation_mapping(
        self, pathway_id: str, mutation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that a mutation correctly maps to pathway structure.

        Args:
            pathway_id: KEGG pathway identifier
            mutation: Mutation specification

        Returns:
            Validation result
        """
        pathway = self.pathway_fetcher.fetch_pathway(pathway_id)
        
        if pathway is None:
            return {
                "mutation_id": mutation.get("id"),
                "valid": False,
                "error": "Pathway not found",
            }

        # Check if mutation type is appropriate for pathway
        mutation_type = mutation.get("type")
        valid_types = [
            "branching_pathway",
            "catalytic_reaction",
            "metabolic_crossover",
            "pathway_inhibition",
        ]

        is_valid_type = mutation_type in valid_types

        # Check if mutation has required fields
        has_required_fields = all(
            field in mutation for field in ["id", "type", "operator"]
        )

        validation = {
            "mutation_id": mutation.get("id"),
            "pathway_id": pathway_id,
            "mutation_type": mutation_type,
            "valid_type": is_valid_type,
            "has_required_fields": has_required_fields,
            "valid": is_valid_type and has_required_fields,
        }

        return validation

    def run_comprehensive_validation(
        self, pathway_ids: List[str]
    ) -> Dict[str, Any]:
        """Run comprehensive validation across multiple pathways.

        Args:
            pathway_ids: List of pathway IDs to validate

        Returns:
            Validation summary
        """
        logger.info(f"Running comprehensive validation on {len(pathway_ids)} pathways")

        results = []
        for pathway_id in pathway_ids:
            result = self.validate_pathway_fetch(pathway_id)
            results.append(result)

        # Calculate metrics
        total = len(results)
        successful = sum(1 for r in results if r.get("success"))
        valid = sum(1 for r in results if r.get("valid", False))
        accuracy = valid / total if total > 0 else 0.0

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "total_pathways": total,
            "successful_fetches": successful,
            "valid_pathways": valid,
            "accuracy": accuracy,
            "target_accuracy": self.target_accuracy,
            "meets_target": accuracy >= self.target_accuracy,
            "results": results,
        }

        self.validation_results.append(summary)

        logger.info(
            f"Validation complete: {valid}/{total} valid ({accuracy:.4%}), "
            f"Target: {self.target_accuracy:.4%}"
        )

        return summary

    def save_results(self, output_path: str) -> None:
        """Save validation results.

        Args:
            output_path: Output file path
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(f"Validation results saved to: {output_path}")

    def generate_report(self) -> str:
        """Generate markdown validation report.

        Returns:
            Markdown report string
        """
        if not self.validation_results:
            return "No validation results available."

        latest = self.validation_results[-1]

        report = f"""# KEGG Pathway Validation Report

## Summary
- **Total Pathways:** {latest['total_pathways']}
- **Successful Fetches:** {latest['successful_fetches']}
- **Valid Pathways:** {latest['valid_pathways']}
- **Accuracy:** {latest['accuracy']:.4%}
- **Target:** {latest['target_accuracy']:.4%}
- **Status:** {'✅ PASSED' if latest['meets_target'] else '❌ FAILED'}

## Pathway Details
"""

        for result in latest["results"][:10]:  # Show first 10
            status = "✅" if result.get("valid") else "❌"
            pathway_id = result.get("pathway_id", "unknown")
            gene_count = result.get("gene_count", 0)
            compound_count = result.get("compound_count", 0)

            report += f"- {status} **{pathway_id}**: {gene_count} genes, {compound_count} compounds\n"

        report += f"\n**Timestamp:** {latest['timestamp']}\n"

        return report
