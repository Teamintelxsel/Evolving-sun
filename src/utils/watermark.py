"""
Watermarking utilities for Evolving Sun.

This module provides utilities for adding watermarks and metadata
to conversations, logs, and other content.
"""

import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Optional


def create_watermark(
    content_type: str,
    source: str,
    metadata: Optional[Dict] = None
) -> str:
    """
    Create a watermark for content.
    
    Args:
        content_type: Type of content (e.g., "conversation", "log", "benchmark")
        source: Source of the content (e.g., "import", "manual", "automated")
        metadata: Additional metadata to include
        
    Returns:
        Watermark string in markdown format
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    watermark = f"""<!-- Evolving Sun Watermark
Type: {content_type}
Source: {source}
Timestamp: {timestamp}
"""
    
    if metadata:
        watermark += "Metadata:\n"
        for key, value in metadata.items():
            watermark += f"  {key}: {value}\n"
    
    watermark += "-->\n"
    
    return watermark


def add_watermark_to_file(
    file_path: str,
    content_type: str,
    source: str,
    metadata: Optional[Dict] = None
) -> None:
    """
    Add watermark to an existing file.
    
    Args:
        file_path: Path to the file
        content_type: Type of content
        source: Source of the content
        metadata: Additional metadata
    """
    watermark = create_watermark(content_type, source, metadata)
    
    # Read existing content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Write watermark + content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(watermark + content)


def extract_watermark(content: str) -> Optional[Dict]:
    """
    Extract watermark metadata from content.
    
    Args:
        content: Content string to extract watermark from
        
    Returns:
        Dictionary with watermark metadata containing 'type', 'source', and 'timestamp' keys,
        or None if no watermark found. Expected watermark format:
        <!-- Evolving Sun Watermark
        Type: <type>
        Source: <source>
        Timestamp: <timestamp>
        -->
    """
    if not content.startswith("<!-- Evolving Sun Watermark"):
        return None
    
    metadata = {}
    lines = content.split('\n')
    
    for line in lines:
        if line.startswith('Type:'):
            metadata['type'] = line.split(':', 1)[1].strip()
        elif line.startswith('Source:'):
            metadata['source'] = line.split(':', 1)[1].strip()
        elif line.startswith('Timestamp:'):
            metadata['timestamp'] = line.split(':', 1)[1].strip()
        elif line.startswith('-->'):
            break
    
    return metadata if metadata else None


def generate_archive_id(title: str, timestamp: Optional[str] = None) -> str:
    """
    Generate a unique archive ID for content.
    
    Args:
        title: Content title
        timestamp: Optional timestamp (uses current time if not provided)
        
    Returns:
        Unique archive ID
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
    
    # Create a simple hash-like ID
    content = f"{title}-{timestamp}"
    hash_obj = hashlib.sha256(content.encode())
    return f"arch-{hash_obj.hexdigest()[:12]}"


def format_metadata_header(metadata: Dict, format_type: str = "yaml") -> str:
    """
    Format metadata as a header.
    
    Args:
        metadata: Metadata dictionary
        format_type: Format type ("yaml" or "json")
        
    Returns:
        Formatted metadata header string
    """
    if format_type == "yaml":
        header = "---\n"
        for key, value in metadata.items():
            if isinstance(value, list):
                header += f"{key}:\n"
                for item in value:
                    header += f"  - {item}\n"
            else:
                header += f"{key}: {value}\n"
        header += "---\n"
        return header
    elif format_type == "json":
        return "```json\n" + json.dumps(metadata, indent=2) + "\n```\n"
    else:
        raise ValueError(f"Unsupported format type: {format_type}")
