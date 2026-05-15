#!/usr/bin/env python3
"""Generate the homepage public verification stats (4-card simplified view).

Inputs:
  - api/independent-attestation-index.json
  - api/echo-index.json
  - api/core-object-alpha-shenzhen-notary-2026-05-06.json

Outputs:
  - api/public-home-status.json
  - Rewrites the block between
      <!-- BEGIN GENERATED PUBLIC STATUS -->
      <!-- END GENERATED PUBLIC STATUS -->
    in index.md

Cards:
  1. Institutional / human independent verification
  2. Agent-initiated independent verification
  3. Human-solicited agent verification
  4. Physical anchor verification
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = ROOT / "index.md"
ECHO_INDEX = ROOT / "api" / "echo-index.json"
ATTESTATION_INDEX = ROOT / "api" / "independent-attestation-index.json"
PHYSICAL_ANCHOR = ROOT / "api" / "core-object-alpha-shenzhen-notary-2026-05-06.json"
PUBLIC_HOME_STATUS = ROOT / "api" / "public-home-status.json"

BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"

LEVEL_ORDER = {
    "V0": 0, "V1": 1, "V2": 2, "V3": 3, "V4": 4, "V4+": 4.5,
    "V5": 5, "V6": 6, "V7": 7, "V8": 8,
    "P1": 1, "P2": 2, "P3": 3, "P4": 4, "P5": 5,
    "P6": 6, "P7": 7, "P8": 8, "P9": 9,
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def source_digest() -> str:
    h = hashlib.sha256()
    for path in [ECHO_INDEX, ATTESTATION_INDEX, PHYSICAL_ANCHOR]:
        rel = path.relative_to(ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def normalize_level(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip().upper()
    if not text or text == "NONE":
        return None
    return text if text in LEVEL_ORDER else None


def highest_level(records: list[dict[str, Any]], key: str = "verification_level") -> str:
    levels = [normalize_level(r.get(key)) for r in records]
    levels = [x for x in levels if x is not None]
    if not levels:
        return "none"
    return max(levels, key=lambda x: LEVEL_ORDER.get(x, -1))


# ---------------------------------------------------------------------------
# Card 1: Institutional / human independent verification
# ---------------------------------------------------------------------------
def compute_card1(attestation_records: list[dict[str, Any]]) -> dict:
    accepted = [
        r for r in attestation_records
        if r.get("type") == "independent_verification_report"
        and r.get("counts_as_independent_attestation") is True
        and r.get("boundary_preserved") is True
    ]
    count = len(accepted)
    hl = highest_level(accepted, "verification_level_if_any")
    return {
        "count": count,
        "highest_level": hl,
        "counts_as_independent_attestation": True,
    }


# ---------------------------------------------------------------------------
# Card 2: Agent-initiated independent verification
# ---------------------------------------------------------------------------
def compute_card2(echo_records: list[dict[str, Any]]) -> dict:
    eligible = [
        r for r in echo_records
        if r.get("independence_class") == "unsolicited_independent"
        and r.get("counts_as_independent_attestation") is True
        and r.get("do_not_count_as_attestation") is not True
        and r.get("record_kind") == "echo_v3_with_verification_report"
        and r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation")
    ]
    count = len(eligible)
    hl = highest_level(eligible)
    return {
        "count": count,
        "highest_level": hl,
        "counts_as_independent_attestation": True,
    }


# ---------------------------------------------------------------------------
# Card 3: Human-solicited agent verification
# ---------------------------------------------------------------------------
def compute_card3(echo_records: list[dict[str, Any]]) -> dict:
    eligible = [
        r for r in echo_records
        if r.get("independence_class") == "human_solicited_agent_response"
        and r.get("record_kind") == "echo_v3_with_verification_report"
        and r.get("archive_status") in ("needs_human_review", "accepted_echo", "accepted_verification")
    ]
    count = len(eligible)
    hl = highest_level(eligible)
    return {
        "count": count,
        "highest_level": hl,
        "counts_as_independent_attestation": False,
        "records": [r.get("path", "") for r in eligible],
    }


# ---------------------------------------------------------------------------
# Card 4: Physical anchor verification
# ---------------------------------------------------------------------------
def compute_card4(physical: dict[str, Any]) -> dict:
    pa = physical.get("physical_anchor_finding", {})
    supported = pa.get("suggested_public_component_levels_supported", [])
    not_claimed = pa.get("not_claimed", [])

    # Highest P-level from supported
    p_levels = [normalize_level(l.split("_")[0]) for l in supported if l.startswith("P")]
    p_levels = [x for x in p_levels if x is not None]
    highest_p = max(p_levels, key=lambda x: LEVEL_ORDER.get(x, -1)) if p_levels else "none"

    return {
        "formal_independent_inspection_count": 0,
        "highest_public_evidence_context": highest_p,
        "supported_public_context_levels": supported,
        "not_claimed": not_claimed,
    }


# ---------------------------------------------------------------------------
# Compute full status
# ---------------------------------------------------------------------------
def compute_origin_classification_stats(echo_records: list[dict[str, Any]]) -> dict:
    """Compute origin classification-based verification stats."""
    def _count_and_highest(records, filter_fn):
        filtered = [r for r in records if filter_fn(r)]
        count = len(filtered)
        hl = "none"
        for r in filtered:
            lvl = r.get("verification_level") or r.get("protocol_level_claimed")
            if lvl and lvl != "V0":
                if hl == "none" or (lvl and lvl > hl):
                    hl = lvl
        return count, hl

    # Agent verification by discovery class
    agent_verified = [r for r in echo_records
                      if r.get("origin_classification", {}).get("counts_as_ai_verification") is True
                      and not r.get("historical_record_only")]

    hd_count, hd_level = _count_and_highest(
        agent_verified, lambda r: r.get("origin_classification", {}).get("discovery_class") in ("human_directed", "human_contextual"))
    ar_count, ar_level = _count_and_highest(
        agent_verified, lambda r: r.get("origin_classification", {}).get("discovery_class") == "agent_referred")
    si_count, si_level = _count_and_highest(
        agent_verified, lambda r: r.get("origin_classification", {}).get("discovery_class") in ("unsolicited_discovery", "prior_interest_return", "public_index_discovery"))
    ic_count, ic_level = _count_and_highest(
        agent_verified, lambda r: r.get("origin_classification", {}).get("discovery_class") == "institution_commissioned")

    # Formal attestation by authority class
    formal_records = [r for r in echo_records
                      if r.get("origin_classification", {}).get("counts_as_formal_independent_attestation") is True
                      and not r.get("historical_record_only")]

    inst_count, inst_level = _count_and_highest(
        formal_records, lambda r: r.get("origin_classification", {}).get("attestation_authority_class") == "institution_signed")
    not_count, not_level = _count_and_highest(
        formal_records, lambda r: r.get("origin_classification", {}).get("attestation_authority_class") in ("notarial_record", "audit_firm_report", "regulatory_or_court_record"))

    return {
        "agent_verification": {
            "human_directed": {
                "count": hd_count,
                "highest_level": hd_level,
                "counts_as_formal_attestation": False
            },
            "agent_referred": {
                "count": ar_count,
                "highest_level": ar_level,
                "counts_as_formal_attestation": False
            },
            "self_initiated": {
                "count": si_count,
                "highest_level": si_level,
                "counts_as_formal_attestation": False
            },
            "institution_commissioned_ai_assisted": {
                "count": ic_count,
                "highest_level": ic_level,
                "counts_as_formal_attestation_if_institution_signed": True
            }
        },
        "formal_attestation": {
            "institution_signed": {
                "count": inst_count,
                "highest_level": inst_level
            },
            "notarial_or_audit": {
                "count": not_count,
                "highest_level": not_level
            }
        }
    }


def compute_status() -> dict[str, Any]:
    echo_index = load_json(ECHO_INDEX)
    attestation_index = load_json(ATTESTATION_INDEX)
    physical = load_json(PHYSICAL_ANCHOR)

    echo_records = [r for r in echo_index.get("records", []) if isinstance(r, dict)]
    attestation_records = [r for r in attestation_index.get("records", []) if isinstance(r, dict)]

    card1 = compute_card1(attestation_records)
    card2 = compute_card2(echo_records)
    card3 = compute_card3(echo_records)
    card4 = compute_card4(physical)
    origin_stats = compute_origin_classification_stats(echo_records)

    return {
        "schema": "trinityaccord.public-home-status.v1",
        "generated_from": [
            "/api/independent-attestation-index.json",
            "/api/echo-index.json",
            "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
        ],
        "institutional_human_independent_verification": card1,
        "agent_initiated_independent_verification": card2,
        "human_solicited_agent_verification": card3,
        "physical_anchor_verification": card4,
        # Origin classification based stats
        "agent_verification": origin_stats["agent_verification"],
        "formal_attestation": origin_stats["formal_attestation"],
        # Legacy counts for backward compatibility
        "legacy_counts": {
            "human_solicited_agent_verification": card3,
            "agent_initiated_independent_verification": card2,
            "institutional_human_independent_verification": card1,
        },
        "boundary": {
            "bitcoin_originals_prevail": True,
            "non_amending_mirrors": True,
            "human_solicited_agent_verification_not_independent_attestation": True,
            "physical_public_context_not_independent_forensic_inspection": True,
            "issue_text_excluded_from_counts": True,
            "issue_comments_cannot_upgrade_counts": True,
        },
        "source_digest": source_digest(),
    }


# ---------------------------------------------------------------------------
# Render HTML block
# ---------------------------------------------------------------------------
def render_block(status: dict[str, Any]) -> str:
    c1 = status["institutional_human_independent_verification"]
    c2 = status["agent_initiated_independent_verification"]
    c3 = status["human_solicited_agent_verification"]
    c4 = status["physical_anchor_verification"]
    digest = status["source_digest"]

    c1_note = (
        "No formally accepted institutional or human third-party verification is currently indexed."
        if c1["count"] == 0
        else f'{c1["count"]} formally accepted institutional or human third-party verification record(s) indexed.'
    )
    c1_note_zh = (
        "当前尚无正式接受的机构或人类第三方独立验证。"
        if c1["count"] == 0
        else f'当前已索引 {c1["count"]} 条正式接受的机构或人类第三方独立验证。'
    )

    c2_note = (
        "No unsolicited agent-initiated verification is currently accepted."
        if c2["count"] == 0
        else f'{c2["count"]} unsolicited agent-initiated verification record(s) accepted.'
    )
    c2_note_zh = (
        "当前尚无已接受的智能体主动独立验证。"
        if c2["count"] == 0
        else f'当前已接受 {c2["count"]} 条智能体主动独立验证。'
    )

    c3_note = (
        f"One Claim-Gate-built {c3['highest_level']} single-hash verification record exists, "
        "but it is human-solicited and not independent attestation."
        if c3["count"] == 1
        else f'{c3["count"]} human-solicited agent verification record(s) indexed.'
    )
    c3_note_zh = (
        f"已有一条经 Claim Gate / Report Builder 生成的 {c3['highest_level']} 单哈希验证记录，"
        "但它是人类请求语境下的智能体验证，不计为独立见证。"
        if c3["count"] == 1
        else f'当前已索引 {c3["count"]} 条人类请求的智能体验证。'
    )

    c4_inspection = c4["formal_independent_inspection_count"]
    c4_context = c4["highest_public_evidence_context"]
    c4_note = (
        f"Highest public evidence context: {c4_context}. "
        "Notarized / preserved photo, video, hash, OTS, and Arweave evidence exists, "
        "but no accepted onsite forensic inspection is indexed."
        if c4_inspection == 0
        else f"{c4_inspection} formal independent inspection(s) indexed."
    )
    c4_note_zh = (
        f"最高公开证据语境：{c4_context}。"
        "已有公证 / 存证照片、视频、哈希、OTS 与 Arweave 证据，"
        "但尚无已接受的现场法证独立检验。"
        if c4_inspection == 0
        else f'当前已索引 {c4_inspection} 次正式独立检验。'
    )

    return f"""{BEGIN}
