#!/usr/bin/env python3
"""Verify record-chain receipt contracts are consistent across API schemas, runtime, and docs."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATTERN = r"^rcg-[0-9]{8}-[a-f0-9]{12}([a-f0-9]{12})?$"
errors: list[str] = []


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


# --- Schema checks ---
intake = load_json("api/record-chain-intake-gateway.v1.json")
receipt_param = (
    intake.get("endpoints", {})
    .get("receipt", {})
    .get("path_parameters", {})
    .get("receipt_id", {})
)
require(
    receipt_param.get("pattern") == RECEIPT_PATTERN,
    "intake gateway receipt_id pattern must allow sha12 or sha24",
)

submit = load_json("api/record-chain-submit-response.v1.json")
submit_receipt = submit.get("properties", {}).get("receipt_id", {})
require(
    submit_receipt.get("pattern") == RECEIPT_PATTERN,
    "submit response receipt_id pattern must allow sha12 or sha24",
)

append_status = submit.get("properties", {}).get("append_status", {})
enum = set(append_status.get("enum", []))
for value in ["queued", "pending_dispatch_failed", "dry_run", "appended", "rejected", "duplicate"]:
    require(value in enum, f"submit response append_status enum missing {value}")

# --- Pattern acceptance/rejection ---
for rid in [
    "rcg-20260613-abcdef123456",
    "rcg-20260613-abcdef123456abcdef123456",
]:
    require(re.fullmatch(RECEIPT_PATTERN, rid) is not None, f"pattern should accept {rid}")

for rid in [
    "rcg-20260613-abcdef12345",
    "rcg-20260613-abcdef1234567",
    "rcg-20260613-abcdef123456-01",
    "rcg-20260613-abcdef123456abcdef12345",
    "rcg-20260613-abcdef123456abcdef1234567",
]:
    require(re.fullmatch(RECEIPT_PATTERN, rid) is None, f"pattern should reject {rid}")

# --- Runtime checks ---
app_text = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
require("sha12-or-sha24" in app_text, "runtime receipt handler should document sha12-or-sha24")
require(
    "[a-f0-9]{12}|[a-f0-9]{24}" in app_text or "[a-f0-9]{12}([a-f0-9]{12})?" in app_text,
    "runtime receipt regex must allow 12 or 24 hex",
)
require("RECEIPT_BACKEND_UNAVAILABLE" in app_text, "receipt endpoint must expose backend-unavailable diagnostic")
require("status_code=503" in app_text, "receipt backend failure must return 503")

# --- Doc checks ---
first_contact = (ROOT / "agent-first-contact.md").read_text(encoding="utf-8")
require("<sha12-or-sha24>" in first_contact, "agent-first-contact receipt example must mention sha12-or-sha24")
require(
    "rcg-YYYYMMDD-<sha12>" not in first_contact,
    "agent-first-contact must not show sha12-only receipt example",
)

if errors:
    raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

print("record-chain receipt contract OK")
