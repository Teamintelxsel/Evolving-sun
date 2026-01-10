#!/usr/bin/env python3
"""
KEGG (Kyoto Encyclopedia of Genes and Genomes) benchmark harness runner.

This script uses Biopython to parse KEGG pathway data and evaluate
biological pathway understanding with watermarked logging.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, List
import urllib.request
import urllib.error

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def fetch_kegg_pathway(pathway_id: str) -> dict:
    """
    Fetch KEGG pathway data using KEGG REST API.
    
    Args:
        pathway_id: KEGG pathway ID (e.g., "hsa00010" for human glycolysis)
    
    Returns:
        Dictionary containing pathway information
    """
    base_url = "http://rest.kegg.jp/get/"
    url = f"{base_url}{pathway_id}"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')
        
        # Parse basic information from KEGG flat file format
        lines = data.split('\n')
        pathway_info = {
            "id": pathway_id,
            "name": "",
            "description": "",
            "genes": [],
            "compounds": []
        }
        
        current_section = None
        for line in lines:
            if line.startswith("NAME"):
                pathway_info["name"] = line[12:].strip()
            elif line.startswith("DESCRIPTION"):
                pathway_info["description"] = line[12:].strip()
            elif line.startswith("GENE"):
                current_section = "genes"
                gene_info = line[12:].strip()
                if gene_info:
                    pathway_info["genes"].append(gene_info)
            elif line.startswith("COMPOUND"):
                current_section = "compounds"
                compound_info = line[12:].strip()
                if compound_info:
                    pathway_info["compounds"].append(compound_info)
            elif current_section and line.startswith(" " * 12):
                # Continuation line
                info = line.strip()
                if info:
                    if current_section == "genes":
                        pathway_info["genes"].append(info)
                    elif current_section == "compounds":
                        pathway_info["compounds"].append(info)
        
        return {
            "success": True,
            "pathway": pathway_info
        }
        
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"Failed to fetch pathway {pathway_id}: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing pathway {pathway_id}: {str(e)}"
        }


def run_kegg_baseline(pathway_ids: List[str]) -> dict:
    """
    Run KEGG pathway analysis baseline.
    
    Args:
        pathway_ids: List of KEGG pathway IDs to analyze
    
    Returns:
        Dictionary containing benchmark results
    """
    print(f"Analyzing {len(pathway_ids)} KEGG pathways...")
    
    results = {
        "dataset": "KEGG Pathways",
        "total_pathways": len(pathway_ids),
        "successful": 0,
        "failed": 0,
        "pathways": []
    }
    
    for pathway_id in pathway_ids:
        print(f"Fetching pathway: {pathway_id}")
        pathway_result = fetch_kegg_pathway(pathway_id)
        
        if pathway_result.get("success"):
            results["successful"] += 1
            pathway_data = pathway_result["pathway"]
            results["pathways"].append({
                "id": pathway_id,
                "name": pathway_data.get("name", "Unknown"),
                "num_genes": len(pathway_data.get("genes", [])),
                "num_compounds": len(pathway_data.get("compounds", [])),
                "status": "success"
            })
        else:
            results["failed"] += 1
            results["pathways"].append({
                "id": pathway_id,
                "error": pathway_result.get("error", "Unknown error"),
                "status": "failed"
            })
    
    results["status"] = "success" if results["failed"] == 0 else "partial"
    
    print(f"Successful: {results['successful']}/{results['total_pathways']}")
    
    return results


def parse_kegg_kgml(kgml_file: str) -> dict:
    """
    Parse KEGG KGML file using Biopython.
    
    Args:
        kgml_file: Path to KGML file
    
    Returns:
        Dictionary containing parsed pathway information
    """
    try:
        from Bio.KEGG.KGML.KGML_parser import read
    except ImportError:
        return {
            "error": "Biopython not installed. Run: pip install biopython",
            "status": "failed"
        }
    
    try:
        with open(kgml_file, 'r') as f:
            pathway = read(f)
        
        return {
            "name": pathway.name,
            "org": pathway.org,
            "number": pathway.number,
            "num_entries": len(pathway.entries),
            "num_relations": len(pathway.relations),
            "num_reactions": len(pathway.reactions),
            "status": "success"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }


def main():
    """Main entry point for KEGG harness."""
    parser = argparse.ArgumentParser(
        description="Run KEGG pathway analysis with watermarked logging"
    )
    parser.add_argument(
        "--pathways",
        nargs="+",
        default=["hsa00010", "hsa00020", "hsa00030"],
        help="KEGG pathway IDs to analyze (default: glycolysis, TCA, pentose phosphate)"
    )
    parser.add_argument(
        "--kgml",
        type=str,
        help="Optional: Path to KGML file to parse with Biopython"
    )
    parser.add_argument(
        "--output",
        default="logs/benchmarks/kegg_results.json",
        help="Output path for results (default: logs/benchmarks/kegg_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run benchmark
    print("=" * 60)
    print("KEGG Pathway Benchmark Harness")
    print("=" * 60)
    
    if args.kgml:
        # Parse KGML file if provided
        results = parse_kegg_kgml(args.kgml)
        results["mode"] = "kgml_parse"
    else:
        # Fetch pathways from REST API
        results = run_kegg_baseline(args.pathways)
        results["mode"] = "rest_api"
    
    # Write watermarked results
    watermark_log(results, args.output)
    
    print("=" * 60)
    print(f"Status: {results.get('status', 'unknown')}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if results.get("status") in ["success", "partial"] else 1)


if __name__ == "__main__":
    main()
