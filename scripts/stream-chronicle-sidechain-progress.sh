#!/usr/bin/env bash
set -u
pid="${1:?capture pid required}"
interval="${CHRONICLE_PROGRESS_PUBLISH_SECONDS:-45}"
while kill -0 "$pid" 2>/dev/null; do
  python3 scripts/publish-chronicle-sidechain-progress.py --phase l2_capture --status running || true
  sleep "$interval"
done
python3 scripts/publish-chronicle-sidechain-progress.py --phase l2_capture || true
