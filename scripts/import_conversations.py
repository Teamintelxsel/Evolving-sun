#!/usr/bin/env python3
"""
Conversation Import Utility

This script imports plaintext or markdown conversation exports and writes them
to the docs/conversations/ directory with proper formatting and metadata.

Usage:
    python import_conversations.py <input_file> [--output-name <name>]
    
Example:
    python import_conversations.py chat_export.txt --output-name feature_discussion
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Import conversation exports to docs/conversations/",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the plaintext or markdown conversation file to import"
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default=None,
        help="Output filename (without extension). Defaults to input filename."
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["markdown", "plaintext"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing file if it exists"
    )
    
    return parser.parse_args()


def read_conversation_file(file_path):
    """Read and validate the conversation file."""
    if not os.path.exists(file_path):
        print(f"Error: Input file '{file_path}' not found.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}", file=sys.stderr)
        sys.exit(1)


def format_conversation(content, source_file, format_type="markdown"):
    """Format the conversation with metadata header."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""---
title: Imported Conversation
source: {source_file}
imported_at: {timestamp}
---

"""
    
    if format_type == "markdown":
        # If content doesn't start with markdown header, add one
        if not content.strip().startswith("#"):
            formatted_content = f"# Conversation\n\n{content}"
        else:
            formatted_content = content
    else:
        formatted_content = content
    
    return header + formatted_content


def write_conversation(output_path, content, overwrite=False):
    """Write the formatted conversation to the output directory."""
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if file exists
    if os.path.exists(output_path) and not overwrite:
        print(f"Error: Output file '{output_path}' already exists.", file=sys.stderr)
        print("Use --overwrite to replace it.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully imported conversation to: {output_path}")
    except Exception as e:
        print(f"Error writing file '{output_path}': {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the conversation import utility."""
    args = parse_arguments()
    
    # Determine output filename
    if args.output_name:
        output_name = args.output_name
    else:
        # Use input filename without extension
        output_name = Path(args.input_file).stem
    
    # Ensure output has .md extension for markdown format
    if args.format == "markdown" and not output_name.endswith(".md"):
        output_name += ".md"
    elif args.format == "plaintext" and not output_name.endswith(".txt"):
        output_name += ".txt"
    
    # Read input file
    content = read_conversation_file(args.input_file)
    
    # Format conversation
    formatted_content = format_conversation(
        content,
        args.input_file,
        args.format
    )
    
    # Determine output path (relative to script location)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    output_path = repo_root / "docs" / "conversations" / output_name
    
    # Write output file
    write_conversation(str(output_path), formatted_content, args.overwrite)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
