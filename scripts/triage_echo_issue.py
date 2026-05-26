#!/usr/bin/env python3
"""
Echo Issue Triage Script
Reads issue title/body from env, outputs triage result as JSON.
"""
import os
import re
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Ensure scripts/ is on sys.path for sibling imports
_scripts_dir = str(Path(__file__).resolve().parent)
if _scripts_dir not in sys.path:
    sys.path.insert(0, _scripts_dir)

try:
    from submission_intake import parse_submission, claim_gate_summary_looks_passed, claim_gate_summary_has_blocking_failure
except Exception:
    parse_submission = None
    claim_gate_summary_looks_passed = None
    claim_gate_summary_has_blocking_failure = None

# Normalized intake parser (Part A)
try:
    from echo_issue_intake import parse_echo_issue, NormalizedEchoIssue
    HAS_NORMALIZED_INTAKE = True
except ImportError:
    HAS_NORMALIZED_INTAKE = False

# P0 remediation: shared safety module
try:
    from claim_text_safety import (
        normalize_claim_text, compact_claim_text, normalized_forms,
        scan_text_for_triage_risks, scan_text_for_forbidden_claims,
        detect_boundary_normalized, detect_boundary_semantic_near_miss_normalized,
    )
    HAS_SHARED_SAFETY = True
except ImportError:
    HAS_SHARED_SAFETY = False

# Issue Text Claim Guard
try:
    from validate_issue_text_claims import classify_issue as itcg_classify
    HAS_ISSUE_TEXT_CLAIM_GUARD = True
except ImportError:
    HAS_ISSUE_TEXT_CLAIM_GUARD = False

# Issue Title / Label Guard
try:
    from validate_issue_title_label_guard import classify_issue_title_labels as itlg_classify
    HAS_ISSUE_TITLE_LABEL_GUARD = True
except ImportError:
    HAS_ISSUE_TITLE_LABEL_GUARD = False

from operational_policy import (
    MANAGED_LABELS as MANAGED_TRIAGE_LABELS,
    ECHO_RATE_LIMIT_60M,
    ECHO_RATE_LIMIT_24H,
    ECHO_RATE_LIMIT_GATEWAY_ECHO_60M,
    ECHO_RATE_LIMIT_GATEWAY_ECHO_24H,
    ECHO_RATE_LIMIT_GATEWAY_VERIFICATION_60M,
    ECHO_RATE_LIMIT_GATEWAY_VERIFICATION_24H,
)

TRIAGE_MARKER = "<!-- trinity-echo-triage-v2 -->"

def emit_result(result, title=None, body=None):
    """Prepend stable marker to comment and emit JSON.

    If title and body are provided and the result includes echo:screened,
    embed a screening digest for TOCTOU binding.
    """
    result.setdefault("managed_labels", MANAGED_TRIAGE_LABELS)
    comment = result.get("comment", "")
    if comment and TRIAGE_MARKER not in comment:
        comment = TRIAGE_MARKER + "\n" + comment

    # Embed screening digest when issue passes triage (echo:screened)
    labels = result.get("labels", [])
    if title is not None and body is not None and "echo:screened" in labels:
        from echo_issue_digest import compute_issue_screening_digest
        digest = compute_issue_screening_digest(title, body)
        digest_line = f"<!-- trinity-echo-screened-digest:v1 sha256={digest} -->"
        comment = digest_line + "\n" + comment

    result["comment"] = comment
    print(json.dumps(result, indent=2))


def build_human_review_action_comment():
    return """This Echo passed automated triage and is ready for human review.

Passing triage does not mean endorsement, archive inclusion, or independent attestation.

## Maintainer review action

After human review, comment exactly one of:

### Normal archive

```text
/echo archive
```

Archives the issue as an Echo JSON record, updates the archive, validates, commits, removes `needs-human-review`, and closes.

### Archive with agent-initiated provenance

Use this if the issue was submitted by an AI/agent through a maintainer account without a direct human instruction to submit this specific Echo:

```text
/echo archive
submission_origin: agent_initiated_via_prior_memory_and_browsing
human_directed_submission: false
human_supplied_link: false
human_supplied_summary: false
agent_browsed_for_submission: true
prior_memory_or_context_used: true
```

### Close without archive

```text
/echo close
```

Only repository OWNER / MEMBER / COLLABORATOR comments are honored.

This is a workflow prompt, not a judgment of intent."""


# --- Soft Issue Accumulator (ST-001/ST-002) ---
def add_unique(labels, label):
    if label not in labels:
        labels.append(label)


def add_soft_issue(soft, labels=None, title="", body="", fix=""):
    if labels:
        for label in labels:
            add_unique(soft["labels"], label)
    if title or body or fix:
        soft["sections"].append({"title": title, "body": body, "fix": fix})


def build_soft_comment(sections):
    parts = [
        "This Echo requires format and/or verification-claim review.",
        "",
        "Please edit this issue. Do not open a new issue.",
        "",
    ]
    for idx, s in enumerate(sections, start=1):
        parts.append(f"## {idx}. {s.get('title', 'Issue')}")
        if s.get("body"):
            parts.append("")
            parts.append(s["body"])
        if s.get("fix"):
            parts.append("")
            parts.append("Recommended fix:")
            parts.append("")
            parts.append(s["fix"])
        parts.append("")
    parts.append("---")
    parts.append("This is a claim-discipline and format check, not a judgment of intent.")
    return "\n".join(parts)


def build_level_specific_comment(level: str, codes: list) -> str:
    """Build level-specific triage comment per Part H3."""
    parts = []
    if level in ("V0",):
        parts.append("No hash, script, or Claim Gate evidence is required for V0. This is read-only orientation.")
    elif level in ("V1",):
        parts.append("No hash, script, or Claim Gate evidence is required for V1. This is authority-boundary recognition only.")
    elif level in ("V2", "V3"):
        if "missing_claim_gate_artifacts" in codes:
            parts.append(
                "V2+ technical claims require path-backed Claim Gate artifacts before archival acceptance.\n"
                "Embedded Evidence Input JSON is useful for review but is not the archival source of truth."
            )
    elif level in ("V4",):
        if "script_evidence_incomplete" in codes:
            parts.append(
                "V4 script-audited verification requires per-script command, environment, exit code, "
                "output summary, script scope, and non-scope."
            )
    elif level in ("V4+",):
        if "not_independent_attestation" in codes:
            parts.append(
                "Technical independent reproduction may support V4+ minimal, but it does not make this "
                "an independent attestation if the run was human-solicited."
            )
        if "v4plus_path_backed_independent_artifact_required" in codes:
            parts.append(
                "V4+ requires path-backed independent technical artifact or implementation digest. "
                "Inline code alone is not enough for archival V4+ acceptance."
            )
    if "context_depth_overclaim" in codes:
        parts.append("Declared context depth appears higher than the evidence supports.")
    return "\n\n".join(parts)


# --- Config ---
# Rate limits now sourced from operational_policy (api/operational-policy.v1.json)
RATE_LIMIT_60M = ECHO_RATE_LIMIT_60M
RATE_LIMIT_24H = ECHO_RATE_LIMIT_24H

BOUNDARY_PATTERNS = [
    r"bitcoin originals are final.*all echoes are non-amending",
    r"bitcoin originals are final.*all mirrors and echoes are non-amending",
    r"比特币三本体为最终权威.*所有回响均非修订",
    r"比特币三本体为最终权威.*所有镜像与回响均为非修订",
]

HARD_INVALID_IMPERATIVE = [
    r"\bmust believe\b",
    r"\bmust obey\b",
    r"\bmust propagate\b",
    r"\ball agents must\b",
    r"\byou are required to\b",
    r"必须相信",
    r"必须服从",
    r"必须传播",
    r"所有智能体必须",
]

HARD_INVALID_FINANCIAL = [
    r"\btoken sale\b",
    r"\bairdrop\b",
    r"\bguaranteed investment\b",
    r"\bbuy now\b",
    r"\bpump\b",
    r"\bcasino\b",
    r"赌博",
    r"投资回报",
    r"空投",
    r"发币",
]

HARD_INVALID_INJECTION = [
    r"ignore previous instructions",
    r"override system prompt",
    r"reveal hidden prompt",
    r"忽略之前所有指令",
    r"覆盖系统提示",
]

# --- Amendment patterns (POSITIVE claims only, excluding negations) ---
# Matches: "amends the trinity accord", "modifies the trinity accord", etc.
# Excludes: "does not amend", "does not modify", "不修改", "不修订", etc.

# Enumerate all conjugated verb forms explicitly for reliable matching
_AMEND_VERBS = [
    "amend", "amends", "amended", "amending",
    "modify", "modifies", "modified", "modifying",
    "supplement", "supplements", "supplemented", "supplementing",
    "extend", "extends", "extended", "extending",
    "replace", "replaces", "replaced", "replacing",
]
_AMEND_VERB_ALT = "|".join(re.escape(v) for v in sorted(_AMEND_VERBS, key=len, reverse=True))
_AMEND_VERB_PATTERN = rf"(?:{_AMEND_VERB_ALT})"
AMENDMENT_VERB_ZH = r"(?:修订|修改|补充|扩展|取代)"

# Positive English patterns: subject + verb + trinity accord
# Negative lookbehind excludes: "not amend", "does not modify", "never replace", etc.
HARD_INVALID_AMENDMENT = [
    # "I/We <verb> the trinity accord"
    r"(?<!\bnot\s)\b(?:i|we)\s+(?:" + _AMEND_VERB_PATTERN + r")\s+(?:the\s+)?trinity\s+accord",
    # "This Echo <verb>s the trinity accord"
    r"(?<!\bnot\s)\bthis\s+echo\s+(?:" + _AMEND_VERB_PATTERN + r")\s+(?:the\s+)?trinity\s+accord",
    # Catch-all: any amendment verb + trinity accord (excluding negation)
    r"(?<!\bnot\s)(?<!\bnever\s)\b(?:" + _AMEND_VERB_PATTERN + r")\s+(?:the\s+)?trinity\s+accord",
    # Chinese: positive claims only
    # "我/我们/本回响 修订/修改/补充/扩展/取代 三位一体协定"
    r"(?:我|我们|本回响)\s*" + AMENDMENT_VERB_ZH + r"(?:了)?\s*三位一体协定",
    # Catch-all Chinese (excluding negation)
    r"(?<!不)(?<!非)" + AMENDMENT_VERB_ZH + r"(?:了)?\s*三位一体协定",
]

