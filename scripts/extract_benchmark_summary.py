#!/usr/bin/env python3
"""
Extract benchmark summary from orchestrated results for GitHub Actions workflow summary.
"""
import json
import sys
import os


def main():
    """Extract and print benchmark summary from latest orchestrated results."""
    # Get the latest orchestrated results file
    latest_result = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not latest_result or not os.path.exists(latest_result):
        print("No results file found")
        return
    
    try:
        with open(latest_result, 'r') as f:
            data = json.load(f)
        
        # Print suite statuses
        for suite_name, suite_data in data.get('suites', {}).items():
            status = suite_data.get('status', 'unknown')
            emoji = '✅' if status in ['completed', 'success'] else '❌'
            print(f'{emoji} **{suite_name.upper()}**: {status}')
    except Exception as e:
        print(f'Error reading results: {e}')


if __name__ == '__main__':
    main()
