"""Secure logging utilities with watermarking for benchmark results."""

import json
import hashlib
import datetime
from pathlib import Path
from typing import Any, Dict


def watermark_log(data: Dict[str, Any], output_path: str) -> None:
    """
    Write benchmark results to a JSON file with security watermark.
    
    Args:
        data: Dictionary containing benchmark results
        output_path: Path to write the watermarked JSON file
    
    The watermark includes:
    - Timestamp of generation
    - SHA256 hash of the data content
    - Framework version metadata
    """
    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create watermark metadata
    timestamp = datetime.datetime.utcnow().isoformat() + 'Z'
    
    # Calculate content hash (excluding watermark itself)
    content_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
    content_hash = hashlib.sha256(content_str.encode()).hexdigest()
    
    # Build watermarked output
    watermarked_data = {
        'watermark': {
            'timestamp': timestamp,
            'content_hash': content_hash,
            'framework': 'evolving-sun-benchmarks',
            'version': '1.0.0'
        },
        'data': data
    }
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(watermarked_data, f, indent=2, ensure_ascii=False)
    
    print(f"Results written to {output_path} with watermark")
    print(f"Content hash: {content_hash}")