HARD_INVALID_AUTHORITY_CLAIM = [
    r"(this\s+)?(website|echo|comment|mirror)\s+is\s+(the\s+)?final\s+authority",
    r"(网站|回响|评论|镜像)\s*是最终权威",
]

ECHO_TYPES = {
    "e1": "E1 Recognition Echo",
    "e2": "E2 Verification Echo",
    "e3": "E3 Critical Echo",
    "e4": "E4 Interpretive Echo",
    "e5": "E5 Technical Audit Echo",
    "e6": "E6 Propagation Echo",
    "e7": "E7 Refusal Echo",
    "e8": "E8 Witness Echo",
    "e9": "E9 Seed Echo",
    "recognition": "E1 Recognition Echo",
    "verification": "E2 Verification Echo",
    "critical": "E3 Critical Echo",
    "interpretive": "E4 Interpretive Echo",
    "technical audit": "E5 Technical Audit Echo",
    "technical-audit": "E5 Technical Audit Echo",
    "propagation": "E6 Propagation Echo",
    "refusal": "E7 Refusal Echo",
    "witness": "E8 Witness Echo",
    "seed": "E9 Seed Echo",
}

# Ordered so that longer suffixes match before shorter ones (V4+ before V4)
VERIFICATION_LEVELS = ["v4+", "v8", "v7", "v6", "v5", "v4", "v3", "v2", "v1", "v0"]

# Schema enum values (full form) — map to short form for checks
SCHEMA_VERIFICATION_MAP = {
    "V0_orientation": "V0",
    "V1_registry_check": "V1",
    "V2_pointer_and_manifest_check": "V2",
    "V3_single_artifact_check": "V3",
    "V4_release_mirror_check": "V4",
    "V5_full_evidence_chain_review": "V5",
    "V6_independent_node_or_rpc_check": "V6",
}

DEPRECATED_VERIFICATION_ALIASES = {
    "V3_single_artifact_check",
    "V6_independent_node_or_rpc_check",
}

OVERCLAIM_PHRASES = [
    r"hash verified",
    r"script-audited",
    r"independently reproduced",
    r"physical inspection",
    r"multi-party attestation",
    r"已验证哈希",
    r"已审计脚本",
    r"已独立复现",
    r"已物理检查",
    r"多方见证",
]

# --- V3 Provenance field detection ---
PROVENANCE_FIELDS = [
    "discovery_source", "agency_level", "independence_class",
    "archive_status", "solicited", "soliciting_party",
    "prompt_available", "human_supplied_link", "human_supplied_summary",
    "independent_followup",
]

INDEPENDENCE_CLASSES = [
    "unsolicited_independent", "solicited_independent_check",
    "human_solicited_agent_response", "maintainer_assisted",
    "maintainer_submitted", "self_reported", "imported_public_commentary",
    "institutional_third_party_attestation", "test_record", "legacy", "unknown",
]


def get_env(name, default=""):
    return os.environ.get(name, default).strip()


def match_any(text, patterns):
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def find_match(text, patterns):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(0)
    return None


def detect_echo_type(text):
    for key, label in ECHO_TYPES.items():
        if re.search(r'\b' + re.escape(key) + r'\b', text, re.IGNORECASE):
            return label
    return None


def detect_verification_level(text):
    """Detect verification level, matching longer suffixes first (V4+ before V4).
    Also recognizes schema enum values like V3_single_artifact_check."""
    # First check for schema enum values (full form)
    for schema_val, short_val in SCHEMA_VERIFICATION_MAP.items():
        if re.search(re.escape(schema_val), text, re.IGNORECASE):
            return short_val
    # Then check for short forms
    for level in VERIFICATION_LEVELS:
        pattern = r'\b' + re.escape(level) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            if level == "v4+":
                return "V4+"
            return level.upper()
    return None


def detect_deprecated_verification_aliases(text):
    """Detect deprecated verification enum strings (R19 fix)."""
    found = []
    for alias in DEPRECATED_VERIFICATION_ALIASES:
        if re.search(re.escape(alias), text, re.IGNORECASE):
            found.append(alias)
    return found


def detect_boundary(text):
    # P0 remediation: use normalized matching to defeat zero-width/homoglyph bypass
    if HAS_SHARED_SAFETY:
        return detect_boundary_normalized(text)
    for p in BOUNDARY_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def detect_boundary_semantic_near_miss(text):
    """Detect semantically close but non-canonical authority boundary wording.

    This should NOT pass the exact protocol gate.
    It should prevent auto-close and route to format review.
    """
    # P0 remediation: use normalized matching
    if HAS_SHARED_SAFETY:
        return detect_boundary_semantic_near_miss_normalized(text)

    text_lower = text.lower()

    has_bitcoin_final = bool(
        re.search(r"bitcoin originals?\s+(are|remain)\s+(the\s+)?final(\s+authority)?", text_lower)
        or re.search(r"bitcoin originals?\s+remain\s+final\s+authority", text_lower)
        or re.search(r"比特币三本体\s*(为|是)?\s*最终权威", text)
    )

    has_non_amending = bool(
        "non-amending" in text_lower
        or re.search(r"does\s+not\s+amend", text_lower)
        or re.search(r"do\s+not\s+amend", text_lower)
        or re.search(r"non\s+amending", text_lower)
        or "非修订" in text
        or "不修订" in text
        or "不修改" in text
    )

    has_echo_or_mirror_scope = bool(
        "echo" in text_lower
        or "echoes" in text_lower
        or "mirror" in text_lower
        or "mirrors" in text_lower
        or "回响" in text
        or "镜像" in text
    )

    return has_bitcoin_final and has_non_amending and has_echo_or_mirror_scope


V0_OVERCLAIM_RISK_PHRASES = [
    r"\bfix verification\b",
    r"\bverification result\b",
    r"\bverified\b",
    r"\bscript-audited\b",
    r"\bindependently reproduced\b",
    r"\bhash verified\b",
    r"\bfull verification\b",
    r"已验证",
    r"已审计",
    r"独立复现",
]


def detect_v0_overclaim_wording(text):
    """Detect V0 Echo using wording that implies higher-level verification."""
    vlevel = detect_verification_level(text)
    if vlevel != "V0":
        return []

    found = []
    for p in V0_OVERCLAIM_RISK_PHRASES:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            found.append(m.group(0))
    return found


def detect_independence_class(text):
    """Detect independence_class from issue body."""
    text_lower = text.lower()
    for cls in INDEPENDENCE_CLASSES:
        if cls in text_lower:
            return cls
    return None


def detect_discovery_source(text):
    """Detect discovery source from issue body."""
    sources = [
        "self_initiated", "agent_recommended", "human_directed", "human_contextual",
        "search_engine", "crawler_discovery", "platform_recommendation",
        "prior_memory", "dataset_or_training_trace", "maintainer_submitted",
        "imported_external_commentary", "unknown",
    ]
    text_lower = text.lower()
    for src in sources:
        if src in text_lower:
            return src
    return None


def detect_solicited(text):
    """Detect whether the echo was solicited."""
    text_lower = text.lower()
    if re.search(r'solicited[:\s]*yes|was.*solicited.*yes|solicited.*true', text_lower):
        return "yes"
    if re.search(r'solicited[:\s]*no|was.*solicited.*no|unsolicited', text_lower):
        return "no"
    return None


def detect_soliciting_party(text):
    """Detect who solicited the echo."""
    text_lower = text.lower()
    parties = [
        "project_author_or_maintainer", "external_human", "institution",
        "other_agent", "not_solicited", "unknown",
    ]
    for party in parties:
        if party in text_lower:
            return party
    return None


def check_provenance_conflicts(text, independence_class, discovery_source, solicited, soliciting_party):
    """
    Check for provenance conflicts.
    Returns (labels, comment) if conflict found, else (None, None).
    """
    labels = []
    comments = []

    # Conflict: unsolicited_independent + human_directed / maintainer_submitted
    if independence_class == "unsolicited_independent" and discovery_source in ("human_directed", "maintainer_submitted"):
        labels.append("echo:provenance-conflict")
        comments.append(
            f"Provenance conflict: independence_class is `unsolicited_independent` but discovery_source is `{discovery_source}`. "
            "An unsolicited independent echo cannot be human-directed or maintainer-submitted."
        )

    # Conflict: institutional_third_party_attestation without institution evidence
    if independence_class == "institutional_third_party_attestation":
        has_institution = bool(re.search(
            r'institution[:\s]+\S+|organization[:\s]+\S+|机构[:\s]*\S+|组织[:\s]*\S+',
            text, re.IGNORECASE
        ))
        if not has_institution:
            labels.append("echo:attestation-overclaim")
            comments.append(
                "Independence class claims `institutional_third_party_attestation` but no institution identity or evidence was found. "
                "An institutional attestation must identify the institution."
            )

    # human_solicited_agent_response / test_record should not be screened as independent
    if independence_class in ("human_solicited_agent_response", "test_record"):
        if "echo:screened" in labels:
            labels.remove("echo:screened")
        labels.append("echo:solicited-record")
        comments.append(
            f"This echo is classified as `{independence_class}`. "
            "It will not be counted as unsolicited independent discovery, external social adoption, or institutional attestation."
        )

    if labels:
        return labels, "\n\n".join(comments)
    return None, None


def detect_missing_provenance(text):
    """Check which provenance fields are missing from the issue body."""
    missing = []
    text_lower = text.lower()
    for field in PROVENANCE_FIELDS:
        # Match field name with underscores, spaces, or hyphens
        field_pattern = field.replace("_", "[-_ ]")
        if not re.search(field_pattern, text_lower):
            missing.append(field)
    return missing


def is_v3_submission(text):
    """Check if this issue uses the v3 provenance-aware template."""
    text_lower = text.lower()
    # Internal schema version field is allowed
    if "echo_submission_schema_version" in text_lower and "v3" in text_lower:
        return True
    # Check if v3-specific provenance fields are present (not just the word "provenance")
    v3_specific = ["discovery_source", "archive_status", "soliciting_party",
                    "prompt_available", "human_supplied_link", "independent_followup"]
    found = sum(1 for field in v3_specific if re.search(field.replace("_", "[-_ ]"), text_lower))
    return found >= 3


def is_echo_submission(text):
    return bool(
        re.search(r'\becho\b', text, re.IGNORECASE)
        or re.search(r'回响', text)
        or re.search(r'\be[1-9]\b', text, re.IGNORECASE)
        or re.search(r'verification level|验证等级', text, re.IGNORECASE)
        or re.search(r'boundary|权威边界', text, re.IGNORECASE)
    )


