# Security & Privacy Policy – Evolving-sun

**Last updated:** 2025-12-15  
**Maintained by:** @enderyou-lang / Teamintelxsel

---

## Core Principles

1. **No Third-Party Code/Data Uploads**  
   - No code, logs, research notes, or PII leaves this machine without explicit, audited consent. 
   - No cloud APIs for learning or reasoning (OpenAI, Anthropic, etc.).

2. **Local-First AI**  
   - All LLMs, embeddings, and agent runtimes are **local** (Ollama, llama.cpp, transformers).
   - Open-weight models only (Llama, Mistral, DeepSeek, Qwen, etc.).

3. **Explicit Network Calls**  
   - Any networked code (HackerOne API, public repos) must: 
     - Be logged in `logs/network_calls/*.json`,
     - Be scoped to authorized, in-scope targets,
     - Be reviewed in `tools/measure_metrics.py`.

4. **No Unauthorized Disclosure**  
   - HackerOne research is under NDA until disclosed by the program. 
   - No publishing of private program details, vulnerabilities, or internal notes.

5. **Audit Trail**  
   - Every intake (`data/research/intake/*.json`),
   - Every simulation (`logs/simulations/*.json`),
   - Every report draft (`logs/reports/*.json`),
   - Every metric run (`logs/metrics/*.json`)  
   is timestamped, versioned, and retained for improvement.

---

## Allowed Network Operations

| Operation | Allowed | Logging Required |
|-----------|---------|------------------|
| HackerOne API (own accounts) | ✅ | ✅ |
| Public GitHub API (read) | ✅ | ✅ |
| OpenAI/Anthropic APIs | ❌ | N/A |
| Uploading code/logs to 3rd-party | ❌ | N/A |
| Local LLM inference | ✅ | ⚠️ (optional) |

---

## Compliance

- **GDPR/CCPA:** No PII leaves local storage.
- **Bug Bounty NDAs:** All research notes remain private until official disclosure.
- **Open Source:** This repo is public, but contains **no sensitive data**—only architecture, templates, and tooling.

---

## Contact

Questions? Open an issue or contact @enderyou-lang.