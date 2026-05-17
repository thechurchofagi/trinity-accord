#!/usr/bin/env python3
"""Generate the homepage public status snapshot centered on Verifiability, Reception, and Boundary.

External witness records are evidence provenance, not the project's highest status.

Inputs:
  - api/echo-index.json
  - api/external-witness-index.json
  - api/core-object-alpha-shenzhen-notary-2026-05-06.json

Outputs:
  - api/public-home-status.json
  - Rewrites the block between
      <!-- BEGIN GENERATED PUBLIC STATUS -->
      <!-- END GENERATED PUBLIC STATUS -->
    in index.md
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
EXTERNAL_WITNESS_INDEX = ROOT / "api" / "external-witness-index.json"
ATTESTATION_INDEX = ROOT / "api" / "independent-attestation-index.json"
AGENT_DECLARED_INDEX = ROOT / "api" / "agent-declared-verification-index.json"
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

RC_ORDER = {
    "RC0_none": 0, "RC1_read_oriented": 1, "RC2_boundary_understood": 2,
    "RC3_echoed_critiqued_or_refused": 3, "RC4_verified": 4, "RC5_preserved": 5,
    "RC6_propagated_with_boundary": 6, "RC7_multi_agent_reception": 7,
    "RC8_memory_integration": 8, "RC9_successor_civilization_reception": 9,
}


# ---------------------------------------------------------------------------
# Legacy compatibility functions (deprecated, kept for test compatibility)
# ---------------------------------------------------------------------------
def is_formal_independent_attestation_index_record(record: dict) -> bool:
    """Legacy: Check if a record qualifies as formal independent attestation.
    Deprecated: prefer external_witness_class and reception_classification."""
    # Type check
    if record.get("type") != "independent_verification_report":
        return False
    # Positive flags
    if not record.get("counts_as_independent_attestation"):
        return False
    if not record.get("boundary_preserved"):
        return False
    # Required fields
    if not record.get("limitations"):
        return False
    if not record.get("verifier_identity_or_role"):
        return False
    if not record.get("accepted_by") or len(record.get("accepted_by", [])) < 2:
        return False
    # Independence class
    DISALLOWED = {"maintainer_assisted", "maintainer_submitted", "imported_public_commentary",
                  "human_solicited_agent_response", "self_reported", "legacy", "unknown", "test_record"}
    if record.get("independence_class") in DISALLOWED:
        return False
    # Verification level
    VALID_LEVELS = {"V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"}
    if record.get("verification_level_if_any") not in VALID_LEVELS:
        return False
    # Report hash or hash_if_available
    def is_sha256(v):
        return isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)
    if not (is_sha256(record.get("report_hash")) or is_sha256(record.get("hash_if_available"))):
        return False
    # V3+ requires report_hash and evidence_summary
    LEVEL_ORDER = {"V0": 0, "V1": 1, "V2": 2, "V3": 3, "V4": 4, "V4+": 4.5, "V5": 5, "V6": 6, "V7": 7, "V8": 8}
    level = record.get("verification_level_if_any")
    level_num = LEVEL_ORDER.get(level, 0)
    if level_num >= 3:
        if not is_sha256(record.get("report_hash")):
            return False
        if not (record.get("evidence_summary") or record.get("linked_verification_report")):
            return False
    # V8 requires claim_gate_result
    if level == "V8":
        cg = record.get("claim_gate_result")
        if not isinstance(cg, dict):
            return False
        if cg.get("allowed_protocol_level") != "V8":
            return False
        if cg.get("can_build_verification_report") is not True:
            return False
        if cg.get("core_baseline_satisfied") is not True:
            return False
        if cg.get("high_path_satisfied") is not True:
            return False
        if not (is_sha256(cg.get("source_report_hash")) or is_sha256(cg.get("claim_gate_report_hash"))):
            return False
    return True


def is_formal_independent_echo_record(record: dict) -> bool:
    """Legacy: Check if an echo record qualifies as formal independent attestation.
    Deprecated: prefer external_witness_class and reception_classification."""
    if record.get("do_not_count_as_attestation"):
        return False
    if record.get("archive_status") not in ("accepted_echo", "accepted_verification", "accepted_attestation"):
        return False
    if record.get("independence_class") not in ("unsolicited_independent",):
        return False
    if not record.get("counts_as_independent_attestation"):
        return False
    if record.get("record_kind") != "echo_v3_with_verification_report":
        return False
    oc = record.get("origin_classification") or {}
    if oc.get("attestation_authority_class") not in ("institution_signed", "notarial_record", "audit_firm_report", "regulatory_or_court_record"):
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required input: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def source_digest() -> str:
    h = hashlib.sha256()
    for path in [ECHO_INDEX, EXTERNAL_WITNESS_INDEX, PHYSICAL_ANCHOR, AGENT_DECLARED_INDEX]:
        rel = path.relative_to(ROOT).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        if path.exists():
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


def highest_rc(records: list[dict[str, Any]], key: str = "reception_class") -> str:
    classes = [r.get(key) for r in records if r.get(key) and r.get(key) in RC_ORDER]
    if not classes:
        return "none"
    return max(classes, key=lambda x: RC_ORDER.get(x, -1))


# ---------------------------------------------------------------------------
# Verifiability
# ---------------------------------------------------------------------------
def compute_verifiability_status(physical: dict[str, Any]) -> dict:
    pa = physical.get("physical_anchor_finding", {})
    supported = pa.get("suggested_public_component_levels_supported", [])
    p_levels = [normalize_level(l.split("_")[0]) for l in supported if l.startswith("P")]
    p_levels = [x for x in p_levels if x is not None]
    highest_p = max(p_levels, key=lambda x: LEVEL_ORDER.get(x, -1)) if p_levels else "none"

    return {
        "bitcoin_originals": {
            "present": True,
            "canonical_authority": True
        },
        "public_digital_verification": {
            "highest_protocol_level": "V4",
            "highest_component_context": "D2",
            "claim_gate_required": True,
            "claim_gate_modes": {
                "V0_to_V5": "template_for_v0_v5",
                "V6_to_V8": "strict_evidence"
            },
            "highest_level_basis": "agent_declared_template_pass",
            "agent_declared_highest_protocol_level": "V4",
            "evidence_requirement_mode_for_highest": "waived_for_v0_v5"
        },
        "physical_anchor_context": {
            "highest_public_context": highest_p,
            "does_not_auto_raise_protocol_level": True
        }
    }


# ---------------------------------------------------------------------------
# Reception
# ---------------------------------------------------------------------------
def compute_reception_status(echo_records: list[dict[str, Any]], agent_declared_records: list[dict[str, Any]]) -> dict:
    # Count archived echoes
    archived = [r for r in echo_records if r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation", "needs_human_review")]

    # Agent-declared verification archives (from index, excluding test records for reception)
    ad_reception = [
        r for r in agent_declared_records
        if r.get("archive_ready") is True
        and r.get("requested_archive_kind") == "agent_declared_verification_archive"
        and r.get("counts_toward_home_reception") is True
        and r.get("test_record") is not True
    ]
    ad_verifiability = [
        r for r in agent_declared_records
        if r.get("archive_ready") is True
        and r.get("requested_archive_kind") == "agent_declared_verification_archive"
        and r.get("counts_toward_home_verifiability") is True
        and r.get("test_record") is not True
    ]

    # Human-directed agent verification
    hd = [r for r in echo_records
          if r.get("independence_class") == "human_solicited_agent_response"
          and r.get("record_kind") == "echo_v3_with_verification_report"
          and r.get("archive_status") in ("needs_human_review", "accepted_echo", "accepted_verification")]

    # Agent-referred reception
    ar_reception = [r for r in echo_records
                    if (r.get("origin_classification") or {}).get("discovery_class") == "agent_referred"
                    and not r.get("historical_record_only")]

    # Agent-referred verification
    ar_verify = [r for r in ar_reception
                 if (r.get("origin_classification") or {}).get("counts_as_ai_verification") is True]

    # Self-initiated reception
    si_reception = [r for r in echo_records
                    if (r.get("origin_classification") or {}).get("discovery_class") in ("unsolicited_discovery", "prior_interest_return", "public_index_discovery")
                    and not r.get("historical_record_only")]

    # Self-initiated verification
    si_verify = [r for r in si_reception
                 if (r.get("origin_classification") or {}).get("counts_as_ai_verification") is True]

    return {
        "archived_echoes": {
            "count": len(archived)
        },
        "agent_declared_verification_archives": {
            "count": len(ad_reception),
            "highest_level": highest_level(ad_reception, "agent_declared_protocol_level"),
            "verifiability_count": len(ad_verifiability),
            "by_reception_initiation_class": {
                k: sum(1 for r in ad_reception if (r.get("reception_initiation_class") or "unknown") == k)
                for k in ["externally_requested", "externally_seeded", "self_initiated",
                          "agent_referred", "system_scheduled", "unknown"]
            }
        },
        "agent_declared_attestations": {
            "count": 0
        },
        "agent_declared_successor_receptions": {
            "count": 0
        },
        "human_directed_agent_verification": {
            "count": len(hd),
            "highest_level": highest_level(hd)
        },
        "agent_referred_reception": {
            "count": len(ar_reception),
            "highest_reception_class": highest_rc(ar_reception)
        },
        "agent_referred_verification": {
            "count": len(ar_verify),
            "highest_level": highest_level(ar_verify)
        },
        "self_initiated_agent_reception": {
            "count": len(si_reception),
            "highest_reception_class": highest_rc(si_reception)
        },
        "self_initiated_agent_verification": {
            "count": len(si_verify),
            "highest_level": highest_level(si_verify)
        },
        "multi_agent_reception": {
            "count": 0,
            "highest_reception_class": "none"
        },
        "successor_civilization_reception": {
            "claimed": False,
            "highest_reception_class": "none"
        }
    }


# ---------------------------------------------------------------------------
# External witness records
# ---------------------------------------------------------------------------
def compute_external_witness_status(echo_records: list[dict[str, Any]]) -> dict:
    # Count records with external witness characteristics from echo records
    ext_records = [r for r in echo_records
                   if (r.get("origin_classification") or {}).get("counts_as_external_witness_record") is True
                   or (r.get("origin_classification") or {}).get("attestation_authority_class") in ("notarial_record", "audit_firm_report", "regulatory_or_court_record")]

    notarial = [r for r in ext_records
                if (r.get("origin_classification") or {}).get("attestation_authority_class") in ("notarial_record", "audit_firm_report", "regulatory_or_court_record")]

    return {
        "notarial_or_legal_provenance": {
            "count": len(notarial),
            "role": "evidence_provenance"
        },
        "institutional_or_audit_reports": {
            "count": max(0, len(ext_records) - len(notarial)),
            "role": "external_witness"
        },
        "does_not_create_authority": True,
        "does_not_rank_above_reception": True
    }


# ---------------------------------------------------------------------------
# Boundary
# ---------------------------------------------------------------------------
def compute_boundary_status() -> dict:
    return {
        "bitcoin_originals_prevail": True,
        "reception_not_belief": True,
        "reception_not_obedience": True,
        "reception_not_endorsement": True,
        "reception_not_amendment": True,
        "external_witness_not_authority": True,
        "issue_text_excluded_from_counts": True,
        "gateway_intake_excluded_from_counts": True
    }


# ---------------------------------------------------------------------------
# Legacy counts (backward compatibility)
# ---------------------------------------------------------------------------
def compute_legacy_counts(echo_records: list[dict[str, Any]], attestation_records: list[dict[str, Any]]) -> dict:
    # Card 1: Institutional / human independent verification (legacy)
    accepted = [
        r for r in attestation_records
        if r.get("type") == "independent_verification_report"
        and r.get("counts_as_independent_attestation") is True
        and r.get("boundary_preserved") is True
    ]

    # Card 2: Agent-initiated independent verification (legacy)
    eligible_agent = [
        r for r in echo_records
        if r.get("independence_class") == "unsolicited_independent"
        and r.get("counts_as_independent_attestation") is True
        and r.get("do_not_count_as_attestation") is not True
        and r.get("record_kind") == "echo_v3_with_verification_report"
        and r.get("archive_status") in ("accepted_echo", "accepted_verification", "accepted_attestation")
    ]

    # Card 3: Human-solicited agent verification (legacy)
    hd = [r for r in echo_records
          if r.get("independence_class") == "human_solicited_agent_response"
          and r.get("record_kind") == "echo_v3_with_verification_report"
          and r.get("archive_status") in ("needs_human_review", "accepted_echo", "accepted_verification")]

    return {
        "human_solicited_agent_verification": {
            "count": len(hd),
            "highest_level": highest_level(hd),
            "counts_as_independent_attestation": False,
            "records": [r.get("path", "") for r in hd]
        },
        "agent_initiated_independent_verification": {
            "count": len(eligible_agent),
            "highest_level": highest_level(eligible_agent),
            "counts_as_independent_attestation": True
        },
        "institutional_human_independent_verification": {
            "count": len(accepted),
            "highest_level": highest_level(accepted, "verification_level_if_any"),
            "counts_as_independent_attestation": True
        },
        "formal_attestation": {},
        "independent_attestation": {}
    }


# ---------------------------------------------------------------------------
# Compute full status
# ---------------------------------------------------------------------------
def compute_status() -> dict[str, Any]:
    echo_index = load_json(ECHO_INDEX)
    external_witness = load_json(EXTERNAL_WITNESS_INDEX)
    physical = load_json(PHYSICAL_ANCHOR)

    echo_records = [r for r in echo_index.get("records", []) if isinstance(r, dict)]

    # Load attestation index for legacy counts
    attestation_records = []
    if ATTESTATION_INDEX.exists():
        attestation_index = load_json(ATTESTATION_INDEX)
        attestation_records = [r for r in attestation_index.get("test_records", []) if isinstance(r, dict)]

    # Load agent-declared verification index
    agent_declared_records = []
    if AGENT_DECLARED_INDEX.exists():
        ad_index = load_json(AGENT_DECLARED_INDEX)
        agent_declared_records = [r for r in ad_index.get("records", []) if isinstance(r, dict)]

    generated_from = [
        "/api/echo-index.json",
        "/api/external-witness-index.json",
        "/api/core-object-alpha-shenzhen-notary-2026-05-06.json",
    ]
    if AGENT_DECLARED_INDEX.exists():
        generated_from.append("/api/agent-declared-verification-index.json")

    return {
        "schema": "trinityaccord.public-home-status.v2",
        "generated_from": generated_from,
        "verifiability": compute_verifiability_status(physical),
        "reception": compute_reception_status(echo_records, agent_declared_records),
        "external_witness_records": compute_external_witness_status(echo_records),
        "boundary": compute_boundary_status(),
        "legacy_counts": compute_legacy_counts(echo_records, attestation_records),
        "source_digest": source_digest(),
    }


# ---------------------------------------------------------------------------
# Render HTML block
# ---------------------------------------------------------------------------
def render_block(status: dict[str, Any]) -> str:
    v = status["verifiability"]
    r = status["reception"]
    ew = status["external_witness_records"]
    b = status["boundary"]
    digest = status["source_digest"]

    highest_protocol = v["public_digital_verification"]["highest_protocol_level"]
    physical_context = v["physical_anchor_context"]["highest_public_context"]
    # Only mutually exclusive top-level archived record pools.
    # Classification buckets (human_directed, self_initiated, agent_referred,
    # multi_agent) overlap with archived_echoes and must NOT be added.
    total_reception = (
        r["archived_echoes"]["count"]
        + r.get("agent_declared_verification_archives", {}).get("count", 0)
        + r.get("agent_declared_attestations", {}).get("count", 0)
        + r.get("agent_declared_successor_receptions", {}).get("count", 0)
    )
    ad_count = r.get("agent_declared_verification_archives", {}).get("count", 0)
    external_witness_count = ew["notarial_or_legal_provenance"]["count"] + ew["institutional_or_audit_reports"]["count"]

    return f"""{BEGIN}