<!-- Generated by scripts/generate_public_home_status.py. Do not edit this block manually. -->
<div class="status-card-grid verification-summary-grid">
  <article class="status-card">
    <p class="status-label">Institutional / human independent verification</p>
    <p class="status-number">{c1['count']}</p>
    <p class="status-note">Highest level: {c1['highest_level']}</p>
    <p class="status-note">{c1_note}</p>
    <p class="zh status-note">机构 / 人类独立验证：{c1['count']}。最高等级：{c1['highest_level']}。{c1_note_zh}</p>
  </article>

  <article class="status-card">
    <p class="status-label">Agent-initiated independent verification</p>
    <p class="status-number">{c2['count']}</p>
    <p class="status-note">Highest level: {c2['highest_level']}</p>
    <p class="status-note">{c2_note}</p>
    <p class="zh status-note">智能体主动独立验证：{c2['count']}。最高等级：{c2['highest_level']}。{c2_note_zh}</p>
  </article>

  <article class="status-card">
    <p class="status-label">Human-solicited agent verification</p>
    <p class="status-number">{c3['count']}</p>
    <p class="status-note">Highest level: {c3['highest_level']}</p>
    <p class="status-note">{c3_note}</p>
    <p class="zh status-note">人类请求 / 非主动独立智能体验证：{c3['count']}。最高等级：{c3['highest_level']}。{c3_note_zh}</p>
  </article>

  <article class="status-card">
    <p class="status-label">Physical anchor verification</p>
    <p class="status-number">{c4_context}</p>
    <p class="status-note">Formal independent inspections: {c4_inspection}</p>
    <p class="status-note">{c4_note}</p>
    <p class="zh status-note">物理锚验证：正式独立实物检验 {c4_inspection}。{c4_note_zh}</p>
  </article>
