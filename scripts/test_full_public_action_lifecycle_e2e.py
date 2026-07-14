#!/usr/bin/env python3
"""Run the full lifecycle simulation with explicit isolated Gateway config."""
from __future__ import annotations

import os

os.environ["TRINITY_REPO_FULL_NAME"] = "isolated/full-lifecycle-audit"
os.environ["TRINITY_TARGET_BRANCH"] = "isolated-audit"
os.environ["TRINITY_GITHUB_TOKEN"] = "isolated-test-token-not-used-for-network"
os.environ["TRINITY_SUBMIT_WRITE_MODE"] = "github_contents_pending"
os.environ["TRINITY_DISPATCH_APPEND_WORKFLOW"] = "0"

from full_public_action_lifecycle_e2e import main

if __name__ == "__main__":
    raise SystemExit(main())
