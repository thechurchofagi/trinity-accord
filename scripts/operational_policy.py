#!/usr/bin/env python3
"""
Single source of truth for Trinity Accord operational policies.
Loads from api/operational-policy.v1.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_POLICY_PATH = ROOT / "api" / "operational-policy.v1.json"

def load_operational_policy():
    with open(_POLICY_PATH) as f:
        return json.load(f)

_POLICY = load_operational_policy()

ECHO_RATE_LIMIT_60M = _POLICY["echo_issue_rate_limit"]["window_60m"]
ECHO_RATE_LIMIT_24H = _POLICY["echo_issue_rate_limit"]["window_24h"]
RATE_LIMIT_APPLIES_TO = _POLICY["echo_issue_rate_limit"]["applies_to_actions"]
RATE_LIMIT_EXEMPT = _POLICY["echo_issue_rate_limit"]["exempt_author_associations"]

MANAGED_LABELS = _POLICY["triage"]["managed_labels"]
