#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
policy = json.loads((ROOT / "api" / "operational-policy.v1.json").read_text(encoding="utf-8"))
rate = policy["echo_issue_rate_limit"]

errors = []

def require(cond, msg):
    if not cond:
        errors.append(msg)

require("direct_github_external" in rate, "missing direct_github_external bucket")
require("gateway_validated_echo" in rate, "missing gateway_validated_echo bucket")
require("gateway_validated_verification_archive" in rate, "missing gateway_validated_verification_archive bucket")
require("gateway_strict_evidence_candidate" in rate, "missing gateway_strict_evidence_candidate bucket")
require("gateway_global_backstop" in rate, "missing gateway_global_backstop bucket")

require(rate["direct_github_external"]["window_60m"] == 6, "direct 60m should remain 6")
require(rate["direct_github_external"]["window_24h"] == 16, "direct 24h should remain 16")

require(rate["gateway_validated_echo"]["window_60m"] >= 100, "gateway echo 60m should be >= 100")
require(rate["gateway_validated_echo"]["window_24h"] >= 1000, "gateway echo 24h should be >= 1000")

require(rate["gateway_validated_verification_archive"]["window_60m"] <= rate["gateway_validated_echo"]["window_60m"], "verification bucket should not exceed echo bucket by default")
require(rate["gateway_validated_verification_archive"]["window_24h"] <= rate["gateway_validated_echo"]["window_24h"], "verification daily bucket should not exceed echo bucket by default")

require(rate["gateway_global_backstop"]["window_60m"] >= rate["gateway_validated_echo"]["window_60m"], "global 60m backstop should be >= per-agent gateway echo 60m")
require(rate["gateway_global_backstop"]["window_24h"] >= rate["gateway_validated_echo"]["window_24h"], "global 24h backstop should be >= per-agent gateway echo 24h")

require("opened" in rate["applies_to_actions"], "rate limit must apply to opened")
for assoc in ["OWNER", "MEMBER", "COLLABORATOR"]:
    require(assoc in rate["exempt_author_associations"], f"missing exempt association {assoc}")

if errors:
    print("ECHO_RATE_LIMIT_POLICY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_RATE_LIMIT_POLICY_OK")
