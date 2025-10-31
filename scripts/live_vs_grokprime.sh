#!/usr/bin/env bash
# scripts/live_vs_grokprime.sh
# Simple script to run a live showdown between "live" and "grokprime" components.
# Customize commands to start your services, run comparisons, or call local scripts.

set -euo pipefail

ROOT_DIR="$(cd ""$(dirname "${BASH_SOURCE[0]}")"/.." && pwd)"

echo "Starting live vs grokprime showdown (template)..."

# Example: run two scripts (replace with your actual startup commands)
if [ -x "${ROOT_DIR}/run_live.sh" ]; then
  "${ROOT_DIR}/run_live.sh" &
  LIVE_PID=$!
  echo "Started live (pid=${LIVE_PID})"
else
  echo "No run_live.sh found or not executable — skipping start for live"
fi

if [ -x "${ROOT_DIR}/run_grokprime.sh" ]; then
  "${ROOT_DIR}/run_grokprime.sh" &
  GROK_PID=$!
  echo "Started grokprime (pid=${GROK_PID})"
else
  echo "No run_grokprime.sh found or not executable — skipping start for grokprime"
fi

# Add your comparison or evaluation logic here. For now, just wait a few seconds.
sleep 3

echo "Showdown complete (template). Cleaning up..."

if [ -n "${LIVE_PID:-}" ]; then
  kill "${LIVE_PID}" || true
fi
if [ -n "${GROK_PID:-}" ]; then
  kill "${GROK_PID}" || true
fi

echo "Done."