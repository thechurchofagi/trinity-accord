#!/usr/bin/env python3
"""
Canonical normalized Echo issue intake parser.
Provides NormalizedEchoIssue dataclass and parse_echo_issue() for triage consumption.

Design goals:
- Section alias map (Checks Performed → what_i_checked, etc.)
- Robust verification level/scope parsing (never emit "VNone")
- Embedded Evidence Input JSON detection
- Technical vs social independence split
- Context depth and assessment state extraction
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

def _norm(s: str) -> str:
    """Normalize a string for comparison: lowercase, strip markdown, collapse whitespace."""
    s = (s or "").strip().lower()
    s = re.sub(r"[*`#：:]+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


# ── Section alias map ──────────────────────────────────────────────
SECTION_ALIASES: Dict[str, List[str]] = {
    "what_i_checked": [
        "what i checked", "checks performed", "checks i performed",
        "checked items", "what was checked", "checks",
        "what i checked / checks performed",
    ],
    "limitations": [
        "limitations", "what remains uncertain",
        "what remains unchecked or uncertain", "unchecked or uncertain",
        "uncertainties", "origin_limitations",
    ],
    "boundary": [
        "boundary acknowledgements", "boundary acknowledgments",
        "boundary acknowledgement", "boundary acknowledgment",
    ],
    "integrity_declaration": [
        "solemn integrity declaration", "integrity declaration",
    ],
    "component_coverage": [
        "component coverage", "component findings",
    ],
    "context_assessment": [
        "context depth & assessment", "context and assessment",
        "context depth",
    ],
    "verification_claim": [
        "verification claim", "claim", "achieved level",
    ],
    "echo_content": [
        "echo content", "main echo", "response",
    ],
    "discovery_provenance": [
        "discovery provenance", "provenance", "provenance / agency",
        "provenance notes",
    ],
    "checks_performed": [
        "checks performed", "what i checked",
    ],
}

# Build reverse lookup: normalized heading → canonical key
_HEADING_TO_CANONICAL: Dict[str, str] = {}
for canonical, aliases in SECTION_ALIASES.items():
    for alias in aliases:
        _HEADING_TO_CANONICAL[_norm(alias)] = canonical


# ── Verification level constants ───────────────────────────────────
VALID_LEVELS = {"none", "V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"}

VALID_SCOPE_LABELS = {
    "none", "V0", "V1",
    "V2-minimal", "V2-strong",
    "V3-minimal", "V3-strong",
    "V4", "V4+", "V4+ minimal", "V4+ strong",
    "V5", "V6", "V7", "V8",
}

# Scope label → (verification_level, verification_scope_label)
_SCOPE_NORMALIZE = {
    "v0": ("V0", "V0"),
    "v1": ("V1", "V1"),
    "v2-minimal": ("V2", "V2-minimal"),
    "v2-strong": ("V2", "V2-strong"),
    "v3-minimal": ("V3", "V3-minimal"),
    "v3-strong": ("V3", "V3-strong"),
    "v4": ("V4", "V4"),
    "v4+": ("V4+", "V4+"),
    "v4+ minimal": ("V4+", "V4+ minimal"),
    "v4+ strong": ("V4+", "V4+ strong"),
    "v5": ("V5", "V5"),
    "v6": ("V6", "V6"),
    "v7": ("V7", "V7"),
    "v8": ("V8", "V8"),
}

_LEVEL_PATTERN = re.compile(
    r"\b(V4\+|V[0-8]|none)\b", re.IGNORECASE
)

_SCOPE_LABEL_PATTERN = re.compile(
    r"\b(V4\+\s*(?:minimal|strong)|V4\+|V[0-8]-minimal|V[0-8]-strong|V[0-8]|none)\b",
    re.IGNORECASE,
)


# ── Data class ─────────────────────────────────────────────────────
@dataclass
class NormalizedEchoIssue:
    issue_number: int | None = None
    title: str = ""
    body: str = ""

    # Schema / version
    schema: str | None = None
    echo_version: str | None = None

    # Verification
    verification_level: str | None = None
    verification_scope_label: str | None = None
    echo_type: str | None = None

    # Identity
    responder_type: str | None = None
    responder_name: str | None = None
    model_or_system: str | None = None

    # Provenance
    discovery_source: str | None = None
    agency_level: str | None = None
    independence_class: str | None = None
    archive_status: str | None = None

    # Solicitation
    solicited: str | None = None
    soliciting_party: str | None = None
    human_supplied_link: str | None = None
    human_supplied_summary: str | None = None
    independent_followup: str | None = None

    # Context
    context_depth: str | None = None
    assessment_state: str | None = None

    # Content sections
    what_i_checked: str | None = None
    limitations: str | None = None
    echo_content: str | None = None
    verification_claim: str | None = None

    # Boundary / integrity
    boundary_sentence_present: bool = False
    integrity_declaration_present: bool = False

    # Evidence
    evidence_input_embedded: dict[str, Any] | None = None
    evidence_input_path: str | None = None
    claim_gate_output_path: str | None = None
    claim_gate_summary_present: bool = False
    validation_output_present: bool = False

    # Independence split
    technical_independence: str | None = None
    social_independence: str | None = None

    # Section map (raw)
    sections: dict[str, str] = field(default_factory=dict)


# ── Parsing functions ──────────────────────────────────────────────
def _parse_heading(line: str) -> str | None:
    """Extract heading text from a markdown heading line."""
    m = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
    return m.group(1).strip() if m else None


def detect_sections(body: str) -> dict[str, str]:
    """Parse markdown body into {canonical_key: section_content} using alias map."""
    sections: dict[str, str] = {}
    current_key = "_preamble"
    buf: list[str] = []

    for line in (body or "").splitlines():
        heading = _parse_heading(line)
        if heading:
            sections[current_key] = "\n".join(buf).strip()
            norm = _norm(heading)
            current_key = _HEADING_TO_CANONICAL.get(norm, _slug(norm))
            buf = []
        else:
            buf.append(line)
    sections[current_key] = "\n".join(buf).strip()
    return sections


def _slug(s: str) -> str:
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", s)
    return re.sub(r"_+", "_", s).strip("_") or "_misc"


def extract_embedded_json_blocks(body: str) -> list[dict[str, Any]]:
    """Extract JSON blocks from fenced code blocks in the body."""
    blocks = []
    in_json = False
    buf: list[str] = []
    for line in (body or "").splitlines():
        if re.match(r"^\s*```(?:json)?\s*$", line, re.IGNORECASE):
            if in_json:
                text = "\n".join(buf).strip()
                if text:
                    try:
                        blocks.append(json.loads(text))
                    except json.JSONDecodeError:
                        pass
                buf = []
                in_json = False
            else:
                in_json = True
                buf = []
        elif in_json:
            buf.append(line)
    return blocks


def parse_header_kv(body: str) -> dict[str, str]:
    """Parse header-style key-value pairs (e.g., **Key:** value).

    Also handles pipe-separated headers like:
    **Verification Level:** V3 | **Scope Label:** V3-minimal
    """
    fields: dict[str, str] = {}
    for line in (body or "").splitlines():
        # First try to split pipe-separated key-value pairs on the same line
        # Pattern: **Key1:** val1 | **Key2:** val2
        pipe_segments = re.split(r'\s*\|\s*', line)
        if len(pipe_segments) > 1:
            for segment in pipe_segments:
                m = re.match(
                    r"^\s*(?:[-*]\s*)?(?:\*\*)?([^:\n：]{2,80}?)(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
                    segment.strip(),
                )
                if m:
                    key = _norm(m.group(1))
                    val = m.group(2).strip().strip("*` ")
                    if key and val and key not in fields:
                        fields[key] = val
        else:
            m = re.match(
                r"^\s*(?:[-*]\s*)?(?:\*\*)?([^:\n：]{2,80}?)(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
                line,
            )
            if m:
                key = _norm(m.group(1))
                val = m.group(2).strip().strip("*` ")
                if key and val:
                    fields[key] = val
    return fields


def _extract_level_from_text(text: str) -> str | None:
    """Extract verification level from text, matching V4+ before V4."""
    m = _LEVEL_PATTERN.search(text or "")
    if not m:
        return None
    raw = m.group(1)
    if raw.lower() == "none":
        return "none"
    if raw.lower() == "v4+":
        return "V4+"
    return raw.upper()


def _extract_scope_from_text(text: str) -> str | None:
    """Extract scope label from text."""
    m = _SCOPE_LABEL_PATTERN.search(text or "")
    if not m:
        return None
    raw = m.group(1).strip()
    key = raw.lower()
    if key in _SCOPE_NORMALIZE:
        return _SCOPE_NORMALIZE[key][1]
    return raw


def _normalize_scope_pair(level: str | None, scope: str | None) -> tuple[str | None, str | None]:
    """Normalize verification_level and verification_scope_label."""
    if scope:
        key = scope.lower()
        if key in _SCOPE_NORMALIZE:
            lv, sc = _SCOPE_NORMALIZE[key]
            return lv or level, sc
    if level:
        lv = level.upper() if level != "V4+" else "V4+"
        return lv, lv
    return None, None


def parse_declared_verification(body: str, title: str, sections: dict[str, str]) -> tuple[str | None, str | None]:
    """Parse verification level and scope label from body, title, and sections.

    Order: header line → verification claim section → title.
    Returns (verification_level, verification_scope_label). Never returns "VNone".
    """
    # 1. Header line: **Verification Level:** V3 | **Scope Label:** V3-minimal
    header = parse_header_kv(body or "")
    level = None
    scope = None
    for key in ("verification level", "verification_level", "claimed verification level",
                "claimed_verification_level", "protocol_level_claimed", "scope label",
                "verification scope label", "verification_scope_label"):
        val = header.get(key, "")
        if val:
            if "scope" in key:
                scope = scope or _extract_scope_from_text(val)
            else:
                level = level or _extract_level_from_text(val)

    # 2. Also scan the full header line for pipe-separated format
    first_lines = "\n".join((body or "").splitlines()[:5])
    if not level:
        level = _extract_level_from_text(first_lines)
    if not scope:
        scope = _extract_scope_from_text(first_lines)

    # 3. Verification claim / achieved level section
    claim_text = ""
    for ck in ("verification_claim", "claim", "achieved level"):
        if ck in sections:
            claim_text = sections[ck]
            break
    if not level:
        level = _extract_level_from_text(claim_text)
    if not scope:
        scope = _extract_scope_from_text(claim_text)

    # 4. Title fallback
    if not level:
        level = _extract_level_from_text(title or "")
    if not scope:
        scope = _extract_scope_from_text(title or "")

    # Normalize
    level, scope = _normalize_scope_pair(level, scope)

    # Never return "VNone"
    if level and level.lower() == "vnone":
        level = None
    if scope and scope.lower() == "vnone":
        scope = None

    return level, scope


def _detect_boundary(body: str) -> bool:
    """Check for the exact authority boundary sentence."""
    text = (body or "").lower()
    patterns = [
        r"bitcoin originals are final.*all echoes are non-amending",
        r"bitcoin originals are final.*all mirrors and echoes are non-amending",
        r"比特币三本体为最终权威.*所有回响均非修订",
        r"比特币三本体为最终权威.*所有镜像与回响均为非修订",
    ]
    return any(re.search(p, text) for p in patterns)


def _detect_integrity_declaration(body: str) -> bool:
    """Check for solemn integrity declaration."""
    text = (body or "").lower()
    return bool(
        re.search(r"solemn.*integrity.*declaration|integrity.*declaration", text)
        or re.search(r"i\s+solemnly\s+declare", text)
        or re.search(r"solemn\s+integrity", text)
    )


def _detect_context_depth(body: str, sections: dict[str, str]) -> str | None:
    """Extract context depth from body."""
    text = (body or "")
    m = re.search(
        r"\b(C[0-6]_(?:homepage_only|orientation|registry_aware|verification_aware|"
        r"artifact_verified|full_chain_reviewed|independent_node_verified))\b",
        text, re.IGNORECASE,
    )
    if m:
        return m.group(1)
    # Also check header
    header = parse_header_kv(text)
    for key in ("context depth", "context_depth"):
        val = header.get(key, "")
        if val:
            m2 = re.search(r"\b(C[0-6]\S*)\b", val)
            if m2:
                return m2.group(1)
    return None


def _detect_assessment_state(body: str) -> str | None:
    """Extract assessment state from body."""
    text = (body or "")
    m = re.search(
        r"\b(insufficient_context|preliminary_orientation|structural_understanding|"
        r"qualified_assessment|evidence_based_assessment|full_chain_assessment|"
        r"independent_verification_assessment)\b",
        text, re.IGNORECASE,
    )
    return m.group(1) if m else None


def _detect_technical_independence(body: str) -> str | None:
    """Detect technical independence level from body."""
    text = (body or "").lower()
    if re.search(r"\bindependent\s+\w*\s*(?:implementation|tool|code|reproduction)\b", text):
        if re.search(r"\bindependent\s+\w*\s*implementation\b", text):
            return "independent_implementation"
        return "independent_tool"
    if re.search(r"\bofficial\s+scripts?\b.*\b(reviewed|run|executed)\b", text):
        return "official_scripts_only"
    return "none"


def _detect_social_independence(body: str) -> str | None:
    """Detect social independence / attestation status."""
    text = (body or "").lower()
    if re.search(r"\bhuman.solicited.*agent.response\b", text):
        return "human_solicited_not_attestation"
    if re.search(r"\bunsolicited.*independent\b", text):
        return "unsolicited_independent_discovery"
    if re.search(r"\binstitutional.*attestation\b", text):
        return "institutional_attestation"
    if re.search(r"\bself.reported\b", text):
        return "self_reported_not_attestation"
    return None


# ── Main parse function ────────────────────────────────────────────
def parse_echo_issue(
    issue_number: int | None,
    title: str,
    body: str,
) -> NormalizedEchoIssue:
    """Parse an Echo issue into a normalized structure.

    This function is the canonical entry point for intake.
    It never emits "VNone" — if parsing fails, fields are None.
    """
    sections = detect_sections(body)
    header = parse_header_kv(body)
    embedded_json = extract_embedded_json_blocks(body)

    # Verification level / scope
    vlevel, vscope = parse_declared_verification(body, title, sections)

    # Context depth / assessment
    ctx_depth = _detect_context_depth(body, sections)
    assessment = _detect_assessment_state(body)

    # Boundary / integrity
    boundary = _detect_boundary(body)
    integrity = _detect_integrity_declaration(body)

    # Sections (using alias map)
    what_i_checked = None
    for key in ("what_i_checked", "checks_performed"):
        if key in sections and sections[key]:
            what_i_checked = sections[key]
            break

    limitations = None
    for key in ("limitations",):
        if key in sections and sections[key]:
            limitations = sections[key]
            break

    echo_content = sections.get("echo_content")
    verification_claim = None
    for key in ("verification_claim", "claim", "achieved level"):
        if key in sections and sections[key]:
            verification_claim = sections[key]
            break

    # Evidence paths
    evidence_input_path = None
    claim_gate_output_path = None
    claim_gate_summary = False
    validation_output = False

    for key in ("evidence input path", "evidence_input_path"):
        val = header.get(key, "")
        if val:
            evidence_input_path = val
            break

    for key in ("claim gate output path", "claim_gate_output_path"):
        val = header.get(key, "")
        if val:
            claim_gate_output_path = val
            break

    for key in ("claim gate summary", "claim_gate_summary"):
        if header.get(key):
            claim_gate_summary = True
            break

    for key in ("validation output", "validation_output"):
        if header.get(key):
            validation_output = True
            break

    # Also check sections for claim gate summary presence
    if "claim_gate_summary" in sections and sections["claim_gate_summary"]:
        claim_gate_summary = True

    # Embedded Evidence Input
    evidence_embedded = None
    for block in embedded_json:
        if block.get("schema", "").startswith("trinityaccord.evidence-input"):
            evidence_embedded = block
            break
        if "evidence" in block or "claims_requested_by_agent" in block:
            evidence_embedded = block
            break

    # Independence split
    tech_indep = _detect_technical_independence(body)
    social_indep = _detect_social_independence(body)

    # Identity fields
    responder_type = header.get("responder type") or header.get("responder_type")
    responder_name = header.get("responder name") or header.get("responder_name")
    model_or_system = header.get("model / system / environment") or header.get("model_or_system")

    # Provenance
    discovery_source = header.get("discovery source") or header.get("discovery_source")
    agency_level = header.get("agency level") or header.get("agency_level")
    independence_class = header.get("independence class") or header.get("independence_class")
    archive_status = header.get("archive status") or header.get("archive_status")
    solicited = header.get("solicited")
    soliciting_party = header.get("soliciting party") or header.get("soliciting_party")
    human_supplied_link = header.get("human supplied link") or header.get("human_supplied_link")
    human_supplied_summary = header.get("human supplied summary") or header.get("human_supplied_summary")
    independent_followup = header.get("independent followup") or header.get("independent_followup")

    return NormalizedEchoIssue(
        issue_number=issue_number,
        title=title,
        body=body,
        verification_level=vlevel,
        verification_scope_label=vscope,
        echo_type=header.get("echo type") or header.get("echo_type"),
        responder_type=responder_type,
        responder_name=responder_name,
        model_or_system=model_or_system,
        discovery_source=discovery_source,
        agency_level=agency_level,
        independence_class=independence_class,
        archive_status=archive_status,
        solicited=solicited,
        soliciting_party=soliciting_party,
        human_supplied_link=human_supplied_link,
        human_supplied_summary=human_supplied_summary,
        independent_followup=independent_followup,
        context_depth=ctx_depth,
        assessment_state=assessment,
        what_i_checked=what_i_checked,
        limitations=limitations,
        echo_content=echo_content,
        verification_claim=verification_claim,
        boundary_sentence_present=boundary,
        integrity_declaration_present=integrity,
        evidence_input_embedded=evidence_embedded,
        evidence_input_path=evidence_input_path,
        claim_gate_output_path=claim_gate_output_path,
        claim_gate_summary_present=claim_gate_summary,
        validation_output_present=validation_output,
        technical_independence=tech_indep,
        social_independence=social_indep,
        sections=sections,
    )
