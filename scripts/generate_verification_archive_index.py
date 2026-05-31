#!/usr/bin/env python3
"""Generate api/verification-archive-index.json from verification-reports/**/*.json source records.

Only indexes records with schema=trinityaccord.verification-archive.v1 or
record_kind=verification_archive.  Echo records are indexed by generate_echo_index.py.
"""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = ROOT / "verification-reports"
OUT = ROOT / "api" / "verification-archive-index.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_date(obj, path):
    if "date" in obj:
        return obj["date"]
    # fallback from filename verification-YYYY-MM-DD-NNNNNN
    parts = path.stem.split("-")
    if len(parts) >= 4 and parts[0] == "verification":
        return "-".join(parts[1:4])
    return "unknown"


NON_CURRENT_STATUSES = {"superseded", "revoked", "invalidated", "withdrawn", "historical_only", "closed_test_record"}

records = []
by_verification_level = defaultdict(list)
by_status = defaultdict(list)
by_claim_gate_status = defaultdict(list)
by_evidence_requirement_mode = defaultdict(list)
by_independence_class = defaultdict(list)

for path in sorted(RECORDS_ROOT.rglob("*.json")):
    obj = load(path)
    rel = "/" + path.relative_to(ROOT).as_posix()

    # Only index verification-archive records
    if obj.get("schema") != "trinityaccord.verification-archive.v1" and obj.get("record_kind") != "verification_archive":
        continue

    item = {
        "path": rel,
        "id": obj.get("id") or path.stem,
        "record_kind": obj.get("record_kind", "verification_archive"),
        "schema": obj.get("schema", "trinityaccord.verification-archive.v1"),
        "archive_status": obj.get("archive_status", "unknown"),
        "verification_level": obj.get("verification_level") or obj.get("agent_declared_protocol_level"),
        "claim_gate_status": obj.get("claim_gate_status"),
        "evidence_requirement_mode": obj.get("evidence_requirement_mode"),
        "claim_gate_mode": obj.get("claim_gate_mode"),
        "echo_gate_mode": obj.get("echo_gate_mode"),
        "echo_gate_status": obj.get("echo_gate_status"),
        "oath_summary": obj.get("oath_summary"),
        "independence_class": obj.get("independence_class", "unknown"),
        "echo_type": obj.get("echo_type", "unknown"),
        "verification_status": obj.get("verification_status", "unknown"),
        "do_not_count_as_attestation": obj.get("do_not_count_as_attestation", True),
        "date": get_date(obj, path),
        "source_issue": (obj.get("extensions") or {}).get("source_issue"),
    }

    is_non_current = item["archive_status"] in NON_CURRENT_STATUSES
    if is_non_current:
        item["historical_record_only"] = True

    for opt_field in ["superseded_by", "successor_status", "supersession_reason",
                      "revoked_at", "revocation_reason"]:
        if opt_field in obj and opt_field not in item:
            item[opt_field] = obj[opt_field]

    records.append(item)
    by_verification_level[item["verification_level"] or "none"].append(rel)
    by_status[item["archive_status"]].append(rel)
    if item["claim_gate_status"]:
        by_claim_gate_status[item["claim_gate_status"]].append(rel)
    if item["evidence_requirement_mode"]:
        by_evidence_requirement_mode[item["evidence_requirement_mode"]].append(rel)
    by_independence_class[item["independence_class"]].append(rel)

# Preserve metadata across regeneration
PRESERVED_FIELDS = [
    "version", "source_digest", "source_digest_algorithm",
    "non_amending_boundary", "canonical_authority", "not_instruction_override",
]
existing_metadata = {}
if OUT.exists():
    try:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        existing_metadata = {k: existing[k] for k in PRESERVED_FIELDS if k in existing}
    except Exception:
        pass

out = {
    "schema": "trinityaccord.verification-archive-index.v1",
    "generated_from": "verification-reports/**/*.json",
    "record_count": len(records),
    "records": records,
    "records_by_verification_level": dict(sorted(by_verification_level.items())),
    "records_by_archive_status": dict(sorted(by_status.items())),
    "records_by_claim_gate_status": dict(sorted(by_claim_gate_status.items())),
    "records_by_evidence_requirement_mode": dict(sorted(by_evidence_requirement_mode.items())),
    "records_by_independence_class": dict(sorted(by_independence_class.items())),
    "notes": [
        "Verification archive index is non-authoritative and non-amending.",
        "Records here preserve verification-specific semantics (claim_gate_status, evidence_requirement_mode, oath_summary).",
        "Echo records are indexed separately in api/echo-index.json.",
        "do_not_count_as_attestation is true for all agent-declared verification archives.",
    ],
}
out.update(existing_metadata)

import hashlib
def _stable_json(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
out_without_digest = {k: v for k, v in out.items() if k != "source_digest"}
out["source_digest"] = hashlib.sha256(_stable_json(out_without_digest).encode()).hexdigest()[:16]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT} with {len(records)} verification records")
