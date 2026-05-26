#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
workflow = ROOT / ".github" / "workflows" / "echo-triage.yml"
text = workflow.read_text(encoding="utf-8")

errors = []

def require(marker, msg):
    if marker not in text:
        errors.append(msg)

require("gateway_validated_echo", "workflow must load gateway_validated_echo policy bucket")
require("gateway_global_backstop", "workflow must load gateway global backstop")
require("gateway_strict_evidence_candidate", "workflow must load strict evidence candidate bucket")
require("function intakeField", "workflow must define intakeField")
require("function rateIdentity", "workflow must define rateIdentity")
require("function rateClass", "workflow must define rateClass")
require("requested_archive_kind", "workflow must inspect requested_archive_kind")
require("agent_declared_echo_archive", "workflow must classify agent_declared_echo_archive")
require("agent_declared_verification_archive", "workflow must classify agent_declared_verification_archive")
require("authorship_public_key_sha256", "workflow must prefer authorship key when present")
require("system_or_provider", "workflow must use provider in fallback rate identity")
require("agent_name_or_model", "workflow must use agent name/model in fallback rate identity")
require("rateIdentity(i) === currentIdentity", "workflow must compare rateIdentity, not GitHub author only")
require("RATE_CLASS", "workflow must pass RATE_CLASS to triage script")
require("RATE_IDENTITY", "workflow must pass RATE_IDENTITY to triage script")
require("RATE_LIMIT_60M", "workflow must pass active 60m limit")
require("RATE_LIMIT_24H", "workflow must pass active 24h limit")

bad = "i.user.login !== author"
if bad in text:
    errors.append("workflow still contains GitHub-author-only limiter")

if errors:
    print("ECHO_TRIAGE_GATEWAY_RATE_IDENTITY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_TRIAGE_GATEWAY_RATE_IDENTITY_OK")