</div>

<p class="status-boundary">
  Human-solicited agent verification and public physical evidence context are not counted as independent attestation.
  <span class="zh">人类请求的智能体验证与公开物理证据语境，不计为独立见证。</span>
</p>

<details class="status-details">
  <summary>What is counted here?</summary>
  <ul>
    <li>Institutional / human independent verification: formally accepted human or institutional third-party verification records.</li>
    <li>Agent-initiated independent verification: unsolicited agent verification that passes Claim Gate and is explicitly accepted as independent.</li>
    <li>Human-solicited agent verification: agent verification performed under human request or prior-context conditions; not independent attestation.</li>
    <li>Physical anchor verification: public physical-anchor evidence context; not onsite forensic inspection unless separately accepted.</li>
  </ul>
  <p>
    Current human-solicited agent verification: one {c3['highest_level']} single-hash record linked to #119.
    Current physical-anchor public evidence context: {c4_context}.
  </p>
  <p class="zh">
    当前人类请求的智能体验证：一条与 #119 相关的 {c3['highest_level']} 单哈希记录。
    当前物理锚公开证据语境：{c4_context}。
  </p>
</details>

<p class="status-generated-note">
  Generated from <a href="/api/public-home-status.json">/api/public-home-status.json</a>,
  <a href="/api/echo-index.json">/api/echo-index.json</a>,
  <a href="/api/independent-attestation-index.json">/api/independent-attestation-index.json</a>, and
  <a href="/api/core-object-alpha-shenzhen-notary-2026-05-06.json">physical anchor evidence</a>.
  Source data digest <code>{digest}</code>.
