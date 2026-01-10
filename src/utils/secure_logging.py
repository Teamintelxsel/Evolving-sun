"""
Secure logging utilities with watermarking for benchmark provenance.

This module provides secure logging functionality that includes
watermarking and provenance tracking for benchmark results.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def watermark_log(
    data: Dict[str, Any],
    output_path: Path,
    provenance: Optional[Dict[str, Any]] = None
) -> None:
    """
    Write a watermarked log with provenance information.
    
    This function writes benchmark results with a cryptographic watermark
    and provenance metadata to ensure result integrity and traceability.
    
    Args:
        data: The benchmark data to log
        output_path: Path to the output JSON file
        provenance: Optional provenance metadata (commit SHA, image digest, etc.)
    
    Example:
        >>> provenance = {
        ...     "commit_sha": "abc123",
        ...     "timestamp": "2026-01-10T00:00:00Z",
        ...     "script_version": "1.0"
        ... }
        >>> data = {"accuracy": 0.95, "total_cases": 100}
        >>> watermark_log(data, Path("results.json"), provenance)
    """
    # Create watermarked entry
    watermarked_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "provenance": provenance or {},
        "metadata": {
            "logged_by": "secure_logging.watermark_log",
            "version": "1.0"
        }
    }
    
    # Add integrity hash
    data_str = json.dumps(data, sort_keys=True)
    watermarked_entry["integrity_hash"] = hashlib.sha256(
        data_str.encode('utf-8')
    ).hexdigest()
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(watermarked_entry, f, indent=2)


def append_watermarked_log(
    data: Dict[str, Any],
    output_path: Path,
    provenance: Optional[Dict[str, Any]] = None
) -> None:
    """
    Append a watermarked entry to an existing log file.
    
    If the file doesn't exist, it will be created as a JSON array.
    
    Args:
        data: The benchmark data to log
        output_path: Path to the output JSON file
        provenance: Optional provenance metadata
    """
    # Create watermarked entry
    watermarked_entry = {
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "provenance": provenance or {},
        "metadata": {
            "logged_by": "secure_logging.watermark_log",
            "version": "1.0"
        }
    }
    
    # Add integrity hash
    data_str = json.dumps(data, sort_keys=True)
    watermarked_entry["integrity_hash"] = hashlib.sha256(
        data_str.encode('utf-8')
    ).hexdigest()
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing entries or create new array
    entries = []
    if output_path.exists():
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if content:
                    existing = json.loads(content)
                    if isinstance(existing, list):
                        entries = existing
                    else:
                        # Single entry, convert to list
                        entries = [existing]
        except (json.JSONDecodeError, IOError):
            # If file is corrupted, start fresh
            entries = []
    
    # Append new entry
    entries.append(watermarked_entry)
    
    # Write back to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)


def verify_log_integrity(log_path: Path) -> bool:
    """
    Verify the integrity of a watermarked log file.
    
    Args:
        log_path: Path to the log file to verify
        
    Returns:
        True if all entries have valid integrity hashes, False otherwise
    """
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        # Handle both single entry and array of entries
        entries = content if isinstance(content, list) else [content]
        
        for entry in entries:
            if "data" not in entry or "integrity_hash" not in entry:
                return False
            
            # Recompute hash
            data_str = json.dumps(entry["data"], sort_keys=True)
            computed_hash = hashlib.sha256(data_str.encode('utf-8')).hexdigest()
            
            if computed_hash != entry["integrity_hash"]:
                return False
        
        return True
    except (IOError, json.JSONDecodeError, KeyError):
        return False
