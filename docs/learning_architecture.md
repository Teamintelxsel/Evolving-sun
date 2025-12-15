# Learning Architecture – Evolving-sun

**Last updated:** 2025-12-15

---

## Overview

Evolving-sun is a **local, privacy-first, self-improving system** for: 

- Security research (HackerOne, bug bounties),
- Continuous learning (agent evolution, simulations),
- High-quality reporting (structured templates, evaluations).

**No OpenAI.  No cloud uploads. All local.**

---

## Core Feedback Loop

```
┌─────────────────────────────────────────────────────────────┐
│  1.  INTAKE                                                  │
│  ├─ HackerOne session                                       │
│  ├─ Fill checklist (research/hackerone_atomic_checklist.md) │
│  └─ Save JSON (data/research/intake/*.json)                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. NORMALIZATION                                           │
│  ├─ python tools/normalize_research.py                      │
│  └─ Output:  research_summary.json                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. REASONING                                               │
│  ├─ python bounty_reasoning.py                              │
│  └─ Output:  bounty_reasoning.json (hypotheses, strategies)  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. MEASUREMENT                                             │
│  ├─ python tools/measure_metrics.py                         │
│  └─ Output: logs/metrics/*.json                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. SUGGESTIONS                                             │
│  ├─ python tools/suggest_improvements.py                    │
│  └─ Output: actionable next steps                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. APPLY → back to INTAKE (continuous improvement)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Responsibilities

| Module | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `main_performance_system.py` | Orchestration, health checks | Config, logs | Dashboards, alerts |
| `continuous_evolution.py` | Agent evolution, simulations | Agent configs | Evolved agents, logs |
| `bounty_reasoning.py` | Strategy, hypotheses | Research intake | `bounty_reasoning.json` |
| `tools/normalize_research.py` | Parse intake JSONs | `data/research/intake/*.json` | `research_summary.json` |
| `tools/measure_metrics.py` | Compute completeness, staleness | All logs/data | `logs/metrics/*.json` |
| `tools/suggest_improvements.py` | Actionable next steps | Metrics | Terminal output |

---

## HackerOne Workflow Integration

1. **Before starting:** Read `research/hackerone_atomic_checklist.md`.
2. **During research:** Take notes (tool, hypothesis, result).
3. **After session:** Fill `research/hackerone_intake_template.json` → save to `data/research/intake/<date>_<program>.json`.
4. **Run loop:**
   ```bash
   python tools/normalize_research.py
   python bounty_reasoning.py
   python tools/measure_metrics.py
   python tools/suggest_improvements.py
   ```
5. **Review suggestions:** Adjust next session's strategy.

---

## Privacy & Local-First

- **All LLMs:** Ollama (Llama 3.1, DeepSeek-R1, Qwen2.5, etc.).
- **All embeddings:** Local (sentence-transformers, llama.cpp).
- **No cloud:** No OpenAI, no Anthropic, no data uploads.
- **Audit trail:** Every JSON is timestamped and retained.

See `docs/security_policy.md` for full policy. 

---

## Extending the System

- **Add new research types:** Create a new intake template in `research/`.
- **Add new metrics:** Edit `tools/measure_metrics.py`.
- **Add new simulations:** Extend `continuous_evolution.py` or create `simulation_runner.py`.
- **Add new dashboards:** Extend `main_performance_system.py` → `dashboard_generator.py`.

---

## Questions? 

Open an issue or contact @enderyou-lang.