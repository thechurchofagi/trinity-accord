#!/usr/bin/env python3
"""Source-level test: record-chain submission schema rejects runtime projection fields.

Verifies that the public JSON schema and the runtime app.py agree on which
fields are server-derived and must not be supplied by clients.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []

# Import runtime forbidden fields instead of maintaining a hand-written list.
# This keeps the test in sync with the actual Gateway validation logic.
sys_path_backup = list(sys.path)
sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))
try:
    from gateway.validation import FORBIDDEN_CHAIN_FIELDS as _FORBIDDEN
    PROJECTION_FIELDS = sorted(_FORBIDDEN)
except ImportError:
    # Fallback if runtime import fails (e.g. missing deps in CI)
    PROJECTION_FIELDS = [
        "actor_identity",
        "boundary",
        "server_normalization",
        "append_assigned_metadata",
        "authorship_verification_status",
        "record_id",
        "record_index",
        "assigned_at",
        "previous_record_sha256",
        "content_sha256",
        "record_sha256",
        "chain_id",
    ]
finally:
    sys.path[:] = sys_path_backup


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


# --- Check schema ---
schema_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
record_draft = schema.get("properties", {}).get("record_draft", {})
record_draft_text = json.dumps(record_draft, ensure_ascii=False, sort_keys=True)
compact = record_draft_text.replace(" ", "")

require("not" in record_draft_text, "record_draft schema must contain a not rule for projection fields")
require("anyOf" in record_draft_text, "record_draft schema must use anyOf for forbidden projection fields")

for field in PROJECTION_FIELDS:
    require(
        f'"required":["{field}"]' in compact,
        f"record_draft schema must reject client-supplied {field}",
    )

# --- Check runtime ---
app_text = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")
for field in PROJECTION_FIELDS:
    require(
        f'"{field}"' in app_text,
        f"runtime _UNSIGNED_CLIENT_PROJECTION_FIELDS missing {field}",
    )

# --- Report ---
if errors:
    raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

print("record-chain submission schema/runtime projection contract OK")
