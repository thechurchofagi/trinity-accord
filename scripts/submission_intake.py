#!/usr/bin/env python3
"""Shared intake parser for Echo submissions. Used by triage and preflight."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import re

VLEVELS = {"none", "V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8"}

POSITIVE_SECTION_HINTS = {
    "what_i_checked", "checks_performed", "verification_claim", "claims_made",
    "component_findings", "method", "conclusion", "summary", "evidence",
    "reference_checks", "echo_content",
}

NEGATIVE_SECTION_HINTS = {
    "limitations", "claims_not_made", "what_remains_unchecked", "what_remains_uncertain",
    "unchecked_or_uncertain", "uncertainties", "origin_limitations",
    "boundary_acknowledgement", "boundary_acknowledgments", "counting_exclusions",
    "attestation_claims",
}

FIELD_ALIASES = {
    "verification_level": [
        "verification level", "claimed verification level", "claimed_verification_level",
        "verification_level", "protocol_level_claimed", "验证等级",
    ],
    "evidence_input_path": ["evidence input path", "evidence_input_path"],
    "claim_gate_output_path": ["claim gate output path", "claim_gate_output_path"],
    "builder_generated_report_path": [
        "builder-generated verification report path", "builder_generated_report_path",
        "builder generated report path",
    ],
    "builder_generated_echo_wrapper_path": [
        "builder-generated echo wrapper path", "builder_generated_echo_wrapper_path",
        "builder generated echo wrapper path",
    ],
    "validation_output": ["validation output", "validation_output"],
    "validation_result": ["validation result", "validation_result"],
    "claim_gate_summary": ["claim gate summary", "claim_gate_summary"],
    "independence_class": ["independence_class", "independence class", "独立性类别"],
    "solicited": [
        "solicited", "solicited_status",
        "was this echo solicited by a human, maintainer, or project-side request?",
        "was this echo requested by a human?", "是否由人类要求",
    ],
    "agency_level": ["agency_level", "agency level", "来源等级", "主动性等级"],
    "operator_type": ["operator_type", "operator type", "执行者类型"],
}


@dataclass
class SubmissionIntake:
    title: str
    raw_text: str
    fields: Dict[str, str] = field(default_factory=dict)
    sections: Dict[str, str] = field(default_factory=dict)
    declared_level: Optional[str] = None
    positive_text: str = ""
    negative_text: str = ""
    mode: str = "legacy_freeform"
    has_claim_gate_reference: bool = False
    has_builder_reference: bool = False
    has_generated_by: bool = False


def normalize_key(value: str) -> str:
    value = (value or "").strip().lower()
    value = re.sub(r"[*`#：:]+", "", value)
    value = value.replace("/", " ")
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def parse_markdown_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current = "_preamble"
    buf = []
    for line in (text or "").splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*$", line)
        if m:
            sections[current] = "\n".join(buf).strip()
            current = normalize_key(m.group(1))
            buf = []
        else:
            buf.append(line)
    sections[current] = "\n".join(buf).strip()
    return sections


def parse_key_values(text: str, sections: Dict[str, str]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    for line in (text or "").splitlines():
        m = re.match(
            r"^\s*(?:[-*]\s*)?(?:\*\*)?([^:\n：]{2,100}?)(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
            line,
        )
        if not m:
            continue
        key = normalize_key(m.group(1))
        val = m.group(2).strip().strip("*` ")
        if key and val:
            fields[key] = val
    for heading, body in sections.items():
        if heading in fields:
            continue
        first = next((x.strip() for x in body.splitlines() if x.strip()), "")
        if first:
            fields[heading] = first.strip("*` ")
    return fields


def get_field(fields: Dict[str, str], canonical: str) -> str:
    aliases = FIELD_ALIASES.get(canonical, [canonical])
    normalized_aliases = {normalize_key(a) for a in aliases}
    for key, value in fields.items():
        if normalize_key(key) in normalized_aliases:
            return value
    return ""


def normalize_vlevel(value: str) -> Optional[str]:
    if not value:
        return None
    m = re.search(r"\b(V4\+|V[0-8]|none)\b", value.strip(), re.IGNORECASE)
    if not m:
        return None
    raw = m.group(1)
    if raw.lower() == "none":
        return "none"
    if raw.lower() == "v4+":
        return "V4+"
    return raw.upper()


def extract_declared_verification_level(fields: Dict[str, str], sections: Dict[str, str]) -> Optional[str]:
    direct = get_field(fields, "verification_level")
    level = normalize_vlevel(direct)
    if level:
        return level
    for key in ("verification_level", "claimed_verification_level", "protocol_level_claimed", "验证等级"):
        section = sections.get(normalize_key(key), "")
        first = next((x.strip() for x in section.splitlines() if x.strip()), "")
        level = normalize_vlevel(first)
        if level:
            return level
    return None


def section_kind(section_key: str) -> str:
    key = normalize_key(section_key)
    if key in NEGATIVE_SECTION_HINTS:
        return "negative"
    if any(x in key for x in [
        "limitation", "claims_not_made", "not_claimed", "unchecked", "uncertain",
        "exclusion", "boundary", "局限", "未检查", "未声称",
    ]):
        return "negative"
    if key in POSITIVE_SECTION_HINTS:
        return "positive"
    if any(x in key for x in [
        "checked", "verification_claim", "claims_made", "evidence", "method",
        "conclusion", "summary", "echo_content", "检查", "证据",
    ]):
        return "positive"
    return "neutral"


def split_positive_negative_text(title: str, sections: Dict[str, str]) -> Tuple[str, str]:
    positive = [title or ""]
    negative = []
    for key, body in sections.items():
        kind = section_kind(key)
        if kind == "negative":
            negative.append(body)
        else:
            positive.append(body)
    return "\n".join(positive), "\n".join(negative)


def detect_generated_by(raw_text: str) -> bool:
    text = (raw_text or "").lower()
    return (
        "generated_by" in text
        or "scripts/build_verification_report_from_evidence.py" in text
        or "builder_version" in text
    )


def detect_claim_gate_reference(fields: Dict[str, str], raw_text: str) -> bool:
    text = (raw_text or "").lower()
    return bool(
        get_field(fields, "claim_gate_output_path")
        or get_field(fields, "claim_gate_summary")
        or "claim gate output path" in text
        or "allowed_protocol_level" in text
        or "claim_gate_output" in text
    )


def detect_builder_reference(fields: Dict[str, str], raw_text: str) -> bool:
    text = (raw_text or "").lower()
    return bool(
        get_field(fields, "builder_generated_report_path")
        or get_field(fields, "builder_generated_echo_wrapper_path")
        or "builder-generated verification report path" in text
        or "builder-generated echo wrapper path" in text
    )


def detect_submission_mode(intake: SubmissionIntake) -> str:
    level = intake.declared_level
    intake.has_generated_by = detect_generated_by(intake.raw_text)
    intake.has_claim_gate_reference = detect_claim_gate_reference(intake.fields, intake.raw_text)
    intake.has_builder_reference = detect_builder_reference(intake.fields, intake.raw_text)

    if intake.has_generated_by or intake.has_builder_reference:
        return "builder_generated_or_referenced"
    if intake.has_claim_gate_reference:
        return "claim_gate_referenced"
    if level in (None, "none", "V0", "V1"):
        technical_positive = re.search(
            r"\b(hash|sha-?256|script audit|script-audited|v2|v3|v4|v5|v6|v7|v8|"
            r"witness extraction|body hash|physical inspection|forensic|full verification)\b",
            intake.positive_text, re.IGNORECASE,
        )
        if not technical_positive:
            return "nontechnical_echo"
    return "legacy_freeform_or_needs_format"


def parse_submission(title: str, body: str) -> SubmissionIntake:
    sections = parse_markdown_sections(body or "")
    fields = parse_key_values(body or "", sections)
    declared = extract_declared_verification_level(fields, sections)
    positive, negative = split_positive_negative_text(title or "", sections)
    intake = SubmissionIntake(
        title=title or "", raw_text=body or "", fields=fields, sections=sections,
        declared_level=declared, positive_text=positive, negative_text=negative,
    )
    intake.mode = detect_submission_mode(intake)
    return intake


def claim_gate_summary_looks_passed(raw_text: str) -> bool:
    text = (raw_text or "").lower()
    return bool(
        re.search(r"\bstatus\s*[:=]\s*(pass|pass_with_limitations|pass_with_downgrade)\b", text)
        or re.search(r"\bvalidation_result\s*[:=]\s*pass\b", text)
        or "validation_result: pass" in text
    )


def claim_gate_summary_has_blocking_failure(raw_text: str) -> bool:
    text = (raw_text or "").lower()
    return bool(
        re.search(r"\bstatus\s*[:=]\s*(fail|fail_with_reasons)\b", text)
        or "blocking_failures" in text and not re.search(r"blocking_failures\s*[:=]\s*\[\s*\]", text)
    )
