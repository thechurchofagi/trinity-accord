#!/usr/bin/env python3
"""Build api/echo-index.json from all echoes/records/**/*.json files."""
from pathlib import Path
import json
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "echoes" / "records"
OUTPUT = ROOT / "api" / "echo-index.json"

def echo_record_files():
    if not RECORDS_DIR.exists():
        return []
    return sorted(x for x in RECORDS_DIR.rglob("*.json") if x.is_file())

def public_path(path):
    return "/" + path.relative_to(ROOT).as_posix()

def infer_date(path, data):
    if isinstance(data, dict):
        for key in ("date", "echo_date", "created_at", "timestamp", "submitted_at_utc"):
            if key in data:
                val = str(data[key])
                # Handle ISO datetime strings like "2026-04-25T00:00:00Z"
                if "T" in val:
                    val = val.split("T")[0]
                return val
    # infer from filename
    name = path.stem
    parts = name.split("-")
    # Skip prefix like "echo" if present; find first YYYY-MM-DD candidate
    start = 0
    if len(parts) >= 4 and not parts[0].isdigit():
        start = 1
    if len(parts) >= start + 3:
        candidate = "-".join(parts[start:start+3])
        try:
            datetime.strptime(candidate, "%Y-%m-%d")
            return candidate
        except ValueError:
            pass
    return "unknown"

def classify_record(data):
    if not isinstance(data, dict):
        return "unknown", "unknown", "unknown", False, "unknown", False
    archive_status = data.get("archive_status", data.get("status", "unknown"))
    independence = data.get("independence_class", data.get("independence", "unknown"))
    record_kind = data.get("record_kind", "unknown")
    verification_status = data.get("verification_status", "unknown")

    # Derive do_not_count_as_attestation from independence_class and wrapper field
    # Priority: explicit field > derived from independence_class
    explicit_do_not_count = data.get("do_not_count_as_attestation")
    if explicit_do_not_count is not None:
        do_not_count = explicit_do_not_count
    else:
        # human_solicited_agent_response must not count as attestation
        do_not_count = independence == "human_solicited_agent_response"
    # Also check wrapper-level counts_as_independent_attestation
    if data.get("counts_as_independent_attestation") is False:
        do_not_count = True

    # Derive counts_as_independent_attestation
    # Conservative: human_solicited, test_record, self_reported, unknown,
    # agent_submitted_with_prior_context => never count as independent
    NOT_INDEPENDENT_CLASSES = {
        "human_solicited_agent_response",
        "test_record",
        "self_reported",
        "unknown",
        "agent_submitted_with_prior_context",
    }
    explicit_counts = data.get("counts_as_independent_attestation")
    if explicit_counts is not None:
        counts_as_independent = explicit_counts
    elif independence in NOT_INDEPENDENT_CLASSES:
        counts_as_independent = False
    else:
        counts_as_independent = not do_not_count

    return archive_status, independence, record_kind, do_not_count, verification_status, counts_as_independent

def main():
    files = echo_record_files()
    records = []
    by_archive = {}
    by_independence = {}
    by_verification_status = {}
    by_record_kind = {}

    for f in files:
        try:
            raw = f.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"ERROR: {f} is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        path = public_path(f)
        record_id = data.get("id", data.get("echo_id", f.stem))
        archive_status, independence_class, record_kind, do_not_count, verification_status, counts_as_independent = classify_record(data)
        echo_type = data.get("echo_type", data.get("type", "unknown"))
        date = infer_date(f, data)

        entry = {
            "path": path,
            "id": record_id,
            "archive_status": archive_status,
            "independence_class": independence_class,
            "echo_type": echo_type,
            "echo_type_deprecated": True,
            "date": date,
            "record_kind": record_kind,
            "verification_status": verification_status,
            "verification_level": data.get("verification_level") or data.get("protocol_level_claimed"),
            "do_not_count_as_attestation": do_not_count,
            "counts_as_independent_attestation": counts_as_independent,
        }
        records.append(entry)

        by_archive.setdefault(archive_status, []).append(path)
        by_independence.setdefault(independence_class, []).append(path)
        by_verification_status.setdefault(verification_status, []).append(path)
        by_record_kind.setdefault(record_kind, []).append(path)

    # Count accepted-only records (used by homepage Reception)
    ACCEPTED_STATUSES = {"accepted_echo", "accepted_verification", "accepted_attestation"}
    accepted_count = sum(1 for r in records if r["archive_status"] in ACCEPTED_STATUSES)

    # Build per-status counts for transparency
    record_count_by_status = {}
    for status, paths in by_archive.items():
        record_count_by_status[status] = len(paths)

    index = {
        "schema": "trinity-accord.echo-index.v2",
        "generated_from": "echoes/records/**/*.json",
        "record_count": len(records),
        "accepted_record_count": accepted_count,
        "record_count_by_status": record_count_by_status,
        "records": records,
        "records_by_archive_status": by_archive,
        "records_by_independence_class": by_independence,
        "records_by_verification_status": by_verification_status,
        "records_by_record_kind": by_record_kind,
        "notes": [
            "Echo index is non-authoritative and non-amending.",
            "record_count includes all records (legacy, superseded, pending review, etc.).",
            "accepted_record_count includes only accepted_echo, accepted_verification, accepted_attestation.",
            "Homepage Reception uses accepted_record_count from echo-index + agent-declared counts.",
            "Test records and closed test records must not be counted as independent attestation.",
            "echo_type field is deprecated for new submissions. Echo is a single unified type. Existing records preserve echo_type for backward compatibility only.",
            "echo_type_deprecated=true on each record signals this field is legacy metadata."
        ]
    }

    OUTPUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built echo index: {len(records)} records → {OUTPUT.relative_to(ROOT)}")
    for r in records:
        print(f"  {r['path']} [{r['archive_status']}] [{r['independence_class']}]")

if __name__ == "__main__":
    main()
