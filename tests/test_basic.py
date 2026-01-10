#!/usr/bin/env python3
"""
Simple tests for the Evolving Sun benchmark framework.

Run with: python tests/test_basic.py
"""

import sys
import json
import hashlib
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.secure_logging import watermark_log


def test_watermark_creation():
    """Test that watermark is created correctly."""
    print("Testing watermark creation...")
    
    test_data = {
        "test": "value",
        "number": 42
    }
    
    output_path = "/tmp/test_watermark.json"
    watermark_log(test_data, output_path)
    
    # Read back
    with open(output_path, 'r') as f:
        result = json.load(f)
    
    # Verify structure
    assert 'watermark' in result, "Missing watermark"
    assert 'data' in result, "Missing data"
    
    # Verify watermark fields
    assert 'timestamp' in result['watermark'], "Missing timestamp"
    assert 'content_hash' in result['watermark'], "Missing content_hash"
    assert 'framework' in result['watermark'], "Missing framework"
    assert 'version' in result['watermark'], "Missing version"
    
    # Verify data integrity
    assert result['data'] == test_data, "Data mismatch"
    
    print("  ✓ Watermark structure is correct")
    return True


def test_hash_verification():
    """Test that hash can be verified."""
    print("Testing hash verification...")
    
    test_data = {"key": "value"}
    output_path = "/tmp/test_hash.json"
    watermark_log(test_data, output_path)
    
    # Read and recalculate hash
    with open(output_path, 'r') as f:
        result = json.load(f)
    
    # Recalculate hash from data
    data_str = json.dumps(result['data'], sort_keys=True, separators=(',', ':'))
    calculated_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    stored_hash = result['watermark']['content_hash']
    
    assert calculated_hash == stored_hash, f"Hash mismatch: {calculated_hash} != {stored_hash}"
    
    print("  ✓ Hash verification successful")
    return True


def test_framework_metadata():
    """Test framework metadata is correct."""
    print("Testing framework metadata...")
    
    test_data = {"test": "metadata"}
    output_path = "/tmp/test_metadata.json"
    watermark_log(test_data, output_path)
    
    with open(output_path, 'r') as f:
        result = json.load(f)
    
    assert result['watermark']['framework'] == 'evolving-sun-benchmarks', "Wrong framework name"
    assert result['watermark']['version'] == '1.0.0', "Wrong version"
    
    print("  ✓ Framework metadata is correct")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Evolving Sun Framework Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_watermark_creation,
        test_hash_verification,
        test_framework_metadata,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
