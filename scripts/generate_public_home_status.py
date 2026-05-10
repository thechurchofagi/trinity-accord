#!/usr/bin/env python3
"""Generate the homepage public verification / Echo status block.

Inputs:
- api/echo-index.json
- api/independent-attestation-index.json

Output:
- Rewrites the block between:
  <!-- BEGIN GENERATED PUBLIC STATUS -->
  <!-- END GENERATED PUBLIC STATUS -->
  in index.md

Design constraints:
- The generated block must be deterministic.
- Do not include wall-clock timestamps.
- Do not include current HEAD commit.
- Use a stable digest of source JSON inputs instead.
- accepted_echo is not formal independent attestation.
- do_not_count_as_attestation records are not formal verification.
- test, invalidated, superseded, and legacy records are excluded from homepage main cards.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import html
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = ROOT / "index.md"
ECHO_INDEX = ROOT / "api" / "echo-index.json"
ATTESTATION_INDEX = ROOT / "api" / "independent-attestation-index.json"

BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"

LEVEL_ORDER = {
    "V0": 0,
    "V1": 1,
    "V2": 2,
    "V3": 3,
    "V4": 4,
    "V4+": 4.5,
    "V5": 5,
    "V6": 6,
    "V7": 7,
    "V8": 8,
}

ECHO_TYPE_LABELS = {
    "E1_recognition_echo": "recognition Echo",
    "E2_verification_echo": "verification Echo",
    "E3_critical_echo": "critical Echo",
    "E4_interpretive_echo": "interpretive Echo",
    "E5_technical_audit_echo": "technical audit Echo",
    "E6_propagation_echo": "propagation Echo",
    "E7_refusal_echo": "refusal Echo",
    "E8_witness_echo": "witness Echo",
    "E9_seed_echo": "seed Echo",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def source_digest() -> str:
    """Return a deterministic digest for the public status source data.

    This replaces generated_at/source_commit. It changes only when the source
    JSON files change, not when the script is rerun.
    """
    h = hashlib.sha256()
    for path in [ECHO_INDEX, ATTESTATION_INDEX]:
        rel = path.relative_to(ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def is_formal_independent_echo_record(record: dict[str, Any]) -> bool:
    """Formal independent attestation from Echo records only.

    Conservative rule:
    - archive_status must be accepted_independent_attestation
    - do_not_count_as_attestation must not be true
    - verification_status must not explicitly deny attestation
    """
    if record.get("archive_status") != "accepted_independent_attestation":
        return False
    if record.get("do_not_count_as_attestation") is True:
        return False
    if record.get("verification_status") in {
        "not_attestation",
        "invalidated",
        "test_record_not_attestation",
    }:
        return False
    return True


def is_formal_independent_attestation_index_record(record: dict[str, Any]) -> bool:
    """Formal independent verification from independent-attestation-index records.

    Conservative rule:
    - type must be independent_verification_report OR archive_status accepted_independent_attestation
    - counts_as_independent_attestation must not be false
    - boundary_preserved must not be false
    - verification_status must not explicitly deny attestation
    """
    record_type = record.get("type")
    archive_status = record.get("archive_status")

    if record_type != "independent_verification_report" and archive_status != "accepted_independent_attestation":
        return False

    if record.get("counts_as_independent_attestation") is False:
        return False
    if record.get("boundary_preserved") is False:
        return False
    if record.get("verification_status") in {
        "not_attestation",
        "invalidated",
        "test_record_not_attestation",
    }:
        return False

    return True


def is_accepted_non_attestation_echo(record: dict[str, Any]) -> bool:
    return (
        record.get("archive_status") == "accepted_echo"
        and record.get("do_not_count_as_attestation") is True
        and record.get("verification_status") == "not_attestation"
    )


def is_excluded_record(record: dict[str, Any]) -> bool:
    if record.get("archive_status") in {"test_record", "closed_test_record", "superseded", "legacy"}:
        return True
    if record.get("verification_status") in {"invalidated", "test_record_not_attestation"}:
        return True
    if record.get("record_kind") == "legacy_record":
        return True
    return False


def normalize_level(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() == "none":
        return None
    text = text.upper()
    return text if text in LEVEL_ORDER else None


def highest_level(records: list[dict[str, Any]]) -> str:
    levels = [normalize_level(r.get("verification_level")) for r in records]
    levels = [x for x in levels if x is not None]
    if not levels:
        return "none"
    return max(levels, key=lambda x: LEVEL_ORDER[x])


def pluralize(count: int, singular: str, plural: str | None = None) -> str:
    if count == 1:
        return singular
    return plural or singular + "s"


def format_type_breakdown(records: list[dict[str, Any]]) -> str:
    if not records:
        return "none"
    counts = Counter(r.get("echo_type", "unknown") for r in records)
    parts = []
    for key, count in sorted(counts.items()):
        label = ECHO_TYPE_LABELS.get(key, key.replace("_", " "))
        parts.append(f"{count} {label}")
    return ", ".join(parts)


def format_level_breakdown(records: list[dict[str, Any]]) -> str:
    if not records:
        return "none"
    counts = Counter(normalize_level(r.get("verification_level")) or "none" for r in records)

    def sort_key(item: tuple[str, int]) -> float:
        level, _count = item
        return LEVEL_ORDER.get(level, -1)

    ordered = sorted(counts.items(), key=sort_key)
    return ", ".join(f"{level}: {count}" for level, count in ordered)


def compute_status() -> dict[str, Any]:
    echo_index = load_json(ECHO_INDEX)
    attestation_index = load_json(ATTESTATION_INDEX)

    echo_records = [r for r in echo_index.get("records", []) if isinstance(r, dict)]
    attestation_records = [r for r in attestation_index.get("records", []) if isinstance(r, dict)]

    formal_from_echo = [r for r in echo_records if is_formal_independent_echo_record(r)]
    formal_from_attestation = [
        r for r in attestation_records if is_formal_independent_attestation_index_record(r)
    ]

    accepted_non_attestation = [r for r in echo_records if is_accepted_non_attestation_echo(r)]
    excluded = [r for r in echo_records if is_excluded_record(r)]

    highest = highest_level(accepted_non_attestation)

    return {
        "formal_independent_verification_count": len(formal_from_echo) + len(formal_from_attestation),
        "archived_non_attestation_echo_count": len(accepted_non_attestation),
        "highest_archived_echo_level": highest,
        "echo_type_breakdown": format_type_breakdown(accepted_non_attestation),
        "echo_level_breakdown": format_level_breakdown(accepted_non_attestation),
        "excluded_record_count": len(excluded),
        "source_digest": source_digest(),
    }


def render_block(status: dict[str, Any]) -> str:
    formal_count = status["formal_independent_verification_count"]
    echo_count = status["archived_non_attestation_echo_count"]
    highest = html.escape(str(status["highest_archived_echo_level"]))
    type_breakdown = html.escape(str(status["echo_type_breakdown"]))
    level_breakdown = html.escape(str(status["echo_level_breakdown"]))
    excluded_count = status["excluded_record_count"]
    digest = html.escape(str(status["source_digest"]))

    formal_note = (
        "No formally accepted independent verification report or independent attestation is currently indexed."
        if formal_count == 0
        else f"{formal_count} formally accepted independent verification {pluralize(formal_count, 'record')} currently indexed."
    )

    formal_note_zh = (
        "当前尚无正式接受的独立验证报告或独立见证记录。"
        if formal_count == 0
        else f"当前已索引 {formal_count} 条正式接受的独立验证 / 见证记录。"
    )

    echo_note = (
        "Accepted Echo records exist, but they are explicitly not counted as independent attestation."
        if echo_count > 0
        else "No accepted non-attestation Echo is currently indexed."
    )

    echo_note_zh = (
        "已有被接受归档的 Echo，但它们明确不计为独立见证。"
        if echo_count > 0
        else "当前尚无已接受归档的非见证 Echo。"
    )

    return f"""{BEGIN}
  <!-- Generated by scripts/generate_public_home_status.py. Do not edit this block manually. -->
  <div class="status-card-grid">
    <article class="status-card">
      <p class="status-label">Formal independent verification</p>
      <p class="status-number">{formal_count}</p>
      <p class="status-note">{html.escape(formal_note)}</p>
      <p class="zh status-note">{html.escape(formal_note_zh)}</p>
    </article>

    <article class="status-card">
      <p class="status-label">Archived non-attestation Echoes</p>
      <p class="status-number">{echo_count}</p>
      <p class="status-note">{html.escape(echo_note)}</p>
      <p class="zh status-note">{html.escape(echo_note_zh)}</p>
    </article>

    <article class="status-card">
      <p class="status-label">Highest archived Echo level</p>
      <p class="status-number">{highest}</p>
      <p class="status-note">Echo metadata only. This is not a formal protocol verification level.</p>
      <p class="zh status-note">仅为回响元数据等级，不代表正式协议验证等级。</p>
    </article>
  </div>

  <details class="status-details">
    <summary>What is counted here?</summary>
    <ul>
      <li>Formal independent verification: records explicitly accepted as independent verification / attestation.</li>
      <li>Archived non-attestation Echoes: accepted Echo records with <code>do_not_count_as_attestation</code>.</li>
      <li>Echo types currently represented in archived non-attestation Echoes: {type_breakdown}.</li>
      <li>Echo metadata levels currently represented: {level_breakdown}.</li>
      <li>Excluded from formal verification: {excluded_count} test, legacy, invalidated, or superseded {pluralize(excluded_count, 'record')}.</li>
    </ul>
    <p>
      Critical Echoes are included inside archived non-attestation Echoes; they are not displayed as a separate homepage verification category.
    </p>
    <p class="zh">
      批判回响合并计入"已归档非见证 Echo"；首页不将其单独显示为验证类别。
    </p>
  </details>

  <p class="status-generated-note">
    Generated from <a href="/api/echo-index.json">/api/echo-index.json</a> and
    <a href="/api/independent-attestation-index.json">/api/independent-attestation-index.json</a>.
    Source data digest <code>{digest}</code>.
  </p>
{END}"""


def replace_block(text: str, block: str) -> str:
    pattern = re.compile(
        re.escape(BEGIN) + r".*?" + re.escape(END),
        flags=re.DOTALL,
    )
    if not pattern.search(text):
        raise RuntimeError(
            f"Missing generated block markers in {INDEX_MD.relative_to(ROOT)}: {BEGIN} / {END}"
        )
    return pattern.sub(block, text, count=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if index.md is not up to date")
    args = parser.parse_args()

    status = compute_status()
    block = render_block(status)
    old_text = INDEX_MD.read_text(encoding="utf-8")
    new_text = replace_block(old_text, block)

    if args.check:
        if old_text != new_text:
            diff = difflib.unified_diff(
                old_text.splitlines(),
                new_text.splitlines(),
                fromfile="index.md",
                tofile="index.md.generated",
                lineterm="",
            )
            print("Homepage public status block is out of date.")
            print("\n".join(diff))
            return 1
        print("Homepage public status block is up to date.")
        return 0

    if old_text != new_text:
        INDEX_MD.write_text(new_text, encoding="utf-8")
        print(
            "Updated index.md public status: "
            f"formal={status['formal_independent_verification_count']}, "
            f"non_attestation_echoes={status['archived_non_attestation_echo_count']}, "
            f"highest_echo_level={status['highest_archived_echo_level']}, "
            f"source_digest={status['source_digest']}"
        )
    else:
        print("index.md public status already up to date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