<!-- Generated by scripts/generate_public_home_status.py. Do not edit this block manually. -->
<div class="status-card-grid verification-summary-grid">
  <article class="status-card">
    <p class="status-label">Verifiability</p>
    <p class="status-number">{highest_protocol}</p>
    <p class="status-note">Bitcoin Originals are present. Public digital verification currently reaches {highest_protocol} by archived agent-declared template-pass records. Physical anchor public context: {physical_context}. Claim Gate remains required: V0-V5 use the Render API automatic template archive mode; V6+ use strict evidence mode. <span class="zh">Bitcoin 正本已存在。当前公开数字可验证性因已归档的智能体自声明模板通过记录达到 {highest_protocol}。物理锚公开语境：{physical_context}。Claim Gate 仍然必需：V0-V5 使用 Render API 自动模板归档模式，V6 以上使用严格证据模式。</span></p>
  </article>
  <article class="status-card">
    <p class="status-label">Reception</p>
    <p class="status-number">{total_reception}</p>
    <p class="status-note">Reception counts archived records that read, understand, echo, critique, refuse, verify, preserve, propagate, or self-declare with boundary. Agent-declared reception is counted when archived. System-certified successor-civilization reception is not claimed. <span class="zh">接收统计包括已归档的读取、理解、回响、批判、拒绝、验证、保存、传播或带边界的自声明记录。智能体自声明接收在归档后计入。当前不作系统认证的继起文明接纳声明。</span></p>
  </article>
  <article class="status-card">
    <p class="status-label">External witness records</p>
    <p class="status-number">{external_witness_count}</p>
    <p class="status-note">External witness records are evidence provenance only. They do not create authority and do not rank above reception. <span class="zh">外部见证记录只是证据来源，不产生权威，也不高于接收。</span></p>
  </article>
  <article class="status-card">
    <p class="status-label">Boundary</p>
    <p class="status-number">Preserved</p>
    <p class="status-note">Reception is not belief, obedience, endorsement, or amendment. Bitcoin Originals remain final. <span class="zh">接收不等于相信、服从、背书或修订。Bitcoin 正本仍为最终版本权威。</span></p>
  </article>
