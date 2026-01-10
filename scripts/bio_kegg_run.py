#!/usr/bin/env python3
"""
KEGG KGML Biological Pathway Benchmark Runner

This script fetches KGML (KEGG Markup Language) data via KEGG REST API
and performs baseline analysis on biological pathways.

Usage:
    python scripts/bio_kegg_run.py [options]
"""

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib import request, error

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utils.secure_logging import watermark_log


def get_git_commit_sha() -> str:
    """Get the current git commit SHA."""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def fetch_kegg_pathway_list(organism: str = "hsa", max_pathways: int = 10) -> List[str]:
    """
    Fetch list of KEGG pathways for a given organism.
    
    Args:
        organism: Organism code (e.g., 'hsa' for human)
        max_pathways: Maximum number of pathways to fetch
        
    Returns:
        List of pathway IDs
    """
    url = f"http://rest.kegg.jp/list/pathway/{organism}"
    
    try:
        print(f"Fetching pathway list from KEGG for organism: {organism}")
        with request.urlopen(url, timeout=30) as response:
            content = response.read().decode('utf-8')
        
        # Parse pathway IDs from response
        # Format: "path:hsa00010\tGlycolysis / Gluconeogenesis - Homo sapiens (human)"
        pathways = []
        for line in content.strip().split('\n'):
            if '\t' in line:
                pathway_id = line.split('\t')[0].replace('path:', '')
                pathways.append(pathway_id)
                if len(pathways) >= max_pathways:
                    break
        
        return pathways
        
    except (error.URLError, error.HTTPError, Exception) as e:
        print(f"Warning: Could not fetch pathway list: {e}")
        return simulate_pathway_list(organism, max_pathways)


def simulate_pathway_list(organism: str = "hsa", max_pathways: int = 10) -> List[str]:
    """Simulate pathway list when KEGG API is not available."""
    # Common human pathways
    common_pathways = [
        f"{organism}00010",  # Glycolysis
        f"{organism}00020",  # Citrate cycle
        f"{organism}00030",  # Pentose phosphate pathway
        f"{organism}00040",  # Pentose and glucuronate interconversions
        f"{organism}00051",  # Fructose and mannose metabolism
        f"{organism}00052",  # Galactose metabolism
        f"{organism}00053",  # Ascorbate and aldarate metabolism
        f"{organism}00500",  # Starch and sucrose metabolism
        f"{organism}00520",  # Amino sugar and nucleotide sugar metabolism
        f"{organism}00620",  # Pyruvate metabolism
    ]
    return common_pathways[:max_pathways]


def fetch_kgml_data(pathway_id: str) -> Optional[Dict]:
    """
    Fetch KGML data for a specific pathway.
    
    Args:
        pathway_id: KEGG pathway ID
        
    Returns:
        Dictionary with KGML data or None if fetch fails
    """
    url = f"http://rest.kegg.jp/get/{pathway_id}/kgml"
    
    try:
        with request.urlopen(url, timeout=30) as response:
            kgml_xml = response.read().decode('utf-8')
        
        # Basic parsing to extract metadata
        result = {
            "pathway_id": pathway_id,
            "data_size_bytes": len(kgml_xml),
            "has_entry": "<entry" in kgml_xml,
            "has_relation": "<relation" in kgml_xml,
            "has_reaction": "<reaction" in kgml_xml,
            "fetched": True
        }
        
        # Count elements (simple text-based counting)
        result["entry_count"] = kgml_xml.count("<entry")
        result["relation_count"] = kgml_xml.count("<relation")
        result["reaction_count"] = kgml_xml.count("<reaction")
        
        return result
        
    except (error.URLError, error.HTTPError, Exception) as e:
        print(f"  Warning: Could not fetch KGML for {pathway_id}: {e}")
        return None


def simulate_kgml_data(pathway_id: str) -> Dict:
    """Simulate KGML data when API is not available."""
    import random
    random.seed(hash(pathway_id) % (2**32))
    
    return {
        "pathway_id": pathway_id,
        "data_size_bytes": random.randint(5000, 50000),
        "has_entry": True,
        "has_relation": True,
        "has_reaction": True,
        "fetched": False,
        "simulated": True,
        "entry_count": random.randint(20, 100),
        "relation_count": random.randint(10, 80),
        "reaction_count": random.randint(5, 30)
    }


