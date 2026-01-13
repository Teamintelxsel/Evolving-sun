#!/usr/bin/env python3
"""
KEGG Pathway Benchmark Runner

This script provides integration with KEGG database via Biopython KGML/REST API
for pathway analysis with watermarked logging.

Usage:
    python scripts/bio_kegg_run.py [--pathway <id>] [--organism <code>]
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_git_commit_sha():
    """Get the current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "unknown"


def get_repo_root():
    """Get the repository root directory."""
    script_dir = Path(__file__).parent
    return script_dir.parent


def fetch_kegg_pathway(pathway_id, organism="hsa"):
    """
    Fetch KEGG pathway data via REST API.
    
    Args:
        pathway_id: KEGG pathway ID (e.g., "00010" for glycolysis)
        organism: Organism code (default: "hsa" for human)
    
    Returns:
        dict: Pathway data and metadata
    """
    import urllib.request
    import urllib.error
    
    # Construct pathway identifier
    full_pathway_id = f"{organism}{pathway_id}"
    rest_url = f"http://rest.kegg.jp/get/{full_pathway_id}"
    
    print(f"Fetching KEGG pathway: {full_pathway_id}")
    print(f"  URL: {rest_url}")
    
    try:
        # Fetch pathway data
        with urllib.request.urlopen(rest_url) as response:
            data = response.read().decode('utf-8')
        
        # Parse basic information
        lines = data.split('\n')
        pathway_info = {
            "pathway_id": full_pathway_id,
            "organism": organism,
            "data_size_bytes": len(data),
            "line_count": len(lines)
        }
        
        # Extract pathway name if present
        for line in lines:
            if line.startswith("NAME"):
                pathway_info["name"] = line.replace("NAME", "").strip()
                break
        
        # Calculate data hash for provenance
        data_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()[:16]
        pathway_info["data_hash"] = data_hash
        
        return pathway_info
    
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def fetch_kgml_pathway(pathway_id, organism="hsa"):
    """
    Fetch KEGG pathway in KGML format.
    
    Args:
        pathway_id: KEGG pathway ID
        organism: Organism code
    
    Returns:
        dict: KGML data and metadata
    """
    import urllib.request
    import urllib.error
    
    full_pathway_id = f"{organism}{pathway_id}"
    kgml_url = f"http://rest.kegg.jp/get/{full_pathway_id}/kgml"
    
    print(f"Fetching KGML for pathway: {full_pathway_id}")
    
    try:
        with urllib.request.urlopen(kgml_url) as response:
            kgml_data = response.read().decode('utf-8')
        
        kgml_info = {
            "pathway_id": full_pathway_id,
            "format": "kgml",
            "data_size_bytes": len(kgml_data),
            "has_data": len(kgml_data) > 0
        }
        
        # Try to parse with Biopython if available
        try:
            from Bio.KEGG import REST
            from Bio.KEGG.KGML import KGML_parser
            from io import StringIO
            
            # Parse KGML
            kgml_io = StringIO(kgml_data)
            pathway = KGML_parser.read(kgml_io)
            
            kgml_info["parsed"] = True
            kgml_info["pathway_name"] = pathway.name if hasattr(pathway, 'name') else None
            kgml_info["entries_count"] = len(pathway.entries) if hasattr(pathway, 'entries') else 0
            kgml_info["reactions_count"] = len(pathway.reactions) if hasattr(pathway, 'reactions') else 0
            
        except ImportError:
            kgml_info["parsed"] = False
            kgml_info["note"] = "Biopython not available for KGML parsing"
        except Exception as e:
            kgml_info["parsed"] = False
            kgml_info["parse_error"] = str(e)
        
        return kgml_info
    
    except urllib.error.HTTPError as e:
        print(f"ERROR: HTTP {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def run_kegg_benchmark(args):
    """
    Run KEGG pathway benchmark.
    
    Args:
        args: Parsed command line arguments
    
    Returns:
        dict: Results dictionary
    """
    results = {
        "benchmark": "kegg_pathway",
        "pathways": []
    }
    
    # Process each pathway
    for pathway_id in args.pathways:
        print(f"\n{'='*60}")
        print(f"Processing pathway: {pathway_id}")
        print(f"{'='*60}")
        
        # Fetch pathway data
        pathway_data = fetch_kegg_pathway(pathway_id, args.organism)
        
        if pathway_data is None:
            print(f"✗ Failed to fetch pathway {pathway_id}")
            continue
        
        # Fetch KGML if requested
        if args.fetch_kgml:
            kgml_data = fetch_kgml_pathway(pathway_id, args.organism)
            if kgml_data:
                pathway_data["kgml"] = kgml_data
        
        results["pathways"].append(pathway_data)
        print(f"✓ Successfully fetched pathway {pathway_id}")
    
    # Add summary
    results["summary"] = {
        "total_pathways": len(args.pathways),
        "successful": len(results["pathways"]),
        "failed": len(args.pathways) - len(results["pathways"]),
        "organism": args.organism,
        "fetch_kgml": args.fetch_kgml
    }
    
    return results


def main():
    """Main entry point for KEGG runner."""
    parser = argparse.ArgumentParser(
        description="Run KEGG pathway analysis with provenance tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--pathways",
        type=str,
        nargs="+",
        default=["00010"],
        help="KEGG pathway IDs to fetch (default: 00010 for glycolysis)"
    )
    
    parser.add_argument(
        "--organism",
        type=str,
        default="hsa",
        help="Organism code (default: hsa for human)"
    )
    
    parser.add_argument(
        "--fetch-kgml",
        action="store_true",
        help="Also fetch KGML format data"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: logs/benchmarks/kegg_results.json)"
    )
    
    args = parser.parse_args()
    
    # Run the benchmark
    results = run_kegg_benchmark(args)
    
    if results is None or len(results["pathways"]) == 0:
        print("\nERROR: No pathways were successfully fetched")
        return 1
    
    # Capture provenance
    provenance = {
        "commit_sha": get_git_commit_sha(),
        "organism": args.organism,
        "pathways": args.pathways,
        "fetch_kgml": args.fetch_kgml,
        "timestamp": datetime.now().isoformat(),
        "script_version": "1.0.0",
        "kegg_rest_api": "http://rest.kegg.jp"
    }
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        repo_root = get_repo_root()
        output_path = repo_root / "logs" / "benchmarks" / "kegg_results.json"
    
    # Write watermarked log
    try:
        # Import watermark_log from utils
        sys.path.insert(0, str(get_repo_root() / "src"))
        from utils.secure_logging import watermark_log
        
        success = watermark_log(str(output_path), results, provenance)
        
        if success:
            print(f"\n✓ Results saved to: {output_path}")
            print(f"  Commit SHA: {provenance['commit_sha']}")
            print(f"  Organism: {provenance['organism']}")
            print(f"  Pathways: {', '.join(provenance['pathways'])}")
        else:
            print(f"\n✗ Failed to save results to: {output_path}")
            return 1
    
    except Exception as e:
        print(f"\n✗ Error saving results: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
