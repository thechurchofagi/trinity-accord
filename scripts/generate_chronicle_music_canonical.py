#!/usr/bin/env python3
"""Generate machine-readable canonical music audit index from CHRONICLE-MUSIC-TABLE.md.

Local-only. No network.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "nft-text-descriptions"
TABLE = DIR / "CHRONICLE-MUSIC-TABLE.md"
OUT = DIR / "chronicle-music-canonical.json"

BOUNDARY = {
    "metadata_lyrics_and_song_references_only": True,
    "not_audio_verification": True,
    "not_copyright_verification": True,
    "not_canonical_authority": True,
    "not_truth_proof": True,
    "not_successor_reception": True,
    "bitcoin_originals_remain_canonical_authority": True,
}

ROW_RE = re.compile(r"^\|\s*#(?P<ordinal>\d+)\s*\|\s*(?P<date>[^|]+?)\s*\|\s*(?P<title>[^|]+?)\s*\|\s*(?P<status>[^|]+?)\s*\|")


def classify_status(status: str) -> str:
    s = status.strip()
    if s == "首次":
        return "first"
    if s.startswith("同 #"):
        return "duplicate"
    if s == "仅引用" or s.startswith("仅引用"):
        return "title_only_reference"
    if "无歌曲" in s:
        return "no_song"
    if "2首" in s or "有歌词" in s:
        return "lyrics_record"
    return "other"


def main() -> int:
    if not TABLE.exists():
        print(f"missing {TABLE}")
        return 1

    entries = []
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        ordinal = int(m.group("ordinal"))
        title_raw = m.group("title").strip()
        status_raw = m.group("status").strip()
        date = m.group("date").strip()
        title = None if title_raw in {"—", "-", ""} else title_raw
        normalized = classify_status(status_raw)

        duplicate_of = None
        dup = re.search(r"同\s*#(\d+)", status_raw)
        if dup:
            duplicate_of = int(dup.group(1))

        entries.append({
            "ordinal": ordinal,
            "date": date,
            "song_title": title,
            "status_raw": status_raw,
            "status": normalized,
            "duplicate_of": duplicate_of,
        })

    errors = []
    if len(entries) != 175:
        errors.append(f"expected 175 rows, got {len(entries)}")
    ords = [e["ordinal"] for e in entries]
    if ords != list(range(1, 176)):
        errors.append("ordinals must be exactly #1..#175")

    lyrics_records = sum(1 for e in entries if e["status"] in {"first", "duplicate", "lyrics_record"})
    title_only = sum(1 for e in entries if e["status"] == "title_only_reference")
    no_song = sum(1 for e in entries if e["status"] == "no_song")

    # Validate counts match actual data (header may differ if data was updated).
    # Expected: lyrics_records + title_only + no_song == 175
    if lyrics_records + title_only + no_song != 175:
        errors.append(f"total mismatch: {lyrics_records}+{title_only}+{no_song}={lyrics_records+title_only+no_song}, expected 175")

    first_titles = {}
    for e in entries:
        if e["status"] == "first" and e["song_title"]:
            first_titles[e["ordinal"]] = e["song_title"]

    out = {
        "schema": "trinityaccord.chronicle-music-canonical.v1",
        "generated_from": [
            "nft-text-descriptions/CHRONICLE-MUSIC-TABLE.md"
        ],
        "total_nfts": 175,
        "lyrics_records": lyrics_records,
        "title_only_references": title_only,
        "no_song_entries": no_song,
        "unique_song_count": "approximately_70",
        "unique_song_count_is_exact": False,
        "boundary": BOUNDARY,
        "entries": entries,
    }

    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if errors:
        print("CHRONICLE_MUSIC_CANONICAL_FAIL")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("CHRONICLE_MUSIC_CANONICAL_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
