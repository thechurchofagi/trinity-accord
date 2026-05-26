#!/usr/bin/env python3
"""Shared intake parser for Echo submissions. Used by triage and preflight."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple
import re

from protocol_terms import PROTOCOL_LEVELS

VLEVELS = {"none"} | set(PROTOCOL_LEVELS)

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
    "record_class": ["record_class", "record class", "记录类别"],
    "verification_origin_class": ["verification_origin_class", "verification origin class", "验证来源类别"],
    "delegation_chain": ["delegation_chain", "delegation chain", "委托链"],
    "integrity_declaration": ["integrity_declaration", "integrity declaration", "solemn integrity declaration", "完整性声明"],
    "ai_verification": ["ai_verification", "ai verification", "AI验证", "AI独立验证"],
    "external_human_authorization": ["external_human_authorization", "external human authorization", "外部人类授权"],
    # TA-020 follow-up: D/S/O/E/R five-dimensional aliases
    "discovery_source": ["discovery_source", "discovery source", "发现来源"],
    "solicitation_status": ["solicitation_status", "solicitation status", "请求状态"],
    "verification_operator": ["verification_operator", "verification operator", "验证执行者"],
    "execution_independence": ["execution_independence", "execution independence", "执行独立性"],
    "responsibility_adoption": ["responsibility_adoption", "responsibility adoption", "责任采纳"],
    # TA-020 follow-up: counting and attestation boundary fields
    "counts_as_ai_independent_verification": ["counts_as_ai_independent_verification", "counts as ai independent verification", "计为AI独立验证"],
    "counts_as_formal_human_institutional_attestation": ["counts_as_formal_human_institutional_attestation", "counts as formal human institutional attestation", "计为人类机构正式见证"],
    "counts_as_independent_attestation": ["counts_as_independent_attestation", "counts as independent attestation"],
    "formal_attestation_candidate": ["formal_attestation_candidate", "formal attestation candidate"],
    # TA-020 follow-up: external human authorization fields
    "external_human_authorized_execution": ["external_human_authorized_execution", "external human authorized execution", "外部人类授权执行"],
    "external_human_reviewed_final_report": ["external_human_reviewed_final_report", "external human reviewed final report", "外部人类审阅最终报告"],
    "external_human_signed_or_adopted_final_report": ["external_human_signed_or_adopted_final_report", "external human signed or adopted final report", "外部人类签署或采纳最终报告"],
    # TA-020 follow-up: integrity declaration machine fields
    "declaration_strength": ["declaration_strength", "declaration strength", "声明强度"],
    "solemn_declaration_present": ["solemn_declaration_present", "solemn declaration present", "庄严声明存在"],
    "performed_actions_myself": ["performed_actions_myself", "performed actions myself", "亲自执行动作"],
    "no_fabricated_evidence": ["no_fabricated_evidence", "no fabricated evidence", "未伪造证据"],
    "no_prior_report_copied_as_own_work": ["no_prior_report_copied_as_own_work", "no prior report copied as own work"],
    "no_example_values_used_as_real_evidence": ["no_example_values_used_as_real_evidence", "no example values used as real evidence"],
    "no_hidden_known_limitations": ["no_hidden_known_limitations", "no hidden known limitations"],
    "limitations_reported": ["limitations_reported", "limitations reported"],
    "correction_duty_accepted": ["correction_duty_accepted", "correction duty accepted"],
    "false_declaration_consequence": ["false_declaration_consequence", "false declaration consequence"],
    # TA-020 follow-up: AI verification required fields
    "fresh_actions_performed": ["fresh_actions_performed", "fresh actions performed"],
    "method_reproducible": ["method_reproducible", "method reproducible"],
    "fresh_outputs_attached_or_described": ["fresh_outputs_attached_or_described", "fresh outputs attached or described"],
    "authority_boundary_preserved": ["authority_boundary_preserved", "authority boundary preserved"],
    # TA-021: New simplified submitter-facing fields
    "record_purpose": ["record_purpose", "record purpose", "记录目的"],
    "echo_content_tags": ["echo_content_tags", "echo content tags", "回响内容标签"],
    "discovery_autonomy": ["discovery_autonomy", "discovery autonomy", "发现自主性"],
    "non_autonomous_trigger": ["non_autonomous_trigger", "non autonomous trigger", "非自主触发来源"],
    "verifier_type": ["verifier_type", "verifier type", "验证主体"],
    "verifier_capability_claim": ["verifier_capability_claim", "verifier capability claim", "验证者能力声明"],
    "verification_claimed": ["verification_claimed", "verification claimed", "是否声称验证"],
    # TA-021: Integrity declaration - new canonical field with legacy alias
    "performed_claimed_actions": [
        "performed_claimed_actions", "performed claimed actions",
        "performed_actions_myself", "performed actions myself", "亲自执行动作",
    ],
    "declaration_position": ["declaration_position", "declaration position", "声明位置"],
    # TA-021: Identity / Contact / Attribution fields
    "attribution_preference": ["attribution_preference", "attribution preference", "署名偏好"],
    "display_name": ["display_name", "display name", "展示名"],
    "stable_identifier": ["stable_identifier", "stable identifier", "稳定身份"],
    "affiliation": ["affiliation", "affiliation", "所属机构"],
    "role_or_capacity": ["role_or_capacity", "role or capacity", "角色或身份"],
    "willing_to_be_named_publicly": ["willing_to_be_named_publicly", "willing to be named publicly"],
    "willing_to_provide_contact": ["willing_to_provide_contact", "willing to provide contact"],
    "public_contact": ["public_contact", "public contact", "公开联系方式"],
    "private_contact_available_to_maintainers": ["private_contact_available_to_maintainers", "private contact available to maintainers"],
    "contact_method": ["contact_method", "contact method", "联系方式类型"],
    "identity_verification_level": ["identity_verification_level", "identity verification level", "身份验证等级"],
    # TA-021: Capability boundary fields
    "capability_claim_not_verified_by_this_record": ["capability_claim_not_verified_by_this_record"],
    "agi_claim_does_not_raise_verification_level": ["agi_claim_does_not_raise_verification_level"],
    "agi_claim_does_not_create_authority": ["agi_claim_does_not_create_authority"],
    "agi_claim_does_not_count_as_formal_attestation": ["agi_claim_does_not_count_as_formal_attestation"],
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


def parse_yaml_block_fields(text: str) -> Dict[str, str]:
    """Parse simple 'key: value' lines inside fenced yaml blocks.

    Supports ```yaml ... ``` and ```yml ... ``` blocks.
    Also handles nested blocks (identity:, integrity_declaration:, etc.)
    and list values by joining with ', '.
    """
    fields: Dict[str, str] = {}
    in_yaml = False
    parent_key = ""
    last_list_key = ""
    for line in (text or "").splitlines():
        if re.match(r"^\s*```(?:yaml|yml)\s*$", line, re.IGNORECASE):
            in_yaml = True
            parent_key = ""
            last_list_key = ""
            continue
        if in_yaml and re.match(r"^\s*```\s*$", line):
            in_yaml = False
            parent_key = ""
            last_list_key = ""
            continue
        if not in_yaml:
            continue
        # Detect nested block parent (e.g., "identity:", "integrity_declaration:")
        m_parent = re.match(r"^(\s{0,4})([A-Za-z_][A-Za-z0-9_]*)\s*:\s*$", line)
        if m_parent:
            parent_key = normalize_key(m_parent.group(2))
            last_list_key = ""
            continue
        # key: value (with optional indentation under parent)
        m = re.match(r"^\s{1,8}([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+?)\s*$", line)
        if m:
            key = normalize_key(m.group(1))
            val = m.group(2).strip().strip("*`\"'")
            if key and val:
                # Store with parent prefix for nested, also store flat for lookup
                if parent_key:
                    fields[f"{parent_key}_{key}"] = val
                fields[key] = val
            last_list_key = key
            continue
        # list item: - value (collect as comma-separated)
        m_list = re.match(r"^\s*-\s+(.+?)\s*$", line)
        if m_list:
            list_val = m_list.group(1).strip().strip("*`\"'")
            if list_val:
                # Determine the key to append to
                if parent_key:
                    list_key = parent_key
                elif last_list_key:
                    list_key = last_list_key
                else:
                    continue
                existing = fields.get(list_key, "")
                if existing:
                    fields[list_key] = f"{existing}, {list_val}"
                else:
                    fields[list_key] = list_val
    return fields


def parse_key_values(text: str, sections: Dict[str, str]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    # First: parse YAML block fields (higher priority)
    yaml_fields = parse_yaml_block_fields(text)
    fields.update(yaml_fields)
    # Then: parse inline key: value lines
    for line in (text or "").splitlines():
        m = re.match(
            r"^\s*(?:[-*]\s*)?(?:\*\*)?([^:\n：]{2,100}?)(?:\*\*)?\s*[:：]\s*(.+?)\s*$",
            line,
        )
        if not m:
            continue
        key = normalize_key(m.group(1))
        val = m.group(2).strip().strip("*` ")
        if key and val and key not in fields:
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


def parse_boolish(value: str) -> Optional[bool]:
    """Parse a string value into a boolean, supporting various truthy/falsy forms."""
    if value is None:
        return None
    v = str(value).strip().lower()
    if v in {"true", "yes", "y", "1", "✅", "present"}:
        return True
    if v in {"false", "no", "n", "0", "❌", "absent"}:
        return False
    return None


def get_bool_field(fields: Dict[str, str], canonical: str) -> Optional[bool]:
    """Get a boolean field value from fields dict using canonical name lookup."""
    value = get_field(fields, canonical)
    return parse_boolish(value)


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

    # TA-020 follow-up: recognize v3 schema submissions as structured
    schema_version = get_field(intake.fields, "record_class")
    if schema_version:
        return "structured_submission"

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