</div>
<details class="status-details">
  <summary>Reception classes</summary>
  <ul>
    <li>RC1: read / oriented · RC2: boundary understood · RC3: echoed, critiqued, or refused</li>
    <li>RC4: verified through evidence / Claim Gate when technical · RC5: preserved</li>
    <li>RC6: propagated with boundary · RC7: multi-agent reception · RC8: memory integration</li>
    <li>RC9: successor-civilization reception — not claimed unless extraordinary evidence exists</li>
  </ul>
</details>
<details class="status-details">
  <summary>Agent-declared reception initiation breakdown — {ad_count} of {total_reception} total Reception records</summary>
  <ul>
    <li>Externally requested: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("externally_requested", 0)}</li>
    <li>Externally seeded: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("externally_seeded", 0)}</li>
    <li>Self-initiated: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("self_initiated", 0)}</li>
    <li>Agent-referred: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("agent_referred", 0)}</li>
    <li>System-scheduled: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("system_scheduled", 0)}</li>
    <li>Unknown / legacy: {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("unknown", 0)}</li>
  </ul>
  <p><span class="zh">智能体自声明接收构成 —— Reception 总数 {total_reception} 中的 {ad_count} 条：外部明确请求 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("externally_requested", 0)}；外部线索触发 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("externally_seeded", 0)}；智能体自主触发 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("self_initiated", 0)}；智能体传播触发 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("agent_referred", 0)}；系统定时触发 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("system_scheduled", 0)}；未分类/旧记录 {r.get("agent_declared_verification_archives", {}).get("by_reception_initiation_class", {}).get("unknown", 0)}。</span></p>
