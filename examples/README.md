# Examples

This directory contains practical examples demonstrating the use of Evolving-sun utilities.

## Available Examples

### complete_workflow.py

A comprehensive example showing how to use all the logging utilities together in a workflow.

**Run:**
```bash
python examples/complete_workflow.py
```

**What it demonstrates:**
- Setting up loggers for different categories
- Logging informational messages with metadata
- Logging structured events as JSON
- Using convenience logging functions
- Complete workflow from startup to completion

**Output:**
The script creates log files in multiple categories:
- `logs/evolution/` - System evolution and workflow events
- `logs/security/` - Security scan results
- `logs/benchmarks/` - Performance benchmark data

Both text logs (`.log`) and JSON event logs (`.json`) are created for easy analysis.

## Creating Your Own Examples

When creating examples:

1. Add your Python script to this directory
2. Make it executable: `chmod +x examples/your_script.py`
3. Include a docstring explaining what it demonstrates
4. Add proper usage instructions
5. Document it in this README

## Tips

- Use `sys.path.insert(0, str(Path(__file__).parent.parent))` to import from src/
- Always include helpful print statements showing progress
- Log to appropriate categories (evolution, benchmarks, security, agent-activity)
- Include both simple logging and structured event logging examples
