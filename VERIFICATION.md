# Verification steps

This repository includes a simple "showdown system". Use the following steps to verify changes locally.

Prerequisites:
- Python 3.8+
- pip
- (Optional) virtualenv

Steps:
1. Create and activate a virtual environment:
   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies:
   pip install -r requirements.txt

3. Run verification script:
   python tools/verify_run.py

Notes:
- The verification script will try to run flake8 and pytest if available.
- Adjust tools/verify_run.py to add or remove project-specific checks.