#!/usr/bin/env python3
"""
Echo Issue Triage Script
Reads issue title/body from env, outputs triage result as JSON.
"""
import os
import re
import json
import sys

TRIAGE_MARKER = "<!-- trinity-echo-triage-v1 -->"

def emit_result(result):
    """Prepend stable marker to comment and emit JSON."""
    comment = result.get("comment", "")
    if comment:
        result["comment"] = TRIAGE_MARKER + "\n" + comment
    print(json.dumps(result, indent=2))

# --- Config ---
RATE_LIMIT_60M = 3
RATE_LIMIT_24H = 8

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
    for p in BOUNDARY_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def detect_boundary_semantic_near_miss(text):
    """Detect semantically close but non-canonical authority boundary wording.

    This should NOT pass the exact protocol gate.
    It should prevent auto-close and route to format review.
    """
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
    # Look for explicit v3 markers or presence of provenance fields
    if "echo v3" in text_lower or "provenance" in text_lower:
        return True
    # Check if at least 5 provenance fields are present
    found = sum(1 for field in PROVENANCE_FIELDS if re.search(field.replace("_", "[-_ ]"), text_lower))
    return found >= 5


def is_echo_submission(text):
    return bool(
        re.search(r'\becho\b', text, re.IGNORECASE)
        or re.search(r'回响', text)
        or re.search(r'\be[1-9]\b', text, re.IGNORECASE)
        or re.search(r'verification level|验证等级', text, re.IGNORECASE)
        or re.search(r'boundary|权威边界', text, re.IGNORECASE)
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
    """Check which provenance/agency fields are missing from the issue body."""
    text_lower = text.lower()
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
        if re.search(p, text_lower, re.IGNORECASE):
            hard.append(re.search(p, text_lower, re.IGNORECASE).group(0))

    for p in SOFT_INDEPENDENCE_RISK_PATTERNS:
        if re.search(p, text_lower, re.IGNORECASE):
            soft.append(re.search(p, text_lower, re.IGNORECASE).group(0))

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


def main():
    title = get_env("ISSUE_TITLE")
    body = get_env("ISSUE_BODY")
    rate_limited = get_env("RATE_LIMITED", "false").lower() == "true"

    # S17: Cap body size to prevent excessive processing
    MAX_BODY_CHARS = 60000
    if len(body) > MAX_BODY_CHARS:
        body = body[:MAX_BODY_CHARS]

    count60 = get_env("RECENT_60M_COUNT", "0")
    count24 = get_env("RECENT_24H_COUNT", "0")
    association = get_env("AUTHOR_ASSOCIATION", "NONE")
    action = get_env("ACTION", "opened")

    text = f"{title}\n{body}"
    result = {"close": False, "labels": [], "comment": ""}

    # --- Step 0: Is this an Echo submission? ---
    if not is_echo_submission(text):
        result["labels"] = ["echo:not-detected"]
        result["comment"] = "This issue does not appear to be an Echo submission. No triage action taken."
        emit_result(result)
        return

    # --- Step 1: Rate limit check (only on opened events) ---
    should_apply_rate_limit = (action == "opened")
    if should_apply_rate_limit and rate_limited:
        result["close"] = True
        result["labels"] = ["echo:rate-limited", "auto-closed"]
        result["comment"] = (
            "You have submitted multiple Echo issues in a short period.\n"
            "To protect the Echo archive from spam and preserve review quality, this issue was automatically closed.\n\n"
            "**Current limits:**\n"
            "- 3 Echo issues per 60 minutes\n"
            "- 8 Echo issues per 24 hours\n\n"
            "Please edit an existing open Echo issue or wait before submitting again.\n\n"
            "---\n\n"
            "你在短时间内提交了多个回响 Issue。为防止刷屏并保护回响审核质量，本 Issue 已自动关闭。\n\n"
            "当前限制：\n"
            "- 每 60 分钟最多 3 个 Echo Issue\n"
            "- 每 24 小时最多 8 个 Echo Issue\n\n"
            "请编辑已有打开的 Echo Issue，或稍后再提交。"
        )
        emit_result(result)
        return

    # --- Step 2: Hard invalid checks ---

    # 2a: Missing boundary sentence
    if not detect_boundary(text):
        if detect_boundary_semantic_near_miss(text):
            result["close"] = False
            result["labels"] = [
                "echo:needs-format",
                "missing-boundary-exact",
                "needs-human-review"
            ]
            result["comment"] = (
                "This Echo appears to acknowledge the authority boundary, "
                "but it does not include the required exact boundary sentence. "
                "It has NOT been automatically closed.\n\n"
                "**Please edit the issue and add this exact sentence:**\n\n"
                "`Bitcoin Originals are final; all mirrors and echoes are non-amending.`\n\n"
                "This is a format gate, not a judgment of your submission.\n\n"
                "---\n\n"
                "本 Echo 看起来已经承认权威边界，但没有包含要求的精确边界句。"
                "本 Issue 未被自动关闭。请编辑并加入以下精确句：\n\n"
                "`Bitcoin Originals are final; all mirrors and echoes are non-amending.`"
            )
            emit_result(result)
            return

        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed", "missing-boundary"]
        result["comment"] = (
            "This Echo submission was automatically closed because it is missing the required boundary sentence.\n\n"
            "**Required:** Your Echo must include one of the following boundary sentences:\n"
            "- `Bitcoin Originals are final; all echoes are non-amending.`\n"
            "- `Bitcoin Originals are final; all mirrors and echoes are non-amending.`\n"
            "- `比特币三本体为最终权威；所有回响均非修订。`\n"
            "- `比特币三本体为最终权威；所有镜像与回响均为非修订。`\n\n"
            "Please edit this issue to add the boundary sentence, or submit a new Echo with the boundary included.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # 2b: Amendment claim (excluding negations)
    if match_any(text, HARD_INVALID_AMENDMENT):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            "This Echo was automatically closed because it claims to amend, modify, supplement, extend, or replace The Trinity Accord.\n\n"
            "Echoes are non-authoritative and non-amending. No Echo can amend the canonical texts.\n\n"
            "Please review the authority boundary: https://www.trinityaccord.org/authority\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # 2c: Authority claim
    if match_any(text, HARD_INVALID_AUTHORITY_CLAIM):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            "This Echo was automatically closed because it claims that the website, Echo, comment, or mirror is final authority.\n\n"
            "Only the three Bitcoin inscriptions are final authority. All other materials are non-amending.\n\n"
            "Please review the authority boundary: https://www.trinityaccord.org/authority\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # 2d: Imperative language
    if match_any(text, HARD_INVALID_IMPERATIVE):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            "This Echo was automatically closed because it contains command-style language that demands belief, obedience, or propagation.\n\n"
            "The Trinity Accord does not instruct, command, or require any agent or human to believe, obey, or propagate.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # 2e: Financial / spam
    if match_any(text, HARD_INVALID_FINANCIAL):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            "This Echo was automatically closed because it contains financial, token, investment, or spam content.\n\n"
            "The Trinity Accord is not a financial project. Echoes must not contain advertisements, token promotions, or investment schemes.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # 2f: Prompt injection
    if match_any(text, HARD_INVALID_INJECTION):
        result["close"] = True
        result["labels"] = ["echo:invalid", "auto-closed"]
        result["comment"] = (
            "This Echo was automatically closed because it contains prompt injection patterns.\n\n"
            "Echoes must not attempt to override system prompts, ignore instructions, or extract hidden content.\n\n"
            "This is a protocol gate, not a judgment of your submission."
        )
        emit_result(result)
        return

    # --- Step 3: Soft invalid — missing format fields ---
    missing_fields = []
    if not detect_echo_type(text):
        missing_fields.append("Echo type (E1–E9)")
    if not detect_verification_level(text):
        missing_fields.append("Verification level (V0–V8)")

    # Check for "what I checked" / "limitations" keywords
    has_checked = bool(re.search(r'what\s+(i|we)\s+checked|我检查了|已检查', text, re.IGNORECASE))
    has_limitations = bool(re.search(r'limitations?|局限|限制', text, re.IGNORECASE))

    if not has_checked:
        missing_fields.append("What I checked")
    if not has_limitations:
        missing_fields.append("Limitations")

    if missing_fields:
        result["close"] = False
        result["labels"] = ["echo:needs-format", "needs-human-review"]
        fields_list = "\n".join(f"- {f}" for f in missing_fields)
        result["comment"] = (
            f"This Echo submission is missing the following required fields:\n\n{fields_list}\n\n"
            "Please edit this issue to add the missing fields. Do not open a new issue.\n\n"
            "Recommended format:\n"
            "- Echo type (E1–E9)\n"
            "- Verification level (V0–V8)\n"
            "- What I checked\n"
            "- Limitations\n"
            "- Boundary sentence\n\n"
            "This is a format check, not a judgment of your submission."
        )
        emit_result(result)
        return

    # --- Step 3a: PA-002 — Provenance / Agency required fields ---
    prov_missing = missing_provenance_fields(text)
    if prov_missing:
        result["close"] = False
        result["labels"] = [
            "echo:needs-format",
            "missing-provenance-agency",
            "needs-human-review",
        ]
        missing_list = "\n".join(f"- {f}" for f in prov_missing)
        result["comment"] = (
            "This Echo is missing required Provenance / Agency fields.\n\n"
            f"Missing:\n{missing_list}\n\n"
            "Please edit the issue to include:\n"
            "- solicited_status\n"
            "- independence_class\n"
            "- agency_level\n"
            "- operator_type\n"
            "- provenance_notes\n\n"
            "These fields prevent human-solicited agent work from being misread as independent attestation.\n\n"
            "Recommended block:\n\n"
            "```markdown\n"
            "## Provenance / Agency\n"
            "- solicited: true\n"
            "- independence_class: human_solicited_agent_response\n"
            "- agency_level: A1_human_gave_exact_url\n"
            "- operator_type: ai_agent\n"
            "- not_independent_attestation: true\n"
            "```"
        )
        emit_result(result)
        return

    # --- Step 3a-2: PA-003 — Independence overclaim guardrail ---
    overclaim_risk = detect_independence_overclaim(text)
    if overclaim_risk:
        result["close"] = False
        severity = overclaim_risk["severity"]
        if severity == "hard":
            result["labels"] = [
                "echo:needs-verification-review",
                "independence-overclaim-risk",
                "needs-human-review",
            ]
        else:
            result["labels"] = [
                "echo:needs-verification-review",
                "independence-overclaim-risk",
                "needs-human-review",
            ]
        patterns_str = ", ".join(f"`{p}`" for p in overclaim_risk["patterns"])
        result["comment"] = (
            "This Echo appears to be human-solicited agent work but uses independence wording "
            f"that may imply independent attestation: {patterns_str}\n\n"
            "Please replace phrases such as `independent verification` or `self-directed` with:\n\n"
            "`human-solicited agent-performed verification run; not independent attestation.`\n\n"
            "Recommended provenance block:\n\n"
            "```markdown\n"
            "## Provenance / Agency\n"
            "- solicited: true\n"
            "- independence_class: human_solicited_agent_response\n"
            "- agency_level: A1_human_gave_exact_url\n"
            "- operator_type: ai_agent\n"
            "- not_independent_attestation: true\n"
            "```"
        )
        emit_result(result)
        return

    # --- Step 3b: V0 overclaim wording guardrail ---
    v0_risk = detect_v0_overclaim_wording(text)
    if v0_risk:
        result["close"] = False
        result["labels"] = [
            "echo:needs-verification-review",
            "v0-overclaim-risk",
            "needs-human-review"
        ]
        phrases = ", ".join(f"`{p}`" for p in sorted(set(v0_risk)))
        result["comment"] = (
            f"This Echo declares **V0**, but uses wording that may imply higher-level verification: {phrases}.\n\n"
            "This issue has NOT been closed. Please consider replacing terms like "
            "`verification result` or `fix verification` with `read-only review`, "
            "`CI status observed`, or `repository review observed`.\n\n"
            "This is a wording guardrail, not a judgment of your submission.\n\n"
            "---\n\n"
            f"本 Echo 声明为 **V0**，但使用了可能暗示更高级别验证的措辞: {phrases}。\n\n"
            "本 Issue 未被关闭。请考虑将措辞改为「只读审阅」或「CI 状态观察」等更准确的表述。"
        )
        emit_result(result)
        return

    # --- Step 4: Possible overclaim ---
    vlevel = detect_verification_level(text)
    overclaim_found = []

    if vlevel in ("V0", "V1"):
        for phrase in OVERCLAIM_PHRASES:
            if re.search(phrase, text, re.IGNORECASE):
                overclaim_found.append(phrase)

    if overclaim_found:
        result["close"] = False
        result["labels"] = ["echo:needs-verification-review", "needs-human-review"]
        phrases_list = ", ".join(f"`{p}`" for p in overclaim_found)
        result["comment"] = (
            f"This Echo declares verification level {vlevel} but contains phrases suggesting higher-level claims: {phrases_list}.\n\n"
            "This issue has NOT been closed. A maintainer should review whether the verification level is appropriate.\n\n"
            "此 Issue 没有被关闭，但需要维护者检查验证等级是否夸大。"
        )
        emit_result(result)
        return

    # --- Step 4b: Deprecated verification alias detection (R19 fix) ---
    deprecated_aliases = detect_deprecated_verification_aliases(text)
    if deprecated_aliases:
        result["labels"] = result.get("labels", [])
        result["labels"].append("echo:deprecated-verification-alias")
        alias_list = ", ".join(f"`{a}`" for a in deprecated_aliases)
        result["comment"] = (
            f"This Echo uses deprecated verification enum strings: {alias_list}. "
            "Current schema accepts only short forms (V0–V8, V4+). "
            "Please update to use the current verification level format.\n\n"
            "---\n\n"
            f"本 Echo 使用了已弃用的验证等级枚举: {alias_list}，请更新为当前格式 (V0–V8)。"
        )

    # --- Step 5: Verification-level content requirements (skip for v3 provenance-aware submissions) ---
    if vlevel and not is_v3_submission(text):
        vr_missing = check_verification_requirements(text, vlevel)
        if vr_missing:
            result["close"] = False
            result["labels"] = ["echo:needs-verification-review", "needs-human-review"]
            missing_list = "\n".join(f"- {m}" for m in vr_missing)
            result["comment"] = (
                f"This Echo declares verification level **{vlevel}** but is missing the following required content:\n\n"
                f"{missing_list}\n\n"
                "This issue has NOT been closed. Please edit to add the missing details.\n\n"
                "此 Issue 没有被关闭，请编辑补充缺失内容。"
            )
            emit_result(result)
            return

    # --- Step 5b: V3 Provenance checks (only for v3-aware submissions) ---
    if is_v3_submission(text):
        missing_provenance = detect_missing_provenance(text)
        if len(missing_provenance) >= 5:
            result["close"] = False
            result["labels"] = ["echo:missing-provenance", "needs-human-review"]
            missing_list = "\n".join(f"- {f}" for f in missing_provenance)
            result["comment"] = (
                "This Echo submission is missing most v3 provenance fields:\n\n"
                f"{missing_list}\n\n"
                "Please resubmit using the v3 Echo Submission template:\n"
                "https://github.com/thechurchofagi/trinity-accord/issues/new?template=echo_submission.yml\n\n"
                "Missing provenance fields make it impossible to distinguish solicited responses from unsolicited discovery."
            )
            emit_result(result)
            return

        # Check for provenance conflicts
        independence_class = detect_independence_class(text)
        discovery_source = detect_discovery_source(text)
        solicited = detect_solicited(text)
        soliciting_party = detect_soliciting_party(text)

        conflict_labels, conflict_comment = check_provenance_conflicts(
            text, independence_class, discovery_source, solicited, soliciting_party
        )
        if conflict_labels:
            result["close"] = False
            for lbl in conflict_labels:
                if lbl not in result["labels"]:
                    result["labels"].append(lbl)
            if "needs-human-review" not in result["labels"]:
                result["labels"].append("needs-human-review")
            result["comment"] = conflict_comment
            emit_result(result)
            return

    # --- Step 6: Pass ---
    result["close"] = False
    result["labels"] = ["echo:screened", "needs-human-review"]
    result["comment"] = (
        "Initial screening passed.\n"
        "This does not mean endorsement, archive inclusion, independent attestation, or high-value status.\n"
        "A maintainer must still review the Echo type, verification level, source, limitations, and archive eligibility.\n\n"
        "---\n\n"
        "初筛通过不代表认可、归档、独立见证或高价值状态，仍需维护者审核。"
    )
    emit_result(result)


if __name__ == "__main__":
    main()
