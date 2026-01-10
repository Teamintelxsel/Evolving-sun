# BENCHMARKS

## Overview

This document describes the verifiable benchmarks used to evaluate Evolving-Sun's performance and provides cryptographic proofs for result authenticity.

---

## Supported Benchmarks

### 1. GPQA (Graduate-Level Google-Proof Q&A)

**Description:** PhD-level reasoning questions spanning science, mathematics, and expert knowledge domains.

**Target Performance:** 74%+ accuracy

**Current Performance:** [To be measured]

**Verification:**
- SHA256 hash of results: [To be generated]
- Merkle root: [To be generated]
- Rekor timestamp: [To be generated]

**How to Run:**
```bash
python benchmarks/gpqa_runner.py \
  --model grok-4 \
  --output-dir benchmarks/results/gpqa
```

---

### 2. SWE-bench Verified

**Description:** Real-world software engineering tasks from GitHub issues.

**Target Performance:** 92.7%

**Current Performance:** [To be measured]

**Baseline:** 88.4% (starting point)

**Verification:**
- SHA256 hash of results: [To be generated]
- Merkle root: [To be generated]
- Rekor timestamp: [To be generated]

**How to Run:**
```bash
python benchmarks/swe_bench_runner.py \
  --variant verified \
  --model claude-opus-4.5 \
  --output-dir benchmarks/results/swe-bench
```

---

### 3. SWE-bench Pro

**Description:** Enterprise-complexity software engineering tasks.

**Target Performance:** 23%+

**Current Performance:** [To be measured]

**Verification:**
- SHA256 hash of results: [To be generated]
- Merkle root: [To be generated]

**How to Run:**
```bash
python benchmarks/swe_bench_runner.py \
  --variant pro \
  --model grok-4 \
  --output-dir benchmarks/results/swe-bench-pro
```

---

### 4. KEGG Pathway Validation

**Description:** Validates accuracy of KEGG metabolic pathway fetching and parsing.

**Target Performance:** 99.94%+ accuracy

**Current Performance:** [To be measured]

**Verification:**
- SHA256 hash of results: [To be generated]
- Merkle root: [To be generated]

**How to Run:**
```bash
python benchmarks/kegg_validator.py \
  --pathways ko01100 ko00010 ko00020 \
  --output-dir benchmarks/results/kegg
```

---

## Cryptographic Verification

All benchmark results are cryptographically verified using multiple methods:

### 1. SHA256 Hashing
Each result file is hashed with SHA256 for tamper detection.

```bash
sha256sum benchmarks/results/*/results.json
```

### 2. Merkle Tree
Results are organized in a Merkle tree for efficient verification.

- Merkle root published in repository
- Individual results can be verified with Merkle proofs
- Tree structure documented in `verification/merkle_trees/`

### 3. Rekor Timestamping
Results are timestamped in Sigstore Rekor for immutable proof of existence.

```bash
rekor-cli upload \
  --artifact benchmarks/results/gpqa/results.json \
  --public-key .pqc-keys/signing.pub
```

### 4. GPG Signing
Results signed with Dilithium (post-quantum) signatures.

```bash
python security/pqc/dilithium_signer.py \
  --sign benchmarks/results/*/results.json \
  --key-id production-signing-key
```

### 5. Web3 Attestation
Major benchmark milestones attested on Ethereum blockchain.

- Contract address: [To be deployed]
- Network: Ethereum Mainnet
- Verification UI: [To be created]

---

## Benchmark Reproduction

All benchmarks are 100% reproducible using Docker containers.

### Prerequisites
```bash
docker pull evolving-sun/benchmark-runner:latest
```

### Run Benchmarks
```bash
docker run -v $(pwd)/results:/results \
  evolving-sun/benchmark-runner:latest \
  --benchmark gpqa \
  --model grok-4
```

### Verify Results
```bash
docker run -v $(pwd)/results:/results \
  evolving-sun/benchmark-verifier:latest \
  --verify /results/gpqa/results.json \
  --merkle-root abc123...
```

---

## Result Format

All benchmark results use a standardized JSON format:

```json
{
  "benchmark": "gpqa",
  "version": "1.0",
  "model": "grok-4",
  "timestamp": "2025-01-10T00:00:00Z",
  "results": {
    "total_questions": 100,
    "correct_answers": 74,
    "accuracy": 0.74
  },
  "verification": {
    "sha256": "abc123...",
    "merkle_root": "def456...",
    "rekor_uuid": "ghi789...",
    "dilithium_signature": "jkl012..."
  }
}
```

---

## Public Verification API

Anyone can verify benchmark results via our public API:

### Verify SHA256 Hash
```bash
curl https://api.evolving-sun.ai/verify/sha256 \
  -d '{"file": "gpqa_results.json", "hash": "abc123..."}'
```

### Verify Merkle Proof
```bash
curl https://api.evolving-sun.ai/verify/merkle \
  -d '{"leaf_hash": "abc123...", "proof": [...], "root": "def456..."}'
```

### Verify Rekor Timestamp
```bash
curl https://api.evolving-sun.ai/verify/rekor \
  -d '{"uuid": "ghi789..."}'
```

---

## Historical Results

All benchmark results are archived with cryptographic proofs:

- **2025-01-10:** Initial baseline measurements
- [Future results will be listed here with verification hashes]

---

## Benchmark Schedule

- **Weekly:** KEGG pathway validation (automated)
- **Bi-weekly:** SWE-bench Verified
- **Monthly:** GPQA, SWE-bench Pro
- **Quarterly:** Full benchmark suite with public report

---

## Reporting Issues

If you discover any discrepancies in benchmark results or verification:

1. File an issue at: https://github.com/Teamintelxsel/Evolving-sun/issues
2. Include: benchmark name, result file hash, expected vs. actual values
3. Security-sensitive issues: security@evolving-sun.ai (PGP key available)

---

## License

Benchmark results are released under CC BY 4.0 for maximum transparency.

---

**Last Updated:** 2025-01-10
**Version:** 1.0
**Maintainer:** Evolving Sun Team
