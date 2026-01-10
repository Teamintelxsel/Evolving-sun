"""
Secure logging utilities with watermarking and provenance tracking.

This module provides enhanced logging capabilities for benchmarks with
cryptographic watermarking and provenance tracking to ensure data integrity
and auditability.
"""

import hashlib
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class WatermarkedLogger:
    """Logger with cryptographic watermarking for data integrity."""
    
    def __init__(self):
        """Initialize the watermarked logger."""
        self._file_lock = threading.Lock()
    
    def _generate_watermark(self, data: Dict[str, Any], provenance: Dict[str, Any]) -> str:
        """
        Generate a cryptographic watermark for the data.
        
        Args:
            data: The data to be watermarked
            provenance: Provenance information (commit SHA, timestamps, etc.)
        
        Returns:
            Hexadecimal watermark string
        """
        # Combine data and provenance for watermark
        combined = {
            "data": data,
            "provenance": provenance,
            "timestamp": datetime.now().isoformat()
        }
        
        # Create deterministic JSON representation
        json_str = json.dumps(combined, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA-256 hash as watermark
        watermark = hashlib.sha256(json_str.encode('utf-8')).hexdigest()
        
        return watermark
    
    def watermark_log(
        self,
        filepath: str,
        data: Dict[str, Any],
        provenance: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Write watermarked log data to a file.
        
        Args:
            filepath: Path to the output file
            data: The data to be logged
            provenance: Optional provenance metadata (commit SHA, config, etc.)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Default provenance if not provided
            if provenance is None:
                provenance = {}
            
            # Add timestamp to provenance
            if "timestamp" not in provenance:
                provenance["timestamp"] = datetime.now().isoformat()
            
            # Generate watermark
            watermark = self._generate_watermark(data, provenance)
            
            # Create watermarked output
            output = {
                "data": data,
                "provenance": provenance,
                "watermark": watermark,
                "watermark_algorithm": "sha256",
                "created_at": datetime.now().isoformat()
            }
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Write with thread safety
            with self._file_lock:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(output, f, indent=2, sort_keys=True)
            
            return True
            
        except Exception as e:
            print(f"Error writing watermarked log: {e}")
            return False
    
    def verify_watermark(self, filepath: str) -> bool:
        """
        Verify the watermark of a logged file.
        
        Args:
            filepath: Path to the file to verify
        
        Returns:
            True if watermark is valid, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            stored_watermark = content.get("watermark")
            data = content.get("data")
            provenance = content.get("provenance")
            
            if not all([stored_watermark, data is not None, provenance is not None]):
                return False
            
            # Recalculate watermark
            calculated_watermark = self._generate_watermark(data, provenance)
            
            return stored_watermark == calculated_watermark
            
        except Exception as e:
            print(f"Error verifying watermark: {e}")
            return False


# Global instance for convenience
_watermarked_logger = WatermarkedLogger()


def watermark_log(
    filepath: str,
    data: Dict[str, Any],
    provenance: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Convenience function to write watermarked log data.
    
    Args:
        filepath: Path to the output file
        data: The data to be logged
        provenance: Optional provenance metadata
    
    Returns:
        True if successful, False otherwise
    """
    return _watermarked_logger.watermark_log(filepath, data, provenance)


def verify_watermark(filepath: str) -> bool:
    """
    Convenience function to verify a watermarked log file.
    
    Args:
        filepath: Path to the file to verify
    
    Returns:
        True if watermark is valid, False otherwise
    """
    return _watermarked_logger.verify_watermark(filepath)
