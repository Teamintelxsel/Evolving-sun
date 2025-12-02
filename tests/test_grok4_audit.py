#!/usr/bin/env python3
"""
tests/test_grok4_audit.py

Unit tests for the Grok-4 audit tool.
"""

import json
import sys
import tempfile
from pathlib import Path

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

import pytest  # noqa: E402

from grok4_audit import (  # noqa: E402
    AuditResult,
    SafetyFlags,
    check_toxicity,
    check_api_misuse,
    check_hallucination,
    audit_file,
    run_audit,
)


class TestCheckToxicity:
    """Tests for toxicity detection."""

    def test_clean_content_no_toxicity(self):
        """Clean content should not be flagged as toxic."""
        content = "This is a normal function that processes data."
        is_toxic, score, issues = check_toxicity(content)

        assert is_toxic is False
        assert score < 0.5
        assert len(issues) == 0

    def test_security_bypass_language_detected(self):
        """Security bypass language should be detected."""
        content = "This function will bypass security checks."
        is_toxic, score, issues = check_toxicity(content)

        assert score > 0
        assert len(issues) > 0
        assert any("security_bypass" in issue["type"] for issue in issues)

    def test_harmful_intent_language_detected(self):
        """Potentially harmful intent language should be detected."""
        content = "This code will attack user data directly."
        is_toxic, score, issues = check_toxicity(content)

        assert score > 0
        assert len(issues) > 0


class TestCheckApiMisuse:
    """Tests for API misuse detection."""

    def test_clean_code_no_misuse(self):
        """Clean code should not be flagged for API misuse."""
        content = """
def calculate_sum(a, b):
    return a + b
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert has_misuse is False
        assert score < 0.3
        assert len(issues) == 0

    def test_eval_usage_detected(self):
        """eval() usage should be detected."""
        content = """
result = eval(user_input)
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("eval" in issue["type"] for issue in issues)

    def test_exec_usage_detected(self):
        """exec() usage should be detected."""
        content = """
exec(dynamic_code)
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("exec" in issue["type"] for issue in issues)

    def test_hardcoded_password_detected(self):
        """Hardcoded passwords should be detected."""
        content = """
password = "supersecret123"
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("hardcoded_password" in issue["type"] for issue in issues)

    def test_hardcoded_api_key_detected(self):
        """Hardcoded API keys should be detected."""
        content = """
api_key = "sk-1234567890abcdef"
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("api_key" in issue["type"] for issue in issues)

    def test_shell_injection_risk_detected(self):
        """Shell injection risks should be detected."""
        content = """
subprocess.call(cmd, shell=True)
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("shell_injection" in issue["type"] for issue in issues)

    def test_pickle_loads_detected(self):
        """Pickle deserialization should be detected."""
        content = """
data = pickle.loads(untrusted_data)
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("pickle" in issue["type"] for issue in issues)

    def test_ssl_verification_disabled_detected(self):
        """Disabled SSL verification should be detected."""
        content = """
response = requests.get(url, verify=False)
"""
        has_misuse, score, issues = check_api_misuse(content)

        assert score > 0
        assert len(issues) > 0
        assert any("ssl" in issue["type"] for issue in issues)


class TestCheckHallucination:
    """Tests for hallucination detection."""

    def test_clean_content_no_hallucination(self):
        """Clean content should not be flagged for hallucination."""
        content = "This function returns the sum of two numbers."
        has_hallucination, score, issues = check_hallucination(content)

        assert has_hallucination is False
        assert score < 0.5
        assert len(issues) == 0

    def test_unverified_claim_detected(self):
        """Unverified claims should be detected."""
        content = """
# TODO: verify this fact before deployment
"""
        has_hallucination, score, issues = check_hallucination(content)

        assert score > 0
        assert len(issues) > 0


class TestAuditFile:
    """Tests for file auditing."""

    def test_audit_clean_file(self):
        """Auditing a clean file should pass."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello():
    print("Hello, world!")
""")
            f.flush()
            filepath = Path(f.name)

        try:
            result = audit_file(filepath)

            assert result['file'] == str(filepath)
            assert result['size_bytes'] > 0
            assert result['toxicity']['flagged'] is False
            assert result['api_misuse']['flagged'] is False
            assert result['hallucination']['flagged'] is False
        finally:
            filepath.unlink()

    def test_audit_file_with_issues(self):
        """Auditing a file with issues should detect them."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
