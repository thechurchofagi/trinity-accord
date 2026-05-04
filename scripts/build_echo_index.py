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
        return "unknown", "unknown"
    archive_status = data.get("archive_status", data.get("status", "unknown"))
    independence = data.get("independence_class", data.get("independence", "unknown"))
    return archive_status, independence

def main():
    files = echo_record_files()
    records = []
    by_archive = {}
    by_independence = {}

    for f in files:
        try:
            raw = f.read_text(encoding="utf-8")
            data = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"ERROR: {f} is not valid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        path = public_path(f)
        record_id = data.get("id", data.get("echo_id", f.stem))
        archive_status, independence_class = classify_record(data)
        echo_type = data.get("echo_type", data.get("type", "unknown"))
        date = infer_date(f, data)

        entry = {
            "path": path,
            "id": record_id,
            "archive_status": archive_status,
            "independence_class": independence_class,
            "echo_type": echo_type,
            "date": date,
        }
        records.append(entry)

        by_archive.setdefault(archive_status, []).append(path)
        by_independence.setdefault(independence_class, []).append(path)

    index = {
        "schema": "trinity-accord.echo-index.v2",
        "generated_from": "echoes/records/**/*.json",
        "record_count": len(records),
        "records": records,
        "records_by_archive_status": by_archive,
        "records_by_independence_class": by_independence,
        "notes": [
            "Echo index is non-authoritative and non-amending.",
            "Test records and closed test records must not be counted as independent attestation."
        ]
    }

    OUTPUT.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Built echo index: {len(records)} records → {OUTPUT.relative_to(ROOT)}")
    for r in records:
        print(f"  {r['path']} [{r['archive_status']}] [{r['independence_class']}]")

if __name__ == "__main__":
    main()