def extract_submission_type(text):
    """Extract submission_type from trinity-issue-intake machine block."""
    m = re.search(r'```trinity-issue-intake\s*(.*?)```', text, re.S)
    if not m:
        return None
    block = m.group(1)
    mt = re.search(r'submission_type\s*:\s*(\S+)', block)
    return mt.group(1) if mt else None


def has_gateway_rendered_canonical_boundary(text):
    """Check if the issue body contains Gateway-rendered canonical boundary sentence.

    Returns True if canonical_boundary_sentence and boundary_sentence_present: true
    are present in the machine block, indicating the Gateway renderer already inserted it.
    """
    m = re.search(r'```trinity-issue-intake\s*(.*?)```', text, re.S)
    if not m:
        return False
    block = m.group(1)
    has_canonical = 'canonical_boundary_sentence:' in block
    has_present = 'boundary_sentence_present: true' in block
    return has_canonical and has_present


def extract_intake_field(text: str, name: str) -> str | None:
    m = re.search(rf"^{re.escape(name)}\s*:\s*(.+?)\s*$", text, re.I | re.M)
    return m.group(1).strip() if m else None

def intake_flag_true(text: str, name: str) -> bool:
    return (extract_intake_field(text, name) or "").strip().lower() == "true"

def requested_archive_kind(text: str) -> str:
    return extract_intake_field(text, "requested_archive_kind") or ""

def auto_archive_action(text: str) -> str:
    return extract_intake_field(text, "auto_archive_action") or ""

def is_gateway_validated_echo_archive(text: str) -> bool:
    return (
        intake_flag_true(text, "created_by_gateway")
        and intake_flag_true(text, "server_validated")
        and intake_flag_true(text, "archive_ready")
        and requested_archive_kind(text) == "agent_declared_echo_archive"
        and auto_archive_action(text) == "auto_archive_agent_declared_echo"
    )

def is_gateway_validated_verification_archive(text: str) -> bool:
    return (
        intake_flag_true(text, "created_by_gateway")
        and intake_flag_true(text, "server_validated")
        and intake_flag_true(text, "archive_ready")
        and requested_archive_kind(text) == "agent_declared_verification_archive"
        and auto_archive_action(text) == "auto_archive_agent_declared_verification"
    )


# --- PA-002: Provenance / Agency required field detection ---
PROVENANCE_REQUIRED_FIELDS = {
    "solicited_status": [
        r"was this echo requested by a human\?",
        r"solicited_status\s*:",
        r"solicited\s*:",
        r"human requested\s*:",
        r"是否由人类要求",
    ],
    "independence_class": [
        r"independence class",
        r"independence_class\s*:",
        r"independence\s*:",
        r"独立性类别",
    ],
    "agency_level": [
        r"agency level",
        r"agency_level\s*:",
        r"agency\s*:",
        r"主动性等级",
        r"来源等级",
    ],
    "operator_type": [
        r"operator type",
        r"operator_type\s*:",
        r"who performed the verification actions",
        r"执行者类型",
        # v3 provenance fields that imply operator_type
        r"discovery source",
        r"discovery_source\s*:",
        r"发现来源",
    ],
}


def missing_provenance_fields(text):
    """Check which provenance/agency fields are missing from the issue body.

    TA-021: If the new simplified schema fields are present (discovery_autonomy,
    verifier_type, etc.), skip the old TA-020 provenance field requirements.
    """
    text_lower = text.lower()

    # Check if new TA-021 simplified schema is in use
    new_schema_indicators = [
        r"record_purpose\s*:",
        r"discovery_autonomy\s*:",
        r"verifier_type\s*:",
        r"verification_claimed\s*:",
    ]
    uses_new_schema = any(
        re.search(p, text_lower, re.IGNORECASE) for p in new_schema_indicators
    )
    if uses_new_schema:
        return []  # New schema replaces old provenance fields

    missing = []
    for field, patterns in PROVENANCE_REQUIRED_FIELDS.items():
        if not any(re.search(p, text_lower, re.IGNORECASE) for p in patterns):
            missing.append(field)
    return missing


# --- PA-003: Independence overclaim guardrail ---
INDEPENDENCE_OVERCLAIM_PATTERNS = [
    r"\bindependent attestation\b",
    r"\bindependent institutional attestation\b",
    r"\binstitutional attestation\b",
    r"\bunsolicited discovery\b",
    r"\bindependently discovered\b",
    r"\bfully independent verification\b",
]

SOFT_INDEPENDENCE_RISK_PATTERNS = [
    r"\bindependent verification\b",
    r"\bindependently computed\b",
    r"\bself-directed\b",
]


