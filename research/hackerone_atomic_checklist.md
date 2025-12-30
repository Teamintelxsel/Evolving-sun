# HackerOne Atomic Research Checklist

**Purpose:** Ensure every HackerOne session is authorized, in-scope, structured, and logged.

**Use before every session.**

---

## Pre-Session

- [ ] **Authorized account?**  
  - Using `enderyou-lang` or another verified H1 handle? 
  - Email matches account (no impersonation)?

- [ ] **In-scope target?**  
  - Program has public policy or private invite?
  - Asset (domain, endpoint, repo) is explicitly in-scope? 
  - No "out-of-scope" tags (e.g., 3rd-party services, DoS)?

- [ ] **Hypothesis ready?**  
  - What are you testing?  (e.g., "CORS misconfiguration on api.example.com")
  - What's the expected outcome? 

- [ ] **Tools ready?**  
  - Burp Suite, ffuf, nuclei, custom scripts?
  - Logs directory created?  (`logs/hackerone/<program_name>/`)

---

## During Session

- [ ] **Log every request/response:**  
  - Burp project saved to `logs/hackerone/<program>/burp_<date>.burp`
  - Terminal output → `logs/hackerone/<program>/terminal_<date>.log`

- [ ] **Screenshot critical findings:**  
  - Save to `logs/hackerone/<program>/screenshots/`

- [ ] **Note dead-ends:**  
  - What didn't work? (e.g., "WAF blocked SQLi payloads")
  - Save to `data/research/intake/<date>_<program>_dead_ends.json`

---

## Post-Session

- [ ] **Fill intake JSON:**  
  - Copy `research/hackerone_intake_template.json`
  - Save as `data/research/intake/<YYYY-MM-DD>_<program_slug>.json`
  - Fill all fields:  date, program_name, title, summary, tags, notes, relevant_to, confidence. 

- [ ] **Run normalization:**  
  ```bash
  python tools/normalize_research.py
  ```

- [ ] **Run reasoning:**  
  ```bash
  python bounty_reasoning.py
  ```

- [ ] **Run metrics:**  
  ```bash
  python tools/measure_metrics.py
  ```

- [ ] **Review suggestions:**  
  ```bash
  python tools/suggest_improvements.py
  ```

- [ ] **Adjust strategy for next session.**

---

## Outcome Decision Tree

| Outcome | Next Action |
|---------|-------------|
| **Valid finding** | Draft report → `logs/reports/<date>_<program>.json` |
| **Duplicate** | Log in intake JSON, tag `duplicate`, move on |
| **Informative** | Log in intake JSON, tag `informative`, save for research |
| **N/A** | Log in intake JSON, tag `n/a`, document why |
| **Out-of-scope** | STOP.  Do not report. Log why it's out-of-scope. |

---

## JSON Logging Schema

Every intake JSON **must** have:

```json
{
  "date": "YYYY-MM-DD",
  "program_name": "example-program",
  "title": "Short description",
  "summary": "Detailed summary of session, findings, or dead-ends",
  "tags":  ["cors", "api", "recon"],
  "notes": "Free-form observations",
  "relevant_to": ["future_api_testing", "cors_research"],
  "confidence": "high|medium|low",
  "outcome": "valid|duplicate|informative|n|a|out-of-scope"
}
```

---

## Privacy Reminder

- **Do not upload logs/code to OpenAI, ChatGPT, or any 3rd-party.**
- **Do not share private program details publicly.**
- **All intake JSONs are local-only until official disclosure.**

See `docs/security_policy.md` for full policy.

---

**Checklist complete?  → Start session.  Stay atomic. Stay in-scope.  Stay logged.**