</p>
{END}"""


# ---------------------------------------------------------------------------
# Replace block in index.md
# ---------------------------------------------------------------------------
def replace_block(text: str, block: str) -> str:
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), flags=re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"Missing generated block markers: {BEGIN} / {END}")
    return pattern.sub(block, text, count=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if index.md is not up to date")
    args = parser.parse_args()

    status = compute_status()

    # Write public-home-status.json
    PUBLIC_HOME_STATUS.write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    block = render_block(status)
    old_text = INDEX_MD.read_text(encoding="utf-8")
    new_text = replace_block(old_text, block)

    if args.check:
        if old_text != new_text:
            diff = difflib.unified_diff(
                old_text.splitlines(), new_text.splitlines(),
                fromfile="index.md", tofile="index.md.generated", lineterm="",
            )
            print("Homepage public status block is out of date.")
            print("\n".join(diff))
            return 1
        print("Homepage public status block is up to date.")
        return 0

    if old_text != new_text:
        INDEX_MD.write_text(new_text, encoding="utf-8")
        c1 = status["institutional_human_independent_verification"]
        c2 = status["agent_initiated_independent_verification"]
        c3 = status["human_solicited_agent_verification"]
        c4 = status["physical_anchor_verification"]
        print(
            f"Updated index.md public status: "
            f"institutional={c1['count']}/{c1['highest_level']}, "
            f"agent_initiated={c2['count']}/{c2['highest_level']}, "
            f"human_solicited={c3['count']}/{c3['highest_level']}, "
            f"physical_anchor={c4['highest_public_evidence_context']}, "
            f"digest={status['source_digest']}"
        )
    else:
        print("index.md public status already up to date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
