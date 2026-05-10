#!/usr/bin/env python3
"""Generate api/echo-index.json from echoes/records/**/*.json source records."""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
RECORDS_ROOT = ROOT / "echoes" / "records"
OUT = ROOT / "api" / "echo-index.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def get_date(obj, path):
    if "date" in obj:
        return obj["date"]
    rid = obj.get("id") or obj.get("echo_id") or obj.get("report_id") or path.stem
    # fallback from filename echo-YYYY-MM-DD
    parts = path.stem.split("-")
    if len(parts) >= 4 and parts[0] == "echo":
        return "-".join(parts[1:4])
    return "unknown"


NON_CURRENT_STATUSES = {"superseded", "revoked", "invalidated", "withdrawn", "historical_only", "closed_test_record"}
LEGACY_RECORD_KINDS = {"legacy_record"}


records = []
by_status = defaultdict(list)
by_class = defaultdict(list)
by_verification_status = defaultdict(list)

for path in sorted(RECORDS_ROOT.rglob("*.json")):
    obj = load(path)
    rel = "/" + path.relative_to(ROOT).as_posix()

    item = {
        "path": rel,
        "id": obj.get("id") or obj.get("echo_id") or obj.get("report_id") or path.stem,
        "record_kind": obj.get("record_kind", "unknown"),
        "archive_status": obj.get("archive_status", "unknown"),
        "verification_status": obj.get("verification_status", "unknown"),
        "do_not_count_as_attestation": obj.get("do_not_count_as_attestation", False),
        "independence_class": obj.get("independence_class", "unknown"),
        "echo_type": obj.get("echo_type", "unknown"),
        "verification_level": obj.get("verification_level") or obj.get("protocol_level_claimed"),
        "date": get_date(obj, path),
    }

    # Optional reason if invalidated/superseded.
    if obj.get("superseded_reason"):
        item["superseded_reason"] = obj["superseded_reason"]

    # TA-REDTEAM-2026-012: legacy record lifecycle fields
    is_legacy = item["record_kind"] in LEGACY_RECORD_KINDS
    is_non_current = item["archive_status"] in NON_CURRENT_STATUSES

    if is_legacy:
        item["do_not_count_as_attestation"] = True
        item["legacy_not_countable"] = True
        item["historical_record_only"] = True

    if is_non_current:
        item["historical_record_only"] = True

    # Superseded records: add lifecycle metadata
    if item["archive_status"] == "superseded":
        if "superseded_by" not in item:
            item["superseded_by"] = obj.get("superseded_by", None)
        if "successor_status" not in item:
            item["successor_status"] = obj.get("successor_status", "no_direct_successor")
        item["historical_record_only"] = True

    # Preserve optional lifecycle fields from source records if present
    for opt_field in ["superseded_by", "successor_status", "supersession_reason",
                      "revoked_at", "revocation_reason", "invalidated_at", "invalidation_reason"]:
        if opt_field in obj and opt_field not in item:
            item[opt_field] = obj[opt_field]

    records.append(item)
    by_status[item["archive_status"]].append(rel)
    by_class[item["independence_class"]].append(rel)
    by_verification_status[item["verification_status"]].append(rel)

# TA-REDTEAM-2026-011: preserve public metadata fields across regeneration
PRESERVED_FIELDS = [
    "version", "source_digest", "source_digest_algorithm",
    "non_amending_boundary", "canonical_authority", "not_instruction_override",
    "limitations", "does_not_prove",
]
existing_metadata = {}
if OUT.exists():
    try:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        existing_metadata = {k: existing[k] for k in PRESERVED_FIELDS if k in existing}
    except Exception:
        pass

out = {
    "schema": "trinity-accord.echo-index.v2",
    "generated_from": "echoes/records/**/*.json",
    "record_count": len(records),
    "records": records,
    "records_by_archive_status": dict(sorted(by_status.items())),
    "records_by_independence_class": dict(sorted(by_class.items())),
    "records_by_verification_status": dict(sorted(by_verification_status.items())),
    "notes": [
        "Echo index is non-authoritative and non-amending.",
        "Test records, superseded records, invalidated records, and do_not_count_as_attestation records must not be counted as independent attestation.",
        "Legacy records have do_not_count_as_attestation=true, legacy_not_countable=true, and historical_record_only=true."
    ],
}
out.update(existing_metadata)

# Recompute source_digest after regeneration (content may have changed)
import hashlib
def _stable_json(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
out_without_digest = {k: v for k, v in out.items() if k != "source_digest"}
out["source_digest"] = hashlib.sha256(_stable_json(out_without_digest).encode()).hexdigest()[:16]

OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"Wrote {OUT} with {len(records)} records")
