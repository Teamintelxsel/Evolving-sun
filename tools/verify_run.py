#!/usr/bin/env python3
"""
tools/verify_run.py

Basic verification script to run automated checks for the "showdown system".
This template:
- installs requirements from requirements.txt if needed (no network-level ops here)
- runs basic linting or tests if present
- returns exit code 0 on success, non-zero on failure

Customize as needed for your project's verification steps.
"""

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def run_command(cmd, cwd=ROOT):
    print(f"> Running: {' '.join(cmd)} (cwd={{cwd}})")
    try:
        subprocess.check_call(cmd, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {{e.returncode}}")
        return e.returncode
    return 0

def main():
    parser = argparse.ArgumentParser(description="Run verification steps for the repo.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    args = parser.parse_args()

    # Example: run linters if they exist
    rc = 0

    # Run a flake8 if installed
    rc = run_command(["flake8", "."])
    if rc != 0:
        sys.exit(rc)

    if not args.skip_tests:
        # Run pytest if present
        rc = run_command(["pytest", "-q"])
        if rc != 0:
            sys.exit(rc)

    print("Verification completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())