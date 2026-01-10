#!/usr/bin/env python3
"""
Conversation Import Tool

This script imports plaintext or markdown conversation exports into the
docs/conversations/ directory with proper formatting and metadata.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


class ConversationImporter:
    """Handles importing and archiving conversations."""
    
    def __init__(self, output_dir="docs/conversations"):
        """
        Initialize the importer.
        
        Args:
            output_dir: Directory where conversations will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def sanitize_filename(self, title):
        """
        Convert title to a safe filename.
        
        Args:
            title: The conversation title
            
        Returns:
            Sanitized filename string
        """
        # Remove special characters and replace spaces with hyphens
        filename = re.sub(r'[^\w\s-]', '', title.lower())
        filename = re.sub(r'[-\s]+', '-', filename)
        return filename.strip('-')
    
    def create_metadata(self, title, tags=None, author=None):
        """
        Create metadata for the conversation.
        
        Args:
            title: Conversation title
            tags: List of tags
            author: Author name
            
        Returns:
            Dictionary with metadata
        """
        metadata = {
            "title": title,
            "imported_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "tags": tags or [],
            "author": author or "Unknown"
        }
        return metadata
    
    def format_conversation(self, content, metadata):
        """
        Format conversation with metadata header.
        
        Args:
            content: Raw conversation content
            metadata: Metadata dictionary
            
        Returns:
            Formatted conversation string
        """
        header = "---\n"
        header += f"title: {metadata['title']}\n"
        header += f"imported_at: {metadata['imported_at']}\n"
        header += f"author: {metadata['author']}\n"
        if metadata['tags']:
            header += f"tags: {', '.join(metadata['tags'])}\n"
        header += "---\n\n"
        
        return header + content
    
    def import_conversation(self, input_file, title=None, tags=None, author=None):
        """
        Import a conversation from a file.
        
        Args:
            input_file: Path to input file
            title: Conversation title (defaults to filename)
            tags: List of tags
            author: Author name
            
        Returns:
            Path to created file
        """
        input_path = Path(input_file)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        # Read content
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Use filename as title if not provided
        if not title:
            title = input_path.stem.replace('-', ' ').replace('_', ' ').title()
        
        # Create metadata
        metadata = self.create_metadata(title, tags, author)
        
        # Format conversation
        formatted_content = self.format_conversation(content, metadata)
        
        # Generate output filename
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        safe_title = self.sanitize_filename(title)
        output_filename = f"{timestamp}-{safe_title}.md"
        output_path = self.output_dir / output_filename
        
        # Handle duplicate filenames
        counter = 1
        while output_path.exists():
            output_filename = f"{timestamp}-{safe_title}-{counter}.md"
            output_path = self.output_dir / output_filename
            counter += 1
        
        # Write formatted conversation
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Also save metadata as JSON
        metadata_path = output_path.with_suffix('.meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return output_path
    
    def import_from_text(self, text, title, tags=None, author=None):
        """
        Import a conversation from text string.
        
        Args:
            text: Conversation text
            title: Conversation title
            tags: List of tags
            author: Author name
            
        Returns:
            Path to created file
        """
        # Create metadata
        metadata = self.create_metadata(title, tags, author)
        
        # Format conversation
        formatted_content = self.format_conversation(text, metadata)
        
        # Generate output filename
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        safe_title = self.sanitize_filename(title)
        output_filename = f"{timestamp}-{safe_title}.md"
        output_path = self.output_dir / output_filename
        
        # Handle duplicate filenames
        counter = 1
        while output_path.exists():
            output_filename = f"{timestamp}-{safe_title}-{counter}.md"
            output_path = self.output_dir / output_filename
            counter += 1
        
        # Write formatted conversation
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        
        # Also save metadata as JSON
        metadata_path = output_path.with_suffix('.meta.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return output_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Import conversations into the Evolving Sun archive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Import from file with title and tags
  %(prog)s --input conversation.txt --title "My Conversation" --tags ai,development
  
  # Import with author information
  %(prog)s --input chat.md --title "Code Review Discussion" --author "John Doe"
  
  # Import from stdin
  echo "This is a conversation" | %(prog)s --title "Quick Note"
        '''
    )
    
    parser.add_argument(
        '--input', '-i',
        help='Input file path (use - for stdin)',
        default=None
    )
    
    parser.add_argument(
        '--title', '-t',
        help='Conversation title',
        required=True
    )
    
    parser.add_argument(
        '--tags',
        help='Comma-separated list of tags',
        default=''
    )
    
    parser.add_argument(
        '--author', '-a',
        help='Author name',
        default=None
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        help='Output directory (default: docs/conversations)',
        default='docs/conversations'
    )
    
    args = parser.parse_args()
    
    # Parse tags
    tags = [tag.strip() for tag in args.tags.split(',') if tag.strip()]
    
    # Create importer
    importer = ConversationImporter(args.output_dir)
    
    try:
        if args.input == '-' or args.input is None:
            # Read from stdin
            content = sys.stdin.read()
            output_path = importer.import_from_text(
                content,
                args.title,
                tags=tags,
                author=args.author
            )
        else:
            # Import from file
            output_path = importer.import_conversation(
                args.input,
                title=args.title,
                tags=tags,
                author=args.author
            )
        
        print(f"✓ Conversation imported successfully!")
        print(f"  Output: {output_path}")
        print(f"  Metadata: {output_path.with_suffix('.meta.json')}")
        
    except Exception as e:
        print(f"✗ Error importing conversation: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
