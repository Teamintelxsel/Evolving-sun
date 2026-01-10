# Conversation Import Tool

The conversation import tool (`scripts/import_conversations.py`) allows you to import plaintext or markdown conversation exports into the conversation archive.

## Features

- Import conversations from files or stdin
- Automatic metadata generation
- Tag support for categorization
- Author attribution
- Duplicate filename handling
- Timestamped archival
- JSON metadata export

## Usage

### Basic Usage

Import a conversation from a file:

```bash
python scripts/import_conversations.py --input conversation.txt --title "My Conversation"
```

### With Tags

Add tags for categorization:

```bash
python scripts/import_conversations.py \
  --input conversation.txt \
  --title "AI Development Discussion" \
  --tags "ai,development,copilot"
```

### With Author

Specify the author:

```bash
python scripts/import_conversations.py \
  --input chat.md \
  --title "Code Review Session" \
  --author "John Doe"
```

### From Stdin

Import conversation text directly:

```bash
echo "This is my conversation content" | python scripts/import_conversations.py \
  --title "Quick Note"
```

## Options

- `--input, -i`: Input file path (use `-` for stdin, default: stdin)
- `--title, -t`: Conversation title (required)
- `--tags`: Comma-separated list of tags
- `--author, -a`: Author name
- `--output-dir, -o`: Output directory (default: `docs/conversations`)

## Output Format

The tool creates two files for each imported conversation:

### 1. Markdown File

Format: `YYYY-MM-DD-title.md`

### 2. Metadata JSON File

Format: `YYYY-MM-DD-title.meta.json`
