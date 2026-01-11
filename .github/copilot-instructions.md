Project: Evolving-sun — AI coding instructions for Copilot agents

Purpose
- Help AI coding agents become productive quickly in this repo (primarily a set
  of PowerShell utilities and small pipelines for HackerOne intake/reporting).

Quick picture
-- This repository contains PowerShell tooling (see h1.ps1) that
  processes intake JSON files, runs Python analysis tools, and renders Markdown
  draft reports. The pipeline expects a Windows/PowerShell environment.

Key files
- h1.ps1: main pipeline script. It:
  - Calls `Run-PythonTools -ToolsList $PythonTools` (hook for Python analysis).
  - Finds latest intake JSON in `$IntakeDir` and parses it with `ConvertFrom-Json`.
  - Optionally calls `ollama run llama3.1` to generate an AI summary.
  - Writes draft Markdown reports to the intake directory.

Developer workflows (what agents should assume)
- Execution: run PowerShell from repo root. Example to run the script directly:
  `pwsh -File h1.ps1` (or dot-source to import helper functions before invoking
  a pipeline function if the script is structured as a module).
- Requirements: Ollama (optional), Python (for tools), and Git. The script
  checks for `ollama` with `Get-Command` and uses the model name `llama3.1`.
- Commits: the script includes commented-out git add/commit lines — preserve
  that behavior or make commits explicit in separate automation steps.

Project conventions and patterns
- PowerShell 5.1 compatibility: prefer simple language features (the script
  uses constructs compatible with 5.1). Avoid relying on very new PowerShell
  behaviors unless adding a note and fallbacks.
- Single-responsibility scripts: `h1.ps1` orchestrates smaller steps (Python
  analysis, JSON intake parsing, optional AI summary). When adding features,
  keep commands modular so they can be invoked independently for testing.
- Slug/file naming: reports use a sanitized `safeSlug` and are written into the
  intake directory with a `report_<intakeBase>_<slug>.md` pattern — preserve
  this naming when modifying output logic.

Integration points (what to be careful about)
- Ollama: script calls `ollama run llama3.1 "<prompt>"`. Respect prompt
  formatting and return trimming; if you change model names or CLI flags,
  update the script comments and fallbacks.
- Python tools: `Run-PythonTools` is invoked with `$PythonTools` — agents
  should search for that function or assume it is defined earlier or provided
  externally; do not remove the call unless replacing it with equivalent
  functionality.
- Intake JSON: code expects specific fields (title, summary, notes, tags,
  confidence, outcome, program_name, relevant_to, submitted, report_id,
  bounty_received). When changing parsing, preserve fallback behavior.

Editing guidance for AI agents
- Keep changes minimal and focused: modify `h1.ps1` in-place (follow existing
  indentation and style). If adding new files, update the script to import
  or dot-source them.
- Preserve backward compatibility: keep default fallbacks for missing JSON
  fields and the existing severity-guess heuristics unless intentionally
  improving them with tests or explicit migration notes.
- Tests: none discovered; if you add tests, include a small README section
  showing how to run them and prefer platform-agnostic commands where possible.

Examples (copy-edit tasks an agent may do)
- Add a CLI flag to `h1.ps1` to select intake directory (preserve defaults).
- Make Ollama calls robust: add a timeout and a clear, documented fallback
  when `ollama` or the model is missing.
- Split large `h1.ps1` sections into helper functions and keep the high-level
  orchestration at the bottom of the file.

What I couldn't infer (ask the user)
- Where `$IntakeDir`, `$PythonTools`, and other global variables are defined
  (search or confirm preferred defaults).
- Any CI/CD or scheduled runners that invoke the script (cron/Task Scheduler,
  GitHub Actions, etc.).

Next steps
- If you want, I can:
  - Scan the repo for other hidden integration files and incorporate them.
  - Split `h1.ps1` into smaller modules and add a README for running locally.

Please review and tell me which gaps to fill or whether to merge as-is.