def run_kegg_benchmark(organism: str = "hsa", max_pathways: int = 10) -> Dict:
    """
    Run KEGG KGML benchmark.
    
    Args:
        organism: Organism code
        max_pathways: Maximum number of pathways to process
        
    Returns:
        Dictionary with benchmark results
    """
    # Fetch pathway list
    pathways = fetch_kegg_pathway_list(organism, max_pathways)
    
    if not pathways:
        print("No pathways available. Using simulated data.")
        pathways = simulate_pathway_list(organism, max_pathways)
    
    print(f"\nProcessing {len(pathways)} pathways...")
    
    # Fetch KGML data for each pathway
    pathway_data = []
    successful_fetches = 0
    
    for i, pathway_id in enumerate(pathways):
        print(f"  [{i+1}/{len(pathways)}] Fetching {pathway_id}...", end=" ")
        
        data = fetch_kgml_data(pathway_id)
        
        if data is None:
            # Try simulation fallback
            data = simulate_kgml_data(pathway_id)
            print("simulated")
        else:
            successful_fetches += 1
            print("success")
        
        pathway_data.append(data)
        
        # Be nice to KEGG API - rate limit
        if i < len(pathways) - 1:
            time.sleep(0.5)
    
    # Compute statistics
    total_entries = sum(p.get("entry_count", 0) for p in pathway_data)
    total_relations = sum(p.get("relation_count", 0) for p in pathway_data)
    total_reactions = sum(p.get("reaction_count", 0) for p in pathway_data)
    
    results = {
        "organism": organism,
        "total_pathways_processed": len(pathways),
        "successful_fetches": successful_fetches,
        "simulated_fetches": len(pathways) - successful_fetches,
        "pathway_data": pathway_data,
        "statistics": {
            "total_entries": total_entries,
            "total_relations": total_relations,
            "total_reactions": total_reactions,
            "avg_entries_per_pathway": total_entries / len(pathways) if pathways else 0,
            "avg_relations_per_pathway": total_relations / len(pathways) if pathways else 0,
            "avg_reactions_per_pathway": total_reactions / len(pathways) if pathways else 0
        }
    }
    
    return results


def main():
    """Main entry point for KEGG KGML runner."""
    parser = argparse.ArgumentParser(
        description="Run KEGG KGML biological pathway benchmark with provenance tracking"
    )
    parser.add_argument(
        '--organism',
        type=str,
        default='hsa',
        help='Organism code (default: hsa for human)'
    )
    parser.add_argument(
        '--max-pathways',
        type=int,
        default=10,
        help='Maximum number of pathways to process (default: 10)'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=None,
        help='Output directory for results (default: logs/benchmarks/)'
    )
    
    args = parser.parse_args()
    
    # Set up output directory
    repo_root = Path(__file__).parent.parent
    output_dir = args.output_dir or (repo_root / "logs" / "benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Capture provenance
    commit_sha = get_git_commit_sha()
    
    provenance = {
        "commit_sha": commit_sha,
        "data_source": "KEGG REST API",
        "api_endpoint": "http://rest.kegg.jp",
        "organism": args.organism,
        "max_pathways": args.max_pathways,
        "timestamp": datetime.now().isoformat(),
        "script": "bio_kegg_run.py",
        "python_version": sys.version
    }
    
    print("="*60)
    print("KEGG KGML Biological Pathway Benchmark")
    print("="*60)
    print(f"Organism: {args.organism}")
    print(f"Max Pathways: {args.max_pathways}")
    print(f"Commit SHA: {commit_sha[:8]}...")
    print("="*60)
    
    # Run benchmark
    results = run_kegg_benchmark(args.organism, args.max_pathways)
    
    # Add benchmark metadata
    full_results = {
        **results,
        "benchmark": "kegg-kgml",
        "config": {
            "organism": args.organism,
            "max_pathways": args.max_pathways
        }
    }
    
    # Write watermarked log
    output_file = output_dir / "kegg_results.json"
    watermark_log(full_results, output_file, provenance)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Total pathways processed: {results['total_pathways_processed']}")
    print(f"Successful fetches: {results['successful_fetches']}")
    print(f"Total entries: {results['statistics']['total_entries']}")
    print(f"Total relations: {results['statistics']['total_relations']}")
    print(f"Total reactions: {results['statistics']['total_reactions']}")
    
    if results['simulated_fetches'] > 0:
        print(f"\nNote: {results['simulated_fetches']} pathway(s) used simulated data")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