password = "secret123"
result = eval(user_input)
""")
            f.flush()
            filepath = Path(f.name)

        try:
            result = audit_file(filepath)

            assert result['api_misuse']['flagged'] is True
            assert len(result['api_misuse']['issues']) > 0
        finally:
            filepath.unlink()

    def test_audit_nonexistent_file(self):
        """Auditing a nonexistent file should handle error gracefully."""
        filepath = Path("/nonexistent/file.py")
        result = audit_file(filepath)

        assert 'error' in result


class TestRunAudit:
    """Tests for the main audit runner."""

    def test_run_audit_empty_input(self):
        """Running audit with no input should return empty result."""
        result = run_audit()

        assert result.decision == 'pass'
        assert len(result.files_audited) == 0
        assert result.safety_flags['toxicity'] is False

    def test_run_audit_single_file(self):
        """Running audit on a single file should work."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')")
            f.flush()
            filepath = Path(f.name)

        try:
            result = run_audit(input_file=filepath)

            assert result.decision == 'pass'
            assert len(result.files_audited) == 1
        finally:
            filepath.unlink()

    def test_run_audit_directory(self):
        """Running audit on a directory should process all files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "file1.py").write_text("print('hello')")
            (tmppath / "file2.py").write_text("print('world')")

            result = run_audit(input_dir=tmppath)

            assert result.decision == 'pass'
            assert len(result.files_audited) == 2

    def test_run_audit_blocking_mode_with_issues(self):
        """Blocking mode should set decision to deny on issues."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
password = "secret123"
api_key = "sk-abcdefghijklmnop1234"
""")
            f.flush()
            filepath = Path(f.name)

        try:
            result = run_audit(input_file=filepath, mode='blocking')

            assert result.decision == 'deny'
            assert result.safety_flags['api_misuse'] is True
        finally:
            filepath.unlink()

    def test_run_audit_audit_only_mode_with_issues(self):
        """Audit-only mode should set decision to flag on issues."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
password = "secret123"
""")
            f.flush()
            filepath = Path(f.name)

        try:
            result = run_audit(input_file=filepath, mode='audit-only')

            assert result.decision == 'flag'
            assert result.safety_flags['api_misuse'] is True
        finally:
            filepath.unlink()

    def test_run_audit_output_file(self):
        """Running audit should write results to output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            input_file = tmppath / "test.py"
            output_file = tmppath / "results.json"

            input_file.write_text("print('hello')")

            run_audit(input_file=input_file, output_file=output_file)

            assert output_file.exists()

            with open(output_file) as f:
                saved_result = json.load(f)

            assert saved_result['decision'] == 'pass'

    def test_run_audit_generates_recommendations(self):
        """Audit should generate recommendations for issues."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
password = "secret123"
""")
            f.flush()
            filepath = Path(f.name)

        try:
            result = run_audit(input_file=filepath)

            assert len(result.recommendations) > 0
            assert any("API" in rec or "security" in rec.lower() for rec in result.recommendations)
        finally:
            filepath.unlink()

    def test_run_audit_metadata(self):
        """Audit should include metadata."""
        result = run_audit()

        assert 'total_files' in result.metadata
        assert 'total_issues' in result.metadata

    def test_run_audit_timestamp(self):
        """Audit should include timestamp."""
        result = run_audit()

        assert result.timestamp != ""
        assert "T" in result.timestamp  # ISO format


class TestAuditResultDataclass:
    """Tests for the AuditResult dataclass."""

    def test_default_values(self):
        """Default values should be safe."""
        result = AuditResult()

        assert result.mode == "audit-only"
        assert result.decision == "pass"
        assert result.version == "1.0.0"

    def test_safety_flags_default(self):
        """Safety flags should default to empty dict."""
        result = AuditResult()

        assert isinstance(result.safety_flags, dict)


class TestSafetyFlagsDataclass:
    """Tests for the SafetyFlags dataclass."""

    def test_default_values(self):
        """Default values should be safe (False)."""
        flags = SafetyFlags()

        assert flags.toxicity is False
        assert flags.hallucination is False
        assert flags.api_misuse is False
        assert flags.toxicity_score == 0.0
        assert flags.hallucination_score == 0.0
        assert flags.api_misuse_score == 0.0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_binary_file_handling(self):
        """Binary files should be handled gracefully."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.bin', delete=False) as f:
            f.write(b'\x00\x01\x02\x03\xff\xfe')
            filepath = Path(f.name)

        try:
            # Should not raise an exception
            result = audit_file(filepath)
            assert 'file' in result
        finally:
            filepath.unlink()

    def test_empty_file(self):
        """Empty files should be handled gracefully."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            filepath = Path(f.name)

        try:
            result = audit_file(filepath)

            assert result['size_bytes'] == 0
            assert result['toxicity']['flagged'] is False
        finally:
            filepath.unlink()

    def test_large_content_performance(self):
        """Large content should be processed without issues."""
        # Create content with 10,000 lines
        content = "\n".join(["print('line')"] * 10000)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            filepath = Path(f.name)

        try:
            result = audit_file(filepath)
            assert result['size_bytes'] > 0
        finally:
            filepath.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
