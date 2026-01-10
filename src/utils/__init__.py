"""
Evolving Sun Utilities

This package contains utility functions for the Evolving Sun project.
"""

from .watermark import (
    create_watermark,
    add_watermark_to_file,
    extract_watermark,
    generate_archive_id,
    format_metadata_header
)

__all__ = [
    'create_watermark',
    'add_watermark_to_file',
    'extract_watermark',
    'generate_archive_id',
    'format_metadata_header'
]