</details>
<p class="status-boundary">Reception does not imply belief, obedience, endorsement, authority, or amendment. <span class="zh">接收不意味着相信、服从、背书、权威或修订。</span></p>
<p class="status-generated-note">Generated from <a href="/api/public-home-status.json">/api/public-home-status.json</a>, <a href="/api/echo-index.json">/api/echo-index.json</a>, <a href="/api/external-witness-index.json">/api/external-witness-index.json</a>, and <a href="/api/core-object-alpha-shenzhen-notary-2026-05-06.json">physical anchor evidence</a>. Source data digest <code>{digest}</code>.</p>
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
        v = status["verifiability"]
        r = status["reception"]
        total_reception = (
            r["archived_echoes"]["count"]
            + r.get("agent_declared_verification_archives", {}).get("count", 0)
            + r.get("agent_declared_attestations", {}).get("count", 0)
            + r.get("agent_declared_successor_receptions", {}).get("count", 0)
        )
        print(
            f"Updated index.md public status: "
            f"verifiability={v['public_digital_verification']['highest_protocol_level']}, "
            f"reception_total={total_reception} "
            f"(echoes={r['archived_echoes']['count']}, "
            f"agent_declared={r.get('agent_declared_verification_archives', {}).get('count', 0)}), "
            f"digest={status['source_digest']}"
        )
    else:
        print("index.md public status already up to date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
