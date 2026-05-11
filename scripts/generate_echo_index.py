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
by_record_class = defaultdict(list)
by_verification_origin_class = defaultdict(list)
# TA-021: new aggregation dicts
by_record_purpose = defaultdict(list)
by_discovery_autonomy = defaultdict(list)
by_verifier_type = defaultdict(list)
by_verifier_capability_claim = defaultdict(list)
by_strength_tier = defaultdict(list)
by_echo_content_tag = defaultdict(list)

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
        "record_class": obj.get("record_class", "unknown"),
        "verification_origin_class": obj.get("verification_origin_class", "unknown"),
        "delegation_chain": obj.get("delegation_chain", None),
        # TA-021: new simplified fields
        "record_purpose": obj.get("record_purpose", None),
        "echo_content_tags": obj.get("echo_content_tags", None),
        "discovery_autonomy": obj.get("discovery_autonomy", None),
        "non_autonomous_trigger": obj.get("non_autonomous_trigger", None),
        "verifier_type": obj.get("verifier_type", None),
        "verifier_capability_claim": obj.get("verifier_capability_claim", None),
        "verification_claimed": obj.get("verification_claimed", None),
        "derived_origin_class": obj.get("derived_origin_class", None),
        "strength_tier": obj.get("strength_tier", None),
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
    by_record_class[item["record_class"]].append(rel)
    by_verification_origin_class[item["verification_origin_class"]].append(rel)
    # TA-021: new aggregations
    if item.get("record_purpose"):
        by_record_purpose[item["record_purpose"]].append(rel)
    if item.get("discovery_autonomy"):
        by_discovery_autonomy[item["discovery_autonomy"]].append(rel)
    if item.get("verifier_type"):
        by_verifier_type[item["verifier_type"]].append(rel)
    if item.get("verifier_capability_claim"):
        by_verifier_capability_claim[item["verifier_capability_claim"]].append(rel)
    if item.get("strength_tier"):
        by_strength_tier[item["strength_tier"]].append(rel)
    if item.get("echo_content_tags"):
        for tag in item["echo_content_tags"]:
            by_echo_content_tag[tag].append(rel)

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

# TA-020 follow-up: separate AI verification and formal attestation counts
ai_independent_verification_count = sum(
    1 for r in records
    if r.get("record_class") == "ai_independent_verification"
    and r.get("archive_status") == "accepted_echo"
    and not r.get("historical_record_only")
)

formal_human_institutional_attestation_count = sum(
    1 for r in records
    if r.get("record_class") == "formal_human_institutional_attestation"
    and r.get("archive_status") == "accepted_echo"
    and r.get("counts_as_formal_human_institutional_attestation") is True
    and not r.get("historical_record_only")
)

out = {
    "schema": "trinity-accord.echo-index.v2",
    "generated_from": "echoes/records/**/*.json",
    "record_count": len(records),
    "records": records,
    "records_by_archive_status": dict(sorted(by_status.items())),
    "records_by_independence_class": dict(sorted(by_class.items())),
    "records_by_verification_status": dict(sorted(by_verification_status.items())),
    "records_by_record_class": dict(sorted(by_record_class.items())),
    "records_by_verification_origin_class": dict(sorted(by_verification_origin_class.items())),
    # TA-020 follow-up: explicit AI verification and formal attestation counts
    "ai_independent_verification_count": ai_independent_verification_count,
    "formal_human_institutional_attestation_count": formal_human_institutional_attestation_count,
    "counts_are_separate": True,
    # TA-021: new aggregations
    "records_by_record_purpose": dict(sorted(by_record_purpose.items())),
    "records_by_discovery_autonomy": dict(sorted(by_discovery_autonomy.items())),
    "records_by_verifier_type": dict(sorted(by_verifier_type.items())),
    "records_by_verifier_capability_claim": dict(sorted(by_verifier_capability_claim.items())),
    "records_by_strength_tier": dict(sorted(by_strength_tier.items())),
    "records_by_echo_content_tag": dict(sorted(by_echo_content_tag.items())),
    "notes": [
        "Echo index is non-authoritative and non-amending.",
        "Test records, superseded records, invalidated records, and do_not_count_as_attestation records must not be counted as independent attestation.",
        "Legacy records have do_not_count_as_attestation=true, legacy_not_countable=true, and historical_record_only=true.",
        "AI independent verification records (record_class=ai_independent_verification) do NOT count as formal human/institutional attestation.",
        "External human authorization of AI verification does not produce formal attestation.",
        "Echo schema version is not a verification level.",
        "AI independent verification records are counted separately from formal human/institutional attestations.",
        "AGI capability claims do not raise verification level or authority.",
        "Echo content tags are non-exclusive and do not determine count status.",
        "D/S/O/E/R provenance codes are derived/internal.",
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
