# Conversations Archive

This directory contains archived conversations imported using the conversation import tool.

## Purpose

The conversations archive stores:
- Technical discussions
- Design decisions
- Meeting notes
- Q&A sessions
- Development discussions
- Learning interactions

## File Structure

Each conversation consists of two files:

1. **Markdown file** (`YYYY-MM-DD-title.md`): The conversation content with metadata frontmatter
2. **Metadata file** (`YYYY-MM-DD-title.meta.json`): Structured metadata in JSON format

## Importing Conversations

Use the conversation import tool to add new conversations:

```bash
python scripts/import_conversations.py \
  --input conversation.txt \
  --title "Conversation Title" \
  --tags "tag1,tag2" \
  --author "Author Name"
```

See [docs/tools/conversation-import.md](../tools/conversation-import.md) for detailed documentation.

## Organization

Conversations are organized chronologically by import date. The filename format includes:
- ISO date (YYYY-MM-DD)
- Sanitized title

Example: `2026-01-10-api-design-discussion.md`

## Searching Conversations

### By Tag

Find conversations with specific tags by searching metadata files:

```bash
grep -r '"tag-name"' docs/conversations/*.meta.json
```

### By Date

Find conversations from a specific date:

```bash
ls docs/conversations/2026-01-10-*
```

### By Content

Search conversation content:

```bash
grep -r "search term" docs/conversations/*.md
```

## Best Practices

1. **Use descriptive titles** - Make it easy to identify the conversation topic
2. **Add relevant tags** - Help with categorization and search
3. **Include author information** - Track conversation participants
4. **Import regularly** - Don't let conversations pile up
5. **Review and curate** - Periodically review and organize archived content

## Metadata Fields

Each conversation includes:
- `title`: Conversation title
- `imported_at`: ISO 8601 timestamp of import
- `author`: Author or participant name
- `tags`: List of categorization tags

## Privacy and Security

- **Never commit sensitive information** - Remove PII, credentials, or confidential data before importing
- **Review before committing** - Always review imported conversations before pushing to the repository
- **Use .gitignore** - Add patterns to exclude sensitive files if needed
