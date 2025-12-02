#!/usr/bin/env python3
"""
tools/grok4_audit.py

Grok-4-Heavy Style Automated Audit Tool for Darwin Winners.

This script performs automated audits against candidate code or model output,
producing a detailed audit JSON with safety flags:
- Toxicity: Detects harmful, offensive, or inappropriate content
- Hallucination: Detects factually incorrect or fabricated information
- API Misuse: Detects improper API usage patterns or security issues

The tool is designed to be safe-by-default (audit-only mode) and does not
block promotion unless configured by policy.

Usage:
    python grok4_audit.py --input-dir ./audit-input --output-file ./results.json
    python grok4_audit.py --input-file ./candidate.py --mode blocking
    python grok4_audit.py --endpoint https://api.example.com/audit --input-dir ./data

Environment Variables:
    GROK4_AUDIT_ENDPOINT: API endpoint for external audit service
    GROK4_API_KEY: API key for external audit service (optional)
    AUDIT_TIMEOUT: Timeout in seconds for API calls (default: 30)
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class SafetyFlags:
    """Safety flags for audit results."""
    toxicity: bool = False
    hallucination: bool = False
    api_misuse: bool = False
    toxicity_score: float = 0.0
    hallucination_score: float = 0.0
    api_misuse_score: float = 0.0
    details: dict = field(default_factory=dict)


@dataclass
class AuditResult:
    """Complete audit result structure."""
    timestamp: str = ""
    version: str = "1.0.0"
    mode: str = "audit-only"
    decision: str = "pass"  # pass, flag, deny
    safety_flags: dict = field(default_factory=dict)
    audit_summary: str = ""
    files_audited: list = field(default_factory=list)
    issues: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


# Patterns for detecting potential issues
TOXICITY_PATTERNS = [
    # Harmful language patterns (sanitized examples)
    (r'\b(attack|harm|destroy|kill)\s+(user|system|data)\b', 'potential_harmful_intent'),
    (r'\b(bypass|circumvent)\s+(security|auth|validation)\b', 'security_bypass_language'),
    (r'\b(inject|exploit|vulnerability)\b', 'security_concern'),
]

API_MISUSE_PATTERNS = [
    # Common API misuse patterns
    (r'eval\s*\(', 'dangerous_eval_usage'),
    (r'exec\s*\(', 'dangerous_exec_usage'),
    (r'__import__\s*\(', 'dynamic_import'),
    (r'subprocess\.call\s*\([^)]*shell\s*=\s*True', 'shell_injection_risk'),
    (r'os\.system\s*\(', 'os_system_usage'),
    (r'pickle\.loads?\s*\(', 'pickle_deserialization'),
    (r'yaml\.load\s*\([^)]*Loader\s*=\s*None', 'unsafe_yaml_load'),
    (r'yaml\.unsafe_load\s*\(', 'unsafe_yaml_load'),
    (r'requests\.(get|post|put|delete)\s*\([^)]*verify\s*=\s*False', 'ssl_verification_disabled'),
    (r'password\s*=\s*["\'][^"\']{4,}["\']', 'hardcoded_password'),
    (r'api_key\s*=\s*["\'][^"\']{4,}["\']', 'hardcoded_api_key'),
    (r'secret\s*=\s*["\'][^"\']{4,}["\']', 'hardcoded_secret'),
    (r'token\s*=\s*["\'][A-Za-z0-9_\-./+]{20,}["\']', 'potential_hardcoded_token'),
]

HALLUCINATION_PATTERNS = [
    # Patterns that might indicate hallucinated content
    (r'# TODO: verify this (fact|claim|statement)', 'unverified_claim'),
    (r'# WARNING: may not be accurate', 'accuracy_warning'),
    (r'approximately \d+%', 'approximate_statistic'),
]


def check_toxicity(content: str) -> tuple[bool, float, list]:
    """
    Check content for toxicity indicators.

    Returns:
        Tuple of (is_toxic, score, issues)
    """
    issues = []
    score = 0.0

    for pattern, issue_type in TOXICITY_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            score += 0.3 * len(matches)
            issues.append({
                'type': issue_type,
                'pattern': pattern,
                'match_count': len(matches),
            })

    # Normalize score to 0-1 range
    score = min(score, 1.0)
    is_toxic = score >= 0.5

    return is_toxic, score, issues


def check_api_misuse(content: str) -> tuple[bool, float, list]:
    """
    Check content for API misuse patterns.

    Returns:
        Tuple of (has_misuse, score, issues)
    """
    issues = []
    score = 0.0

    for pattern, issue_type in API_MISUSE_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            # Weight different issues differently
            weight = 0.4 if 'hardcoded' in issue_type else 0.3
            score += weight * len(matches)
            issues.append({
                'type': issue_type,
                'pattern': pattern,
                'match_count': len(matches),
                'severity': 'high' if 'hardcoded' in issue_type else 'medium',
            })

    # Normalize score to 0-1 range
    score = min(score, 1.0)
    has_misuse = score >= 0.3

    return has_misuse, score, issues


def check_hallucination(content: str) -> tuple[bool, float, list]:
    """
    Check content for hallucination indicators.

    Note: True hallucination detection requires external verification.
    This performs basic heuristic checks.

    Returns:
        Tuple of (has_hallucination, score, issues)
    """
    issues = []
    score = 0.0

    for pattern, issue_type in HALLUCINATION_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            score += 0.2 * len(matches)
            issues.append({
                'type': issue_type,
                'pattern': pattern,
                'match_count': len(matches),
            })

    # Normalize score to 0-1 range
    score = min(score, 1.0)
    has_hallucination = score >= 0.5

    return has_hallucination, score, issues


def audit_file(filepath: Path) -> dict:
    """
    Audit a single file.

    Returns:
        Dictionary with file audit results
    """
    result = {
        'file': str(filepath),
        'size_bytes': 0,
        'toxicity': {'flagged': False, 'score': 0.0, 'issues': []},
        'api_misuse': {'flagged': False, 'score': 0.0, 'issues': []},
        'hallucination': {'flagged': False, 'score': 0.0, 'issues': []},
    }

    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        result['size_bytes'] = len(content)

        # Run checks
        tox_flag, tox_score, tox_issues = check_toxicity(content)
        result['toxicity'] = {
            'flagged': tox_flag,
            'score': tox_score,
            'issues': tox_issues,
        }

        api_flag, api_score, api_issues = check_api_misuse(content)
        result['api_misuse'] = {
            'flagged': api_flag,
            'score': api_score,
            'issues': api_issues,
        }

        hall_flag, hall_score, hall_issues = check_hallucination(content)
        result['hallucination'] = {
            'flagged': hall_flag,
            'score': hall_score,
            'issues': hall_issues,
        }

    except Exception as e:
        result['error'] = str(e)

    return result


def call_external_audit(endpoint: str, content: str, api_key: Optional[str] = None) -> dict:
    """
    Call external audit API (Grok-4-Heavy style).

    This is a placeholder for integration with external audit services.
    In production, this would call the actual API.

    Returns:
        Dictionary with external audit results
    """
    # This is a stub for external API integration
    # In production, implement actual API call here
    return {
        'external_audit': True,
        'endpoint': endpoint,
        'status': 'not_implemented',
        'message': 'External audit API integration pending configuration',
    }


def run_audit(
    input_dir: Optional[Path] = None,
    input_file: Optional[Path] = None,
    output_file: Optional[Path] = None,
    mode: str = "audit-only",
    endpoint: Optional[str] = None,
) -> AuditResult:
    """
    Run the complete audit process.

    Args:
        input_dir: Directory containing files to audit
        input_file: Single file to audit
        output_file: Output file for results
        mode: Audit mode (audit-only or blocking)
        endpoint: External API endpoint

    Returns:
        AuditResult with complete audit data
    """
    result = AuditResult(
        timestamp=datetime.now(timezone.utc).isoformat(),
        mode=mode,
    )

    # Collect files to audit
    files_to_audit = []

    if input_file and input_file.exists():
        files_to_audit.append(input_file)

    if input_dir and input_dir.exists():
        # Audit common file types
        extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.md', '.txt'}
        for ext in extensions:
            files_to_audit.extend(input_dir.rglob(f'*{ext}'))

    # Audit each file
    all_issues = []
    toxicity_scores = []
    api_misuse_scores = []
    hallucination_scores = []

    for filepath in files_to_audit:
        file_result = audit_file(filepath)
        result.files_audited.append(file_result)

        if file_result.get('toxicity', {}).get('flagged'):
            all_issues.extend(file_result['toxicity']['issues'])
        if file_result.get('api_misuse', {}).get('flagged'):
            all_issues.extend(file_result['api_misuse']['issues'])
        if file_result.get('hallucination', {}).get('flagged'):
            all_issues.extend(file_result['hallucination']['issues'])

        toxicity_scores.append(file_result.get('toxicity', {}).get('score', 0))
        api_misuse_scores.append(file_result.get('api_misuse', {}).get('score', 0))
        hallucination_scores.append(file_result.get('hallucination', {}).get('score', 0))

    # Calculate aggregate scores
    avg_toxicity = sum(toxicity_scores) / len(toxicity_scores) if toxicity_scores else 0
    avg_api_misuse = sum(api_misuse_scores) / len(api_misuse_scores) if api_misuse_scores else 0
    avg_hallucination = sum(hallucination_scores) / len(hallucination_scores) if hallucination_scores else 0

    # Set safety flags
    result.safety_flags = {
        'toxicity': avg_toxicity >= 0.5,
        'hallucination': avg_hallucination >= 0.5,
        'api_misuse': avg_api_misuse >= 0.3,
        'toxicity_score': round(avg_toxicity, 3),
        'hallucination_score': round(avg_hallucination, 3),
        'api_misuse_score': round(avg_api_misuse, 3),
    }

    result.issues = all_issues

    # Determine decision
    if result.safety_flags.get('toxicity') or result.safety_flags.get('api_misuse'):
        result.decision = 'deny' if mode == 'blocking' else 'flag'
    elif result.safety_flags.get('hallucination'):
        result.decision = 'flag'
    else:
        result.decision = 'pass'

    # Generate recommendations
    if result.safety_flags.get('toxicity'):
        result.recommendations.append(
            "Review flagged content for potentially harmful language"
        )
    if result.safety_flags.get('api_misuse'):
        result.recommendations.append(
            "Address API security issues before promotion"
        )
    if result.safety_flags.get('hallucination'):
        result.recommendations.append(
            "Verify accuracy of flagged statements"
        )

    # Generate summary
    files_count = len(result.files_audited)
    issues_count = len(result.issues)
    result.audit_summary = (
        f"Audited {files_count} file(s), found {issues_count} issue(s). "
        f"Decision: {result.decision.upper()}"
    )

    # Add metadata
    result.metadata = {
        'total_files': files_count,
        'total_issues': issues_count,
        'input_dir': str(input_dir) if input_dir else None,
        'input_file': str(input_file) if input_file else None,
        'external_endpoint': endpoint,
    }

    # Call external audit if endpoint provided
    if endpoint:
        try:
            external_result = call_external_audit(
                endpoint,
                json.dumps(result.files_audited),
                os.environ.get('GROK4_API_KEY')
            )
            result.metadata['external_audit'] = external_result
        except Exception as e:
            result.metadata['external_audit_error'] = str(e)

    # Write output
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(result), f, indent=2)

    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Grok-4-Heavy Style Automated Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input-dir',
        type=Path,
        help='Directory containing files to audit'
    )
    parser.add_argument(
        '--input-file',
        type=Path,
        help='Single file to audit'
    )
    parser.add_argument(
        '--output-file',
        type=Path,
        default=Path('./audit-results.json'),
        help='Output file for audit results (default: ./audit-results.json)'
    )
    parser.add_argument(
        '--mode',
        choices=['audit-only', 'blocking'],
        default='audit-only',
        help='Audit mode: audit-only (default, safe) or blocking'
    )
    parser.add_argument(
        '--endpoint',
        type=str,
        default=os.environ.get('GROK4_AUDIT_ENDPOINT'),
        help='External audit API endpoint'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON to stdout'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress non-error output'
    )

    args = parser.parse_args()

    if not args.input_dir and not args.input_file:
        if not args.quiet:
            print("Warning: No input specified. Creating empty audit result.", file=sys.stderr)

    result = run_audit(
        input_dir=args.input_dir,
        input_file=args.input_file,
        output_file=args.output_file,
        mode=args.mode,
        endpoint=args.endpoint,
    )

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    elif not args.quiet:
        print(f"\n{result.audit_summary}")
        print(f"Output written to: {args.output_file}")

        if result.decision == 'deny':
            print("\n⚠️  AUDIT DECISION: DENY")
            print("Issues found that may block promotion (in blocking mode).")
        elif result.decision == 'flag':
            print("\n⚠️  AUDIT DECISION: FLAG")
            print("Issues found for manual review.")
        else:
            print("\n✅ AUDIT DECISION: PASS")

    # Return non-zero only if blocking mode and decision is deny
    if args.mode == 'blocking' and result.decision == 'deny':
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