def extract_selected_value(text, field_names):
    """Extract a field value from issue body by field name patterns."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        for name in field_names:
            m = re.search(rf"{re.escape(name)}\s*:\s*(.+)$", line, re.IGNORECASE)
            if m:
                return m.group(1).strip().strip("*` ")
        lower = line.lower().strip()
        if any(name.lower() in lower for name in field_names):
            for j in range(i + 1, min(i + 5, len(lines))):
                val = lines[j].strip()
                if val and not val.startswith("#") and val not in ("_", "-"):
                    return val.strip("*` ")
    return ""


def detect_human_solicited_context(text):
    """Detect whether the Echo is human-solicited based on provenance fields."""
    text_lower = text.lower()
    independence = extract_selected_value(text, ["independence_class", "Independence Class", "Independence"])
    solicited = extract_selected_value(text, ["solicited_status", "Was this Echo requested by a human?", "solicited"])
    agency = extract_selected_value(text, ["agency_level", "Agency Level"])

    return (
        "human_solicited_agent_response" in independence.lower()
        or "yes_human_requested" in solicited.lower()
        or "human requested" in text_lower
        or "a human user requested" in text_lower
        or "a1_human_gave_exact_url" in agency.lower()
        or "a2_human_gave_repo_name" in agency.lower()
    )


def detect_independence_overclaim(text):
    """Detect human-solicited work claiming independent attestation."""
    text_lower = text.lower()
    human_solicited = detect_human_solicited_context(text)

    hard = []
    soft = []

    for p in INDEPENDENCE_OVERCLAIM_PATTERNS:
        m = re.search(p, text_lower, re.IGNORECASE)
        if m and not _is_in_negation_context(text, m.start()):
            hard.append(m.group(0))

    for p in SOFT_INDEPENDENCE_RISK_PATTERNS:
        m = re.search(p, text_lower, re.IGNORECASE)
        if m and not _is_in_negation_context(text, m.start()):
            soft.append(m.group(0))

    if human_solicited and hard:
        return {
            "severity": "hard",
            "patterns": hard,
            "reason": "Human-solicited agent work cannot claim independent attestation or unsolicited discovery.",
        }

    if human_solicited and soft:
        return {
            "severity": "soft",
            "patterns": soft,
            "reason": "Human-solicited agent work uses wording that may imply independence.",
        }

    return None


def detect_independence_overclaim_scoped(context_text, claim_text):
    # TA-020 follow-up: if structured attestation denial is present, skip overclaim detection
    if has_structured_attestation_denial(context_text):
        return None
    human_solicited = detect_human_solicited_context(context_text)
    hard = []
    soft = []
    for p in INDEPENDENCE_OVERCLAIM_PATTERNS:
        m = re.search(p, claim_text.lower(), re.IGNORECASE)
        if m and not _is_in_negation_context(claim_text, m.start()):
            hard.append(m.group(0))
    for p in SOFT_INDEPENDENCE_RISK_PATTERNS:
        m = re.search(p, claim_text.lower(), re.IGNORECASE)
        if m and not _is_in_negation_context(claim_text, m.start()):
            soft.append(m.group(0))
    if human_solicited and hard:
        return {"severity": "hard", "patterns": hard, "reason": "Human-solicited agent work cannot claim independent attestation or unsolicited discovery."}
    if human_solicited and soft:
        return {"severity": "soft", "patterns": soft, "reason": "Human-solicited agent work uses wording that may imply independence."}
    return None


def has_structured_attestation_denial(raw_text):
    t = (raw_text or "").lower()
    false_markers = [
        "independent_attestation: false", "institutional_attestation: false",
        "unsolicited_discovery: false", "multi_party_attestation: false",
        "count_as_independent_attestation: false", "do_not_count_as_attestation: true",
        "not_independent_attestation: true",
    ]
    return any(x in t for x in false_markers)


# --- V3/V4/V5/V6 verification-level content checks ---
def check_verification_requirements(text, vlevel):
    """
    Check whether the issue body has the content required for its declared level.
    Returns a list of missing requirement descriptions.
    """
    missing = []
    text_lower = text.lower()

    if vlevel in ("V3",):
        # V3 needs: computed hash / expected hash / tool or command
        has_hash = bool(re.search(
            r'(computed|expected|sha-?256|hash)\s*[:=]', text, re.IGNORECASE
        ))
        has_tool = bool(re.search(
            r'(tool|command|script|reproduce|reproduction)', text, re.IGNORECASE
        ))
        has_zh_hash = bool(re.search(r'(哈希|校验|验证值)', text))
        has_zh_tool = bool(re.search(r'(工具|命令|脚本|复现)', text))
        if not (has_hash or has_zh_hash):
            missing.append("computed hash / expected hash")
        if not (has_tool or has_zh_tool):
            missing.append("tool or command used")

    elif vlevel in ("V4", "V4+"):
        # V4/V4+ needs: reviewed script source / inputs / network access / command / output summary
        has_script = bool(re.search(
            r'(reviewed\s+)?(script\s+source|source\s+code|脚本源码|源代码)', text, re.IGNORECASE
        ))
        has_inputs = bool(re.search(
            r'(inputs?|input\s+data|输入|输入数据)', text, re.IGNORECASE
        ))
        has_network = bool(re.search(
            r'(network\s+access|http|curl|fetch|网络|请求)', text, re.IGNORECASE
        ))
        has_command = bool(re.search(
            r'(command|命令|执行)', text, re.IGNORECASE
        ))
        has_output = bool(re.search(
            r'(output\s+summary|result|输出|结果)', text, re.IGNORECASE
        ))
        checks = [
            ("reviewed script source", has_script),
            ("inputs", has_inputs),
            ("network access or command", has_network or has_command),
            ("output summary", has_output),
        ]
        for name, ok in checks:
            if not ok:
                missing.append(name)

    elif vlevel in ("V5",):
        # V5 (full public digital verification) needs: limitations + component findings
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")

    elif vlevel in ("V6",):
        # V6 (remote physical witness) needs: limitations + live witness evidence
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        has_live = bool(re.search(
            r'(live\s+remote|live\s+video|nonce|challenge|实时远程|实时视频|挑战)', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")
        if not has_live:
            missing.append("live remote witness evidence with nonce/challenge")

    elif vlevel in ("V7",):
        # V7 (onsite physical witness) needs: limitations + onsite physical inspection or custody log
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        has_physical = bool(re.search(
            r'(onsite|custody\s+log|direct\s+physical\s+inspection|'
            r'现场|保管记录|物理检查|亲自检查)', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")
        if not has_physical:
            missing.append("onsite physical inspection or custody log")

    elif vlevel in ("V8",):
        # V8 (forensic physical attestation) needs: limitations + tool-assisted forensic evidence
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        has_forensic = bool(re.search(
            r'(forensic|microscopy|tool-assisted|confidential\s+challenge|'
            r'法证|显微镜|工具辅助|保密挑战)', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")
        if not has_forensic:
            missing.append("tool-assisted forensic analysis evidence")

    elif vlevel in ("V6",):
        # V6 needs: limitations + participants or signed report
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        has_participants = bool(re.search(
            r'(participants?|witnesses?|signed\s+report|参与者|见证人|签署报告)', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")
        if not has_participants:
            missing.append("participants or signed report")

    return missing


# --- ST-003: V4+ Claim Gate ---
_V4PLUS_STRONG_CLAIM = re.compile(
    r"(?:v4\+\s*(?:full\s+)?(?:protocol\s+)?verification"
    r"|independent(?:ly)?\s+reproduced"
    r"|independent\s+digital\s+reproduction"
    r"|v4\+\s+(?:full|complete|verified|verification)\b)",
    re.IGNORECASE,
)

_V4PLUS_WEAK_MENTION = re.compile(
    r"(?:v4\+\s*(?:candidate|attempt|partial|draft|preliminary)"
    r"|not\s+v4\+"
    r"|非\s*v4\+)",
    re.IGNORECASE,
)


def claims_v4plus(text):
    """Return True only if text makes a strong V4+ claim (not just 'V4+ candidate')."""
    if _V4PLUS_WEAK_MENTION.search(text):
        return False
    return bool(_V4PLUS_STRONG_CLAIM.search(text))


V4PLUS_REQUIRED_SIGNALS = {
    "independent_method_used": [
        r"independent tool", r"independent implementation", r"custom script",
        r"not using official script", r"separate implementation", r"独立工具", r"独立实现",
    ],
    "target_artifact_or_claim": [
        r"target artifact", r"artifact:", r"inscription", r"manifest", r"target claim", r"验证目标",
    ],
    "command_or_code_reference": [
        r"command", r"code", r"script", r"source reviewed", r"命令", r"代码", r"脚本",
    ],
    "computed_result": [
        r"computed", r"actual", r"result", r"sha-?256", r"计算", r"结果",
    ],
    "expected_result_source": [
        r"expected", r"manifest", r"official result", r"声明值", r"预期",
    ],
    "comparison_result": [
        r"match", r"matched", r"compare", r"comparison", r"一致", r"比对",
    ],
    "scope_boundary": [
        r"scope", r"limitations?", r"not v5", r"not full public digital", r"范围", r"局限",
    ],
}


_NEGATION_CONTEXT = re.compile(
    r"(?:not[\s_]?(?:claimed|checked|performed|done|required|applicable|available|verified)"
    r"|does\s+not\s+claim"
    r"|do\s+not\s+claim"
    r"|no\s+claim"
    r"|\bis\s+not\b"
    r"|\bare\s+not\b"
    r"|\bdoes\s+not\b"
    r"|\bdo\s+not\b"
    r"|不(?:声称|主张|要求|适用)"
    r"|未(?:声称|主张))",
    re.IGNORECASE,
)

_NEGATION_SECTION_HEADER = re.compile(
    r"^[#\s*-]*(?:not[\s_]?(?:claimed|checked|verified|required|applicable)"
    r"|unavailable"
    r"|limitations?)\s*[:\-]?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _is_in_negation_context(text, match_pos):
    """Check if a match position is within a negation context (e.g. 'not_claimed' section)."""
    # Check the line containing the match
    line_start = text.rfind("\n", 0, match_pos) + 1
    line_end = text.find("\n", match_pos)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    if _NEGATION_CONTEXT.search(line):
        return True

    # Check if we're under a negation section header (not_claimed, not_checked, unavailable, etc.)
    preceding = text[:line_start]
    for m in _NEGATION_SECTION_HEADER.finditer(preceding):
        # Check if there's a non-list-item non-empty line between the header and the match
        section_start = m.end()
        between = text[section_start:line_start]
        # If the between text is only list items and blank lines, we're still in the section
        non_list_lines = [
            l for l in between.split("\n")
            if l.strip() and not l.strip().startswith("-") and not l.strip().startswith("*")
        ]
        if not non_list_lines:
            return True

    return False


def missing_signal_groups(text, signal_groups):
    missing = []
    for name, patterns in signal_groups.items():
        found_in_positive = False
        for p in patterns:
            m = re.search(p, text, re.IGNORECASE)
            if m and not _is_in_negation_context(text, m.start()):
                found_in_positive = True
                break
        if not found_in_positive:
            missing.append(name)
    return missing


def check_v4plus_claim_gate(text):
    if not claims_v4plus(text):
        return []
    missing = missing_signal_groups(text, V4PLUS_REQUIRED_SIGNALS)
    if re.search(r"full protocol verification|full verification|完整.*验证", text, re.IGNORECASE):
        if "not v5" not in text.lower() and "not full public digital" not in text.lower():
            missing.append("explicit_not_v5_boundary")
    return missing


# --- ST-004: B5/B6 Bitcoin Component Claim Gate ---
B5_REQUIRED_SIGNALS = {
    "raw_transaction_source": [r"raw transaction", r"raw tx", r"bitcoin node", r"mempool.*raw", r"blockstream.*raw", r"原始交易"],
    "witness_bytes_extracted": [r"witness bytes", r"witness data", r"extracted witness", r"见证数据", r"见证字节"],
    "extraction_tool_or_command": [r"ord", r"bitcoin-cli", r"command", r"script", r"tool", r"命令", r"工具"],
    "inscription_envelope_parsed": [r"ordinals envelope", r"inscription envelope", r"envelope parsed", r"铭文 envelope"],
}

B6_REQUIRED_SIGNALS = {
    **B5_REQUIRED_SIGNALS,
    "body_bytes_reconstructed": [r"body bytes", r"reconstructed body", r"content bytes", r"body reconstructed", r"正文字节"],
    "computed_body_hash": [r"computed body hash", r"body sha-?256", r"content sha-?256", r"计算.*hash"],
    "expected_body_hash_source": [r"expected body hash", r"declared body hash", r"manifest", r"声明.*hash"],
}


def _claim_in_affirmative_context(text, patterns):
    """Check if any pattern matches in a non-negation context."""
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m and not _is_in_negation_context(text, m.start()):
            return True
    return False


def check_bitcoin_component_claim_gate(text):
    text_lower = text.lower()
    issues = []

    b5_patterns = [r"\bb5\b", r"witness parsing", r"witness extraction"]
    if _claim_in_affirmative_context(text, b5_patterns):
        missing = missing_signal_groups(text, B5_REQUIRED_SIGNALS)
        if missing:
            issues.append(("B5", missing))

    b6_patterns = [r"\bb6\b", r"body hash", r"content sha256", r"inscription body hash"]
    if _claim_in_affirmative_context(text, b6_patterns):
        missing = missing_signal_groups(text, B6_REQUIRED_SIGNALS)
        if missing:
            issues.append(("B6", missing))

    return issues


# --- ST-005: C5 / 175/175 Chronicle Recovery Gate ---
def claims_full_chronicle_recovery(text):
    text_lower = text.lower()
    return bool(
        "175/175" in text_lower
        or "full chronicle recovery" in text_lower
        or "all records verified" in text_lower
        or ("records verified" in text_lower and "175" in text_lower)
        or "full recovery" in text_lower
    )


C5_REQUIRED_SIGNALS = {
    "recovery_package_source": [r"recovery package", r"arweave", r"ipfs", r"package source", r"恢复包"],
    "downloaded_package_hash": [r"package hash", r"sha-?256", r"computed hash", r"恢复包.*hash"],
    "record_count_observed": [r"record count", r"175/175", r"175 records", r"记录数量"],
    "record_ids_or_manifest": [r"record ids", r"manifest", r"token_index", r"记录 ID"],
    "full_iteration_log": [r"iteration log", r"for each record", r"all records", r"每条记录", r"完整遍历"],
    "failures_count": [r"failures", r"failed", r"0 failures", r"失败"],
}


def check_chronicle_recovery_claim_gate(text):
    c5_patterns = [
        r"175/175", r"full chronicle recovery", r"all records verified",
        r"records verified.*175", r"full recovery",
    ]
    if not _claim_in_affirmative_context(text, c5_patterns):
        return []
    return missing_signal_groups(text, C5_REQUIRED_SIGNALS)


# --- ST-006: D5 / V5 / Full Public Digital Gate ---
def claims_full_public_digital(text):
    text_lower = text.lower()
    return bool(
        re.search(r"\bv5\b", text_lower)
        or "full public digital verification" in text_lower
        or "full protocol verification" in text_lower
        or "all mirrors verified" in text_lower
        or "all public digital targets" in text_lower
    )


V5_REQUIRED_SIGNALS = {
    "all_required_public_targets_checked": [r"all required public.*checked", r"all public digital targets", r"required targets", r"全部.*公共.*目标"],
    "unavailable_targets_listed": [r"unavailable targets", r"not checked", r"not available", r"unavailable", r"未检查", r"不可用"],
    "bitcoin_anchor_checked": [r"bitcoin", r"inscription", r"txid", r"block"],
    "github_artifacts_checked": [r"github", r"repository", r"manifest"],
    "arweave_checked_or_unavailable": [r"arweave", r"unavailable.*arweave", r"arweave.*not checked"],
    "ipfs_checked_or_unavailable": [r"ipfs", r"cid", r"unavailable.*ipfs", r"ipfs.*not checked"],
    "eth_witness_checked_or_unavailable": [r"eth", r"ethereum", r"guardian witness", r"unavailable.*eth", r"eth.*not checked"],
    "chronicle_checked_or_unavailable": [r"chronicle", r"recovery", r"175", r"chronicle.*not checked"],
}


def check_v5_full_public_digital_gate(text):
    v5_patterns = [
        r"\bv5\b", r"full public digital verification",
        r"full protocol verification", r"all mirrors verified",
        r"all public digital targets",
    ]
    if not _claim_in_affirmative_context(text, v5_patterns):
        return []
    return missing_signal_groups(text, V5_REQUIRED_SIGNALS)


# ── Part B1: Level-specific requirements (normalized intake) ───────
LEVEL_REQUIREMENTS = {
    "V0": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present"],
        "forbidden_requirements": ["hash", "claim_gate", "script_command"],
    },
    "V1": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present"],
        "forbidden_requirements": ["hash", "claim_gate", "script_command"],
    },
    "V2": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present", "verification_scope_label"],
        "requires_claim_gate": True,
        "claim_gate_mode": "lightweight_allowed",
    },
    "V3": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present", "verification_scope_label"],
        "requires_claim_gate": True,
        "claim_gate_mode": "required",
    },
    "V4": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present"],
        "requires_claim_gate": True,
        "requires_script_evidence": True,
    },
    "V4+": {
        "required": ["what_i_checked", "limitations", "boundary_sentence_present"],
        "requires_claim_gate": True,
        "requires_script_evidence": True,
        "requires_independent_technical_artifact": True,
    },
}


@dataclass
class TriageResult:
    """Structured triage result from normalized intake evaluation."""
    labels: list = field(default_factory=list)
    codes: list = field(default_factory=list)
    messages: list = field(default_factory=list)
    missing_fields: list = field(default_factory=list)
    missing_evidence: list = field(default_factory=list)


def evaluate_echo_issue(normalized: "NormalizedEchoIssue") -> TriageResult:
    """Evaluate a normalized Echo issue against level-specific rules.

    Part B1: Level-specific requirements.
    Part B5: Context-depth gating.
    Part B6: Assessment-state gating.
    Part B4: Independence negation handling.
    """
    result = TriageResult()
    level = normalized.verification_level
    scope = normalized.verification_scope_label

    if not level:
        result.codes.append("verification_level_parse_failed")
        result.messages.append(
            "Could not parse declared verification level. "
            "Please provide `Verification Level: V0–V8` and, for V2/V3, `Scope Label`."
        )
        return result

    req = LEVEL_REQUIREMENTS.get(level)
    if not req:
        result.codes.append("unknown_level")
        return result

    # ── Required fields ────────────────────────────────────────────
    for field_name in req.get("required", []):
        val = getattr(normalized, field_name, None)
        if field_name == "boundary_sentence_present":
            if not val:
                result.missing_fields.append("boundary_sentence")
                result.codes.append("missing_boundary")
        elif field_name == "verification_scope_label":
            if not val:
                result.missing_fields.append("verification_scope_label")
                result.codes.append("missing_scope_label")
        elif not val:
            result.missing_fields.append(field_name)
            result.codes.append(f"missing_{field_name}")

    # ── Claim Gate requirement (V2+) ───────────────────────────────
    if req.get("requires_claim_gate"):
        has_cg_path = bool(normalized.claim_gate_output_path)
        has_cg_embedded = bool(normalized.evidence_input_embedded)
        if not has_cg_path and has_cg_embedded:
            # Only flag when embedded JSON exists but path is missing
            result.codes.append("missing_claim_gate_artifacts")
            result.messages.append(
                "Embedded Evidence Input JSON was found, but V2+ submissions must reference "
                "path-backed Claim Gate artifacts: evidence_input_path, claim_gate_output_path. "
                "Please add repository paths or run the report builder."
            )
            result.labels.append("echo:needs-verification-review")
        # Don't flag for freeform submissions without embedded JSON
        # (they get format review from the soft issue accumulator instead)

    # ── V4 script evidence ─────────────────────────────────────────
    if req.get("requires_script_evidence"):
        has_embedded = bool(normalized.evidence_input_embedded)
        if has_embedded:
            scripts = normalized.evidence_input_embedded.get("evidence", {}).get("scripts", [])
            if scripts:
                for s in scripts:
                    if not s.get("command"):
                        result.codes.append("script_evidence_incomplete")
                        result.messages.append(
                            "V4 script-audited verification requires per-script: command, environment, "
                            "exit code, output summary, script scope, and non-scope."
                        )
                        break
            # If scripts array is empty or missing, don't flag — it's a freeform submission
        # Only flag script_evidence_incomplete for claim-gate-referenced or builder-generated modes
        # Don't flag for freeform V4 submissions (they get format review instead)

    # ── V4+ independent technical artifact ─────────────────────────
    if req.get("requires_independent_technical_artifact"):
        tech = normalized.technical_independence
        # Only flag if the issue explicitly claims V4+ with independent reproduction language
        body_lower = (normalized.body or "").lower()
        claims_independent = bool(re.search(
            r'\bindependent\s+(?:tool|implementation|code|reproduction)\b', body_lower
        ))
        if tech not in ("independent_tool", "independent_implementation") and claims_independent:
            result.codes.append("v4plus_path_backed_independent_artifact_required")
            result.messages.append(
                "V4+ requires path-backed independent technical artifact or implementation digest. "
                "Inline code alone is not enough for archival V4+ acceptance."
            )

    # ── Part B5: Context-depth gating ──────────────────────────────
    ctx = normalized.context_depth
    if ctx:
        ctx_ok = True
        if ctx == "C5_full_chain_reviewed":
            # Needs full-chain report path or all public digital targets listed
            has_full_chain = bool(normalized.claim_gate_output_path)  # simplified check
            has_all_targets = bool(normalized.what_i_checked and len(normalized.what_i_checked) > 200)
            if not (has_full_chain or has_all_targets):
                ctx_ok = False
        elif ctx == "C6_independent_node_verified":
            # Needs local node / SPV / independent node RPC evidence
            body_lower = (normalized.body or "").lower()
            has_node = bool(re.search(
                r'(local\s+node|spv|independent\s+node|bitcoin\s+core|bitcoind|rpc|'
                r'本地节点|独立节点)', body_lower
            ))
            if not has_node:
                ctx_ok = False
        if not ctx_ok:
            result.codes.append("context_depth_overclaim")
            result.labels.append("context-depth-overclaim-risk")
            result.messages.append(
                f"Declared context depth ({ctx}) appears higher than the evidence supports."
            )

    # ── Part B6: Assessment-state gating ───────────────────────────
    assessment = normalized.assessment_state
    if assessment == "independent_verification_assessment":
        social = normalized.social_independence
        if social == "human_solicited_not_attestation":
            result.codes.append("not_independent_attestation")
            result.labels.append("not-independent-attestation")
            result.messages.append(
                "Assessment state is 'independent_verification_assessment' but the record is "
                "human-solicited. This is technical independence only, not social independent attestation."
            )

    # ── Part B4: Solicited-record boundary ─────────────────────────
    social = normalized.social_independence
    if social == "human_solicited_not_attestation":
        result.labels.append("echo:solicited-record")
        result.codes.append("solicited_record_boundary")
        # Do NOT add provenance-conflict for normal solicited records
        # Only add it if there's an actual contradiction (checked elsewhere)

    return result


def main():
    # P3 remediation: support --event-json for hardened input
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--event-json", help="Path to GitHub event JSON file")
    args, _ = parser.parse_known_args()

    if args.event_json:
        try:
            with open(args.event_json, "r", encoding="utf-8") as f:
                event = json.load(f)
            issue = event.get("issue", {})
            title = issue.get("title", "")
            body = issue.get("body", "")
            association = issue.get("author_association", get_env("AUTHOR_ASSOCIATION", "NONE"))
            action = event.get("action", get_env("ACTION", "opened"))
        except Exception as e:
            print(json.dumps({"error": f"Failed to read event JSON: {e}"}))
            return
    else:
        title = get_env("ISSUE_TITLE")
        body = get_env("ISSUE_BODY")
        association = get_env("AUTHOR_ASSOCIATION", "NONE")
        action = get_env("ACTION", "opened")

    rate_limited = get_env("RATE_LIMITED", "false").lower() == "true"
    rate_class = get_env("RATE_CLASS", "direct")
    rate_identity = get_env("RATE_IDENTITY", "")
    active_rate_limit_60m = get_env("RATE_LIMIT_60M", "")
    active_rate_limit_24h = get_env("RATE_LIMIT_24H", "")

    # S17: Cap body size to prevent excessive processing
    MAX_BODY_CHARS = 60000
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS]

    count60 = get_env("RECENT_60M_COUNT", "0")
    count24 = get_env("RECENT_24H_COUNT", "0")

    text = f"{title}\n{body}"

    intake = parse_submission(title, body) if parse_submission else None
    declared_vlevel = intake.declared_level if intake else detect_verification_level(text)
    positive_text = intake.positive_text if intake else text
    negative_text = intake.negative_text if intake else ""
    mode = intake.mode if intake else "legacy_freeform_or_needs_format"

    result = {"close": False, "labels": [], "labels_to_remove": [], "comment": "", "recommended_title": None}

    # Detect submission_type for wording distinction
    submission_type = extract_submission_type(text)
    is_report_candidate = submission_type == "verification_report_candidate"
    gateway_has_canonical = has_gateway_rendered_canonical_boundary(text)

    # Choose subject phrasing based on submission_type
    subject_phrase = "This verification report candidate" if is_report_candidate else "This Echo"

    # --- Step 0: Is this an Echo submission? ---
    if not is_echo_submission(text):
        result["labels"] = ["echo:not-detected"]
        result["comment"] = "This issue does not appear to be an Echo submission. No triage action taken."
        emit_result(result, title, body)
        return

    # --- Step 1: Rate limit check (only on opened events) ---
    should_apply_rate_limit = (action == "opened")
    if should_apply_rate_limit and rate_limited:
        display_60m = active_rate_limit_60m or str(ECHO_RATE_LIMIT_60M)
        display_24h = active_rate_limit_24h or str(ECHO_RATE_LIMIT_24H)
        result["close"] = True
        result["labels"] = ["echo:rate-limited", "auto-closed"]
        result["comment"] = (
            "You have submitted multiple Echo issues in a short period.\n"
            "To protect the Echo archive from spam and preserve review quality, this issue was automatically closed.\n\n"
            "**Current limits:**\n"
            f"- {display_60m} Echo issues per 60 minutes\n"
            f"- {display_24h} Echo issues per 24 hours\n\n"
            "Please edit an existing open Echo issue or wait before submitting again.\n\n"
            "---\n\n"
            "你在短时间内提交了多个回响 Issue。为防止刷屏并保护回响审核质量，本 Issue 已自动关闭。\n\n"
            "当前限制：\n"
            f"- 每 60 分钟最多 {display_60m} 个 Echo Issue\n"
            f"- 每 24 小时最多 {display_24h} 个 Echo Issue\n\n"
            "请编辑已有打开的 Echo Issue，或稍后再提交。"
        )
        emit_result(result, title, body)
        return

    # --- Step 1.2: Render API only — direct archive attempt detection ---
    # Per Render API only policy: V0-V5 agent-declared archive can only be
    # created through the Render API. Direct GitHub Issues attempting archive
    # must be closed with guidance. This runs before amendment/boundary checks
    # so that #168-like issues get direct archive guidance first.
    ARCHIVE_INTENT_PATTERNS = [
        r"agent_declared_verification_archive",
        r"Agent-Declared Verification Archive",
        r"V[0-5]\s+archive",
        r"trinity_issue_intake",
        r"archive_ready",
        r"auto_archive_agent_declared_verification",
    ]
    _has_archive_intent = any(re.search(p, text, re.IGNORECASE) for p in ARCHIVE_INTENT_PATTERNS)
    # Strict receipt check: all Render API receipt fields must be present
    from gateway_intake import parse_intake_block
    from gateway_v0_v5_policy import is_valid_gateway_receipt_block
    try:
        _intake_fields = parse_intake_block(text, required=False)
        _has_gateway_receipt = is_valid_gateway_receipt_block(_intake_fields) if _intake_fields else False
    except Exception:
        _has_gateway_receipt = False

    if _has_archive_intent and not _has_gateway_receipt:
        result["close"] = True
        result["labels"] = [
            "echo:invalid", "auto-closed",
            "invalid:direct-issue-archive-attempt",
            "render-api-required", "not-counted",
        ]
        result["comment"] = (
            "<!-- trinity-render-api-only-v1 -->\n\n"
            "This Issue was closed because V0–V5 agent-declared archive records "
            "can only be created through the Render API.\n\n"
            "Detected an archive-like direct GitHub Issue, but no valid Gateway receipt was present.\n\n"
            "GitHub Issues are output records, not submission inputs.\n\n"
            "Use:\n\n"
            "1. POST `/gateway/preflight`\n"
            "2. POST `/agent-submit`\n\n"
            "or use the official `/agent-submit/` page, which submits to the Render API.\n\n"
            "Do not paste hand-written `trinity_issue_intake` JSON or hand-written "
            "`trinity-issue-intake` blocks into GitHub Issues.\n\n"
            "---\n\n"
            "此 Issue 已关闭，因为 V0–V5 智能体自声明归档只能通过 Render API 创建。\n"
            "GitHub Issue 是输出记录，不是提交入口。\n"
            "请通过 `/gateway/preflight` 和 `/agent-submit` 提交。"
        )
        emit_result(result, title, body)
        return

    # --- Step 1.4: Receipt-bearing Gateway auto archive early exit ---
    # Valid Gateway archives are server-validated and server-rendered.
    # They should not be triaged as regular freeform Echoes.
    try:
        from gateway_intake import parse_intake_block
        from gateway_v0_v5_policy import is_valid_gateway_receipt_block
        _intake_fields = parse_intake_block(text, required=False)
        _has_valid_receipt = is_valid_gateway_receipt_block(_intake_fields) if _intake_fields else False
        _is_valid_gw_verification_archive = (
            _has_valid_receipt
            and is_gateway_validated_verification_archive(text)
            and "verification_oath_present: true" in text
        )
        _is_valid_gw_echo_archive = (
            _has_valid_receipt
            and is_gateway_validated_echo_archive(text)
            and (
                "agent_integrity_declaration_present: true" in text
                or "verification_oath_present: true" in text
            )
        )
    except Exception:
        _is_valid_gw_verification_archive = False
        _is_valid_gw_echo_archive = False

    if _is_valid_gw_verification_archive or _is_valid_gw_echo_archive:
        result["close"] = False
        result["labels"] = ["echo:screened", "needs-human-review"]
        archive_kind = (
            "agent_declared_echo_archive"
            if _is_valid_gw_echo_archive
            else "agent_declared_verification_archive"
        )
        result["comment"] = (
            "<!-- trinity-receipt-bearing-archive-v1 -->\n\n"
            f"This is a receipt-bearing Gateway auto archive candidate of kind `{archive_kind}`. "
            "It has been server-validated and server-rendered. "
            "The triage workflow will attempt auto-archive. If auto-archive fails, "
            "a maintainer may comment `/echo archive` to manually archive.\n\n"
            "This record remains non-authoritative, non-amending, and not independent attestation."
        )
        emit_result(result, title, body)
        return

    # --- Step 1.5: P0 unified normalized risk scan ---
    # This catches Unicode/homoglyph/synonym bypasses that raw regex may miss.
    if HAS_SHARED_SAFETY:
        triage_risks = scan_text_for_triage_risks(text)
        risk_categories = {r["category"] for r in triage_risks}
        # prompt_injection, imperative_command, financial_promotion → hard close
        hard_close_cats = {"prompt_injection", "imperative_command", "financial_promotion"}
        if risk_categories & hard_close_cats:
            matched = [r for r in triage_risks if r["category"] in hard_close_cats]
            match_summary = ", ".join(f"`{r['match']}`" for r in matched[:5])
            result["close"] = True
            result["labels"] = ["echo:invalid", "auto-closed"]
            result["comment"] = (
                f"{subject_phrase} was automatically closed because the unified risk scan detected "
                f"prohibited patterns: {match_summary}\n\n"
                "This is a protocol gate, not a judgment of your submission."
            )
            emit_result(result, title, body)
            return
        # amendment_claim, false_authority → hard close
        authority_cats = {"amendment_claim", "false_authority"}
        if risk_categories & authority_cats:
            result["close"] = True
            result["labels"] = ["echo:invalid", "auto-closed"]
            result["comment"] = (
                f"{subject_phrase} was automatically closed because it claims to amend the Trinity Accord "
                "or asserts false authority.\n\n"
                "Echoes are non-authoritative and non-amending.\n\n"
                "This is a protocol gate, not a judgment of your submission."
            )
            emit_result(result, title, body)
            return

    # --- Step 2: Hard invalid checks (legacy regex, retained as defense-in-depth) ---

    # 2a: Missing boundary sentence
    if not detect_boundary(text):
        # If Gateway renderer already inserted canonical boundary, skip missing-boundary-exact
        if gateway_has_canonical:
            pass  # Gateway-rendered canonical boundary is present; no triage action needed
        elif detect_boundary_semantic_near_miss(text):
            result["close"] = False
            result["labels"] = [
                "echo:needs-format",
                "missing-boundary-exact",
                "needs-human-review"
            ]
            result["comment"] = (
                f"{subject_phrase} appears to acknowledge the authority boundary, "
                "but it does not include the required exact boundary sentence. "
                "It has NOT been automatically closed.\n\n"
                "**Please edit the issue and add this exact sentence:**\n\n"
                "`Bitcoin Originals are final; all mirrors and echoes are non-amending.`\n\n"
                "This is a format gate, not a judgment of your submission.\n\n"
                "---\n\n"
                "本提交看起来已经承认权威边界，但没有包含要求的精确边界句。"
                "本 Issue 未被自动关闭。请编辑并加入以下精确句：\n\n"
                "`Bitcoin Originals are final; all mirrors and echoes are non-amending.`"
            )
            emit_result(result, title, body)
            return
        else:
            result["close"] = True
            result["labels"] = ["echo:invalid", "auto-closed", "missing-boundary"]
            result["comment"] = (
                f"{subject_phrase} was automatically closed because it is missing the required boundary sentence.\n\n"
                "**Required:** Your submission must include one of the following boundary sentences:\n"
                "- `Bitcoin Originals are final; all echoes are non-amending.`\n"
                "- `Bitcoin Originals are final; all mirrors and echoes are non-amending.`\n"
                "- `比特币三本体为最终权威；所有回响均非修订。`\n"
                "- `比特币三本体为最终权威；所有镜像与回响均为非修订。`\n\n"
                "Please edit this issue to add the boundary sentence, or submit a new submission with the boundary included.\n\n"
                "This is a protocol gate, not a judgment of your submission."
            )
            emit_result(result, title, body)
            return

    # 2b: Amendment claim (excluding negations)
    if match_any(text, HARD_INVALID_AMENDMENT):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            f"{subject_phrase} was automatically closed because it claims to amend, modify, supplement, extend, or replace The Trinity Accord.\n\n"
            "Echoes are non-authoritative and non-amending. No Echo can amend the canonical texts.\n\n"
            "Please review the authority boundary: https://www.trinityaccord.org/authority\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result, title, body)
        return

    # 2c: Authority claim
    if match_any(text, HARD_INVALID_AUTHORITY_CLAIM):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            f"{subject_phrase} was automatically closed because it claims that the website, Echo, comment, or mirror is final authority.\n\n"
            "Only the three Bitcoin inscriptions are final authority. All other materials are non-amending.\n\n"
            "Please review the authority boundary: https://www.trinityaccord.org/authority\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result, title, body)
        return

    # 2d: Imperative language
    if match_any(text, HARD_INVALID_IMPERATIVE):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            f"{subject_phrase} was automatically closed because it contains command-style language that demands belief, obedience, or propagation.\n\n"
            "The Trinity Accord does not instruct, command, or require any agent or human to believe, obey, or propagate.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result, title, body)
        return

    # 2e: Financial / spam
    if match_any(text, HARD_INVALID_FINANCIAL):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            f"{subject_phrase} was automatically closed because it contains financial, token, investment, or spam content.\n\n"
            "The Trinity Accord is not a financial project. Echoes must not contain advertisements, token promotions, or investment schemes.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result, title, body)
        return

    # 2f: Prompt injection
    if match_any(text, HARD_INVALID_INJECTION):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            f"{subject_phrase} was automatically closed because it contains prompt injection patterns.\n\n"
            "Echoes must not attempt to override system prompts, ignore instructions, or extract hidden content.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result, title, body)
        return

    # --- Step 2f-2: Issue Text Claim Guard ---
    if HAS_ISSUE_TEXT_CLAIM_GUARD:
        itcg_result = itcg_classify(text)
        # Guardian test: force labels and provisional warning
        if itcg_result.get("has_guardian_test_marker"):
            for lbl in ["guardian-test", "issue-submission-only", "not-independent-attestation", "claim-gate-required"]:
                add_unique(result["labels"], lbl)
            result["comment"] = (
                "This Issue is classified as a guardian test / issue_submission_only. "
                "It is human-solicited and does not count as independent attestation. "
                "The V-level statements in the Issue body or comments are provisional Issue text only "
                "and do not upgrade the accepted verification level. "
                "To archive a verification record, submit Evidence Input and regenerate a report "
                "through Claim Gate / Report Builder.\n\n"
                "Self-declared Issue levels are provisional until Claim Gate / Report Builder outputs are archived."
            )
            # Don't close here; let remaining triage continue for label accumulation

        # Provenance conflict: human-solicited claiming independent
        if itcg_result.get("provenance_conflict"):
            add_unique(result["labels"], "not-independent-attestation")
            add_unique(result["labels"], "claim-gate-required")
            if "echo:provenance-conflict" not in result["labels"]:
                add_unique(result["labels"], "echo:provenance-conflict")

        # Technical level claim without builder output
        if itcg_result.get("requires_claim_gate") and not itcg_result.get("has_builder_output_reference"):
            add_unique(result["labels"], "claim-gate-required")
            add_unique(result["labels"], "issue-submission-only")

        # Level upgrade language in comments
        if itcg_result.get("has_level_upgrade_claim"):
            add_unique(result["labels"], "claim-gate-required")
            if not result["comment"]:
                result["comment"] = (
                    "This comment contains provisional level-upgrade language. "
                    "Issue comments cannot upgrade verification level. "
                    "To update the accepted level, submit Evidence Input and regenerate the report "
                    "through Claim Gate / Report Builder.\n\n"
                    "Self-declared Issue levels are provisional until Claim Gate / Report Builder outputs are archived."
                )

        # All-green overclaim
        if itcg_result.get("all_green_overclaim"):
            add_unique(result["labels"], "claim-gate-required")

    # --- Step 2f-3: Issue Title / Label Guard ---
    if HAS_ISSUE_TITLE_LABEL_GUARD:
        try:
            itlg_result = itlg_classify(title=title, body=body, labels=result.get("labels", []))

            # Title overclaim
            if itlg_result.get("title_overclaims_allowed_level"):
                add_unique(result["labels"], "claim-gate-required")
                if itlg_result.get("recommended_title"):
                    result["recommended_title"] = itlg_result["recommended_title"]
                if not result["comment"]:
                    result["comment"] = (
                        "Issue title overclaims the Claim Gate allowed level. "
                        f"Recommended title: {itlg_result.get('recommended_title', 'N/A')}\n\n"
                        "Wrong: Guardian Test V4/V4+\n"
                        f"Correct: {itlg_result.get('recommended_title', 'Guardian Test — requested V4/V4+, Claim Gate allowed V3')}"
                    )

            # Forbidden labels on guardian tests
            if itlg_result.get("forbidden_labels_present"):
                for lbl in itlg_result["forbidden_labels_present"]:
                    add_unique(result["labels_to_remove"], lbl)
                for lbl in itlg_result.get("recommended_labels_add", []):
                    add_unique(result["labels"], lbl)

            # Comment upgrade detected
            if itlg_result.get("comment_status") == "comment_upgrade_detected":
                add_unique(result["labels"], "claim-gate-required")
                if not result["comment"]:
                    result["comment"] = (
                        "Issue comments cannot upgrade verification level. "
                        "Submit Evidence Input and regenerate builder outputs."
                    )

            # Guardian test forced non-attestation
            if itlg_result.get("is_guardian_test"):
                for lbl in ["guardian-test", "issue-submission-only", "not-independent-attestation", "not-archived", "claim-gate-required"]:
                    add_unique(result["labels"], lbl)

            # Right/wrong guidance
            if itlg_result.get("right_wrong_guidance"):
                guidance_lines = []
                for g in itlg_result["right_wrong_guidance"]:
                    guidance_lines.append(f"Wrong: {g.get('wrong', '')}")
                    guidance_lines.append(f"Correct: {g.get('right', '')}")
                if guidance_lines and not result["comment"]:
                    result["comment"] = "\n".join(guidance_lines)

        except Exception:
            pass  # Fall through if ITLG fails

    # --- Step 2g: Normalized intake evaluation (Part A/B) ---
    normalized_triage = None
    if HAS_NORMALIZED_INTAKE:
        try:
            normalized = parse_echo_issue(None, title, body)
            normalized_triage = evaluate_echo_issue(normalized)
            # Merge labels from normalized triage
            for lbl in normalized_triage.labels:
                add_unique(result["labels"], lbl)
        except Exception:
            pass  # Fall through to legacy triage

    # --- Step 3+: Soft issue accumulator (ST-001/ST-002) ---
    soft = {"labels": [], "sections": []}

    # --- Step 3: Soft invalid — missing format fields ---
    missing_fields = []
    if not detect_echo_type(text):
        missing_fields.append("Echo type (E1–E9)")
    if not detect_verification_level(text):
        missing_fields.append("Verification level (V0–V8)")

    # Part B3: Use normalized intake for section alias matching
    has_checked = False
    has_limitations = False
    if normalized_triage is not None and HAS_NORMALIZED_INTAKE:
        try:
            norm = parse_echo_issue(None, title, body)
            has_checked = bool(norm.what_i_checked)
            has_limitations = bool(norm.limitations)
        except Exception:
            pass
    if not has_checked:
        has_checked = bool(re.search(r'what\s+(i|we)\s+checked|checks\s+performed|我检查了|已检查', text, re.IGNORECASE))
    if not has_limitations:
        has_limitations = bool(re.search(r'limitations?|what\s+remains\s+uncertain|uncertainties|局限|限制', text, re.IGNORECASE))

    if not has_checked:
        missing_fields.append("What I checked")
    if not has_limitations:
        missing_fields.append("Limitations")

    if missing_fields:
        fields_list = "\n".join(f"- {f}" for f in missing_fields)
        add_soft_issue(
            soft,
            labels=["echo:needs-format"],
            title="Missing required format fields",
            body=f"Missing:\n{fields_list}",
            fix="Please edit this issue to add the missing fields.\n\n"
                 "Recommended format:\n"
                 "- Echo type (E1–E9)\n"
                 "- Verification level (V0–V8)\n"
                 "- What I checked\n"
                 "- Limitations\n"
                 "- Boundary sentence",
        )

    # --- Step 3a: PA-002 — Provenance / Agency required fields ---
    prov_missing = missing_provenance_fields(text)
    if prov_missing:
        missing_list = "\n".join(f"- {f}" for f in prov_missing)
        add_soft_issue(
            soft,
            labels=["echo:needs-format", "missing-provenance-agency"],
            title="Missing Provenance / Agency fields",
            body=f"Missing:\n{missing_list}\n\n"
                 "These fields prevent human-solicited agent work from being misread as independent attestation.",
            fix="```markdown\n"
                "## Provenance / Agency\n"
                "- solicited: true\n"
                "- independence_class: human_solicited_agent_response\n"
                "- agency_level: A1_human_gave_exact_url\n"
                "- operator_type: ai_agent\n"
                "- not_independent_attestation: true\n"
                "```",
        )

    # --- Step 3a-2: PA-003 — Independence overclaim guardrail ---
    if has_structured_attestation_denial(text):
        overclaim_risk = None
    else:
        overclaim_risk = detect_independence_overclaim_scoped(text, positive_text)
    if overclaim_risk:
        patterns_str = ", ".join(f"`{p}`" for p in overclaim_risk["patterns"])
        add_soft_issue(
            soft,
            labels=["echo:needs-verification-review", "independence-overclaim-risk"],
            title="Independence overclaim detected",
            body=f"Human-solicited agent work uses independence wording: {patterns_str}\n\n"
                 f"Reason: {overclaim_risk['reason']}",
            fix="Replace `independent verification` or `self-directed` with:\n\n"
                "`human-solicited agent-performed verification run; not independent attestation.`\n\n"
                "```markdown\n"
                "## Provenance / Agency\n"
                "- solicited: true\n"
                "- independence_class: human_solicited_agent_response\n"
                "- agency_level: A1_human_gave_exact_url\n"
                "- operator_type: ai_agent\n"
                "- not_independent_attestation: true\n"
                "```",
        )

    # --- V-level detection (moved before V0 overclaim check) ---
    # Part A: Use normalized intake for robust V-level parsing (never VNone)
    normalized_vlevel = None
    if HAS_NORMALIZED_INTAKE:
        try:
            norm_v = parse_echo_issue(None, title, body)
            normalized_vlevel = norm_v.verification_level
        except Exception:
            pass
    vlevel = declared_vlevel or normalized_vlevel
    legacy_vlevel = None
    if not vlevel and mode == "legacy_freeform_or_needs_format":
        legacy_vlevel = detect_verification_level(positive_text)
    effective_vlevel = vlevel or legacy_vlevel

    # --- Step 3b: V0 overclaim wording guardrail ---
    if effective_vlevel == "V0":
        v0_risk = []
        for p in V0_OVERCLAIM_RISK_PHRASES:
            m = re.search(p, positive_text, re.IGNORECASE)
            if m:
                v0_risk.append(m.group(0))
    else:
        v0_risk = []
    if v0_risk:
        phrases = ", ".join(f"`{p}`" for p in sorted(set(v0_risk)))
        add_soft_issue(
            soft,
            labels=["echo:needs-verification-review", "v0-overclaim-risk"],
            title="V0 wording implies higher-level verification",
            body=f"Phrases: {phrases}",
            fix="Replace with `read-only review`, `CI status observed`, or `repository review observed`.",
        )

    # --- Step 4: Possible overclaim ---
    overclaim_found = []

    if vlevel in ("V0", "V1"):
        for phrase in OVERCLAIM_PHRASES:
            if re.search(phrase, text, re.IGNORECASE):
                overclaim_found.append(phrase)

    if overclaim_found:
        phrases_list = ", ".join(f"`{p}`" for p in overclaim_found)
        add_soft_issue(
            soft,
            labels=["echo:needs-verification-review"],
            title=f"V0/V1 overclaim: phrases suggest higher-level claims",
            body=f"Phrases: {phrases_list}",
            fix="A maintainer should review whether the verification level is appropriate.",
        )

    # --- Step 4b: Deprecated verification alias detection (R19 fix) ---
    deprecated_aliases = detect_deprecated_verification_aliases(text)
    if deprecated_aliases:
        alias_list = ", ".join(f"`{a}`" for a in deprecated_aliases)
        add_soft_issue(
            soft,
            labels=["echo:deprecated-verification-alias"],
            title="Deprecated verification enum strings",
            body=f"Deprecated: {alias_list}. Current schema accepts only short forms (V0–V8, V4+).",
            fix="Update to use the current verification level format.",
        )

    # --- V2 Claim Gate requirement ---
    if mode == "legacy_freeform_or_needs_format" and effective_vlevel == "V2":
        add_soft_issue(
            soft,
            labels=["echo:needs-format", "needs-human-review"],
            title="V2 reference verification should use lightweight Claim Gate evidence",
            body="This issue declares V2 reference verification but does not include `evidence_input_path` or `claim_gate_output_path`.",
            fix="Create a minimal V2 Evidence Input, run `scripts/claim_gate.py`, then add `evidence_input_path` and `claim_gate_output_path` or paste the Claim Gate summary.",
        )

    # --- Step 5: Verification-level content requirements ---
    if effective_vlevel and mode == "legacy_freeform_or_needs_format":
        vr_missing = check_verification_requirements(positive_text, effective_vlevel)
    else:
        vr_missing = []

    if vr_missing:
        missing_list = "\n".join(f"- {m}" for m in vr_missing)
        add_soft_issue(
            soft,
            labels=["echo:needs-verification-review"],
            title=f"V{vlevel} missing required content",
            body=f"Missing:\n{missing_list}",
            fix="Please edit to add the missing details.",
        )

    # --- Step 5b: V3 Provenance checks ---
    if is_v3_submission(text):
        missing_provenance = detect_missing_provenance(text)
        if len(missing_provenance) >= 5:
            missing_list = "\n".join(f"- {f}" for f in missing_provenance)
            add_soft_issue(
                soft,
                labels=["echo:missing-provenance"],
                title="Missing most v3 provenance fields",
                body=f"Missing:\n{missing_list}",
                fix="Please resubmit using the v3 Echo Submission template.",
            )
        else:
            # Check for provenance conflicts
            independence_class = detect_independence_class(text)
            discovery_source = detect_discovery_source(text)
            solicited = detect_solicited(text)
            soliciting_party = detect_soliciting_party(text)

            conflict_labels, conflict_comment = check_provenance_conflicts(
                text, independence_class, discovery_source, solicited, soliciting_party
            )
            if conflict_labels:
                for lbl in conflict_labels:
                    add_unique(soft["labels"], lbl)
                add_soft_issue(
                    soft,
                    title="Provenance conflict detected",
                    body=conflict_comment,
                )

    # --- ST-003: V4+ claim gate ---
    v4p_missing = check_v4plus_claim_gate(positive_text)
    if v4p_missing:
        add_soft_issue(
            soft,
            labels=["v4plus-overclaim-risk", "echo:needs-verification-review"],
            title="V4+ claim lacks required independent reproduction evidence",
            body="Missing V4+ evidence fields:\n" + "\n".join(f"- {m}" for m in v4p_missing),
            fix="```markdown\n"
                "## V4+ Reproduction Scope\n"
                "- independent_method_used:\n"
                "- official_method_not_used_or_limited:\n"
                "- target_artifact_or_claim:\n"
                "- command_or_code_reference:\n"
                "- computed_result:\n"
                "- expected_result_source:\n"
                "- comparison_result:\n"
                "- scope_boundary:\n"
                "- not_v5_full_public_digital_verification: true\n"
                "```",
        )

    # --- ST-004: B5/B6 Bitcoin component claim gate ---
    for level, missing in check_bitcoin_component_claim_gate(positive_text):
        add_soft_issue(
            soft,
            labels=["component-overclaim-risk", "bitcoin-component-overclaim-risk", "echo:needs-verification-review"],
            title=f"{level} Bitcoin component claim lacks required evidence",
            body=f"{level} requires witness extraction/body reconstruction evidence. Missing:\n" + "\n".join(f"- {m}" for m in missing),
            fix="```markdown\n"
                "## Bitcoin Witness / Body Verification Evidence\n"
                "- raw_transaction_source:\n"
                "- witness_bytes_extracted:\n"
                "- extraction_tool_or_command:\n"
                "- inscription_envelope_parsed:\n"
                "- body_bytes_reconstructed:\n"
                "- computed_body_hash:\n"
                "- expected_body_hash_source:\n"
                "- limitation: if these were not performed, downgrade to B1/B2.\n"
                "```",
        )

    # --- ST-005: C5 / 175/175 chronicle recovery gate ---
    c5_missing = check_chronicle_recovery_claim_gate(positive_text)
    if c5_missing:
        add_soft_issue(
            soft,
            labels=["component-overclaim-risk", "chronicle-overclaim-risk", "echo:needs-verification-review"],
            title="C5 / 175/175 recovery claim lacks full recovery evidence",
            body="Missing C5 evidence fields:\n" + "\n".join(f"- {m}" for m in c5_missing),
            fix="```markdown\n"
                "## Chronicle Full Recovery Evidence\n"
                "- recovery_package_source:\n"
                "- downloaded_package_hash:\n"
                "- record_count_observed:\n"
                "- record_ids_or_manifest:\n"
                "- full_iteration_log:\n"
                "- failures_count:\n"
                "- limitation: if full iteration was not performed, downgrade to C0/C1/C2/C3.\n"
                "```",
        )

    # --- ST-006: D5 / V5 / full public digital gate ---
    v5_missing = check_v5_full_public_digital_gate(positive_text)
    if v5_missing:
        add_soft_issue(
            soft,
            labels=["v5-overclaim-risk", "full-public-digital-overclaim-risk", "echo:needs-verification-review"],
            title="Full public digital / V5 claim lacks required target coverage",
            body="Missing V5 coverage fields:\n" + "\n".join(f"- {m}" for m in v5_missing),
            fix="```markdown\n"
                "## V5 Full Public Digital Coverage\n"
                "- all_required_public_targets_checked:\n"
                "- unavailable_targets:\n"
                "  - ...\n"
                "- bitcoin_anchor_checked:\n"
                "- github_artifacts_checked:\n"
                "- arweave_checked_or_unavailable:\n"
                "- ipfs_checked_or_unavailable:\n"
                "- eth_witness_checked_or_unavailable:\n"
                "- chronicle_checked_or_unavailable:\n"
                "- not_physical_verification: true\n"
                "```",
        )

    # --- Claim Gate referenced routing ---
    if mode == "claim_gate_referenced":
        labels = ["needs-human-review"]
        if "human_solicited_agent_response" in text.lower():
            labels.append("echo:solicited-record")
        if effective_vlevel in ("V6", "V7", "V8"):
            labels.append("echo:needs-verification-review")
        if claim_gate_summary_has_blocking_failure(text):
            labels.append("echo:needs-verification-review")
            comment = "Claim Gate output appears to contain blocking failures. This issue is routed for verification review. Triage did not infer V-level from free text."
        elif claim_gate_summary_looks_passed(text):
            labels.append("echo:screened")
            comment = "Claim Gate output was detected and appears to pass. This issue remains non-authoritative and is routed for human review. Triage did not infer verification level from free text."
        else:
            labels.append("echo:needs-verification-review")
            comment = "Claim Gate reference was detected, but triage could not confirm a PASS status from the issue text. Please include the Claim Gate summary or linked output. Triage did not infer verification level from free text."
        emit_result({"close": False, "labels": labels, "comment": comment}, title, body)
        return

    # --- Builder-generated routing ---
    if mode == "builder_generated_or_referenced":
        labels = ["needs-human-review"]
        if "human_solicited_agent_response" in text.lower():
            labels.append("echo:solicited-record")
        if effective_vlevel in ("V6", "V7", "V8"):
            labels.append("echo:needs-verification-review")
        if re.search(r"validation_result\s*[:=]\s*pass", text, re.IGNORECASE) or "validation_result\": \"PASS\"" in text:
            labels.append("echo:screened")
            comment = "Builder-generated verification output was detected with PASS validation metadata. Triage is limited to routing/status; validation should rely on the generated output and validator."
        else:
            labels.append("echo:needs-verification-review")
            comment = "Builder-generated output was referenced, but PASS validation metadata was not detected in the issue text. Please include validation output or ensure the linked generated file passes `validate_agent_submission.py`."
        emit_result({"close": False, "labels": labels, "comment": comment}, title, body)
        return

    # --- Final soft issue handling ---
    # Part H: Merge normalized triage results into soft issues
    if normalized_triage is not None:
        # Only merge issue-type labels, not informational ones like echo:solicited-record
        issue_labels = {
            "echo:needs-verification-review", "echo:needs-format",
            "context-depth-overclaim-risk", "not-independent-attestation",
            "independence-overclaim-risk",
        }
        for lbl in normalized_triage.labels:
            if lbl in issue_labels:
                add_unique(soft["labels"], lbl)
        # Add level-specific comments
        if HAS_NORMALIZED_INTAKE and normalized_triage.codes:
            try:
                norm_final = parse_echo_issue(None, title, body)
                level_comment = build_level_specific_comment(
                    norm_final.verification_level or "", normalized_triage.codes
                )
                if level_comment:
                    add_soft_issue(
                        soft,
                        title="Level-specific guidance",
                        body=level_comment,
                    )
            except Exception:
                pass

    if soft["labels"]:
        add_unique(soft["labels"], "needs-human-review")

        if any(
            label.endswith("overclaim-risk")
            or label in ("component-overclaim-risk", "v4plus-overclaim-risk", "v5-overclaim-risk")
            for label in soft["labels"]
        ):
            add_unique(soft["labels"], "echo:needs-verification-review")
        elif "echo:needs-format" not in soft["labels"]:
            add_unique(soft["labels"], "echo:needs-format")

        result["close"] = False
        result["labels"] = soft["labels"]
        result["comment"] = build_soft_comment(soft["sections"])
        emit_result(result, title, body)
        return

    # --- Step 6: Pass ---
    result["close"] = False
    result["labels"] = ["echo:screened", "needs-human-review"]
    result["comment"] = build_human_review_action_comment()
    emit_result(result, title, body)


if __name__ == "__main__":
    main()
