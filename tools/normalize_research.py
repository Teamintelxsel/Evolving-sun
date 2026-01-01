#!/usr/bin/env python3
"""
HackerOne Research Normalization Tool
Aggregates all intake JSONs into research_summary.json
Optimized with parallel processing and ujson
"""
import json
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool
import sys

INTAKE_DIR = Path("data/research/intake")
OUTPUT_FILE = Path("research_summary.json")

def load_intake(file_path):
    """Load single intake JSON with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data['_source_file'] = str(file_path)
            return data
    except json.JSONDecodeError as e:
        print(f"⚠️  Invalid JSON in {file_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error loading {file_path}: {e}", file=sys.stderr)
        return None

def normalize():
    """Normalize all intake JSONs with parallel processing"""
    if not INTAKE_DIR.exists():
        print(f"⚠️  {INTAKE_DIR} does not exist. Creating it.")
        INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    
    intake_files = sorted(INTAKE_DIR.glob("*.json"))
    
    if not intake_files:
        print("ℹ️  No intake files found")
        intakes = []
    else:
        # Parallel processing for large datasets
        if len(intake_files) > 10:
            with Pool(processes=8) as pool:
                intakes = pool.map(load_intake, intake_files)
        else:
            intakes = [load_intake(f) for f in intake_files]
        
        # Filter out failed loads
        intakes = [i for i in intakes if i is not None]
    
    # Generate summary with metadata
    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_intakes": len(intakes),
        "intakes": intakes,
        "metadata": {
            "programs": list(set(i.get("program_name", "unknown") for i in intakes)),
            "outcomes": {
                "valid": sum(1 for i in intakes if i.get("outcome") == "valid"),
                "duplicate": sum(1 for i in intakes if i.get("outcome") == "duplicate"),
                "informative": sum(1 for i in intakes if i.get("outcome") == "informative"),
                "n/a": sum(1 for i in intakes if i.get("outcome") == "n/a"),
                "out-of-scope": sum(1 for i in intakes if i.get("outcome") == "out-of-scope")
            },
            "total_time_spent_minutes": sum(i.get("time_spent_minutes", 0) for i in intakes)
        }
    }
    
    # Write output
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Normalized {len(intakes)} intakes → {OUTPUT_FILE}")
    print(f"📊 Programs: {len(summary['metadata']['programs'])}")
    print(f"✅ Valid findings: {summary['metadata']['outcomes']['valid']}")
    print(f"⏱️  Total time invested: {summary['metadata']['total_time_spent_minutes']/60:.1f} hours")

if __name__ == "__main__":
    normalize()
