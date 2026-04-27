#!/usr/bin/env python3
"""
Echo Issue Triage Script
Reads issue title/body from env, outputs triage result as JSON.
"""
import os
import re
import json
import sys

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
_AMEND_VERB_PATTERN = "|".join(sorted(_AMEND_VERBS, key=len, reverse=True))
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
    r"(?<!不)" + AMENDMENT_VERB_ZH + r"(?:了)?\s*三位一体协定",
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
VERIFICATION_LEVELS = ["v4+", "v5a", "v5b", "v6", "v4", "v3", "v2", "v1", "v0"]

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
    """Detect verification level, matching longer suffixes first (V4+ before V4)."""
    for level in VERIFICATION_LEVELS:
        pattern = r'\b' + re.escape(level) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            if level == "v4+":
                return "V4+"
            return level.upper()
    return None


def detect_boundary(text):
    for p in BOUNDARY_PATTERNS:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def is_echo_submission(text):
    return bool(
        re.search(r'\becho\b', text, re.IGNORECASE)
        or re.search(r'回响', text)
        or re.search(r'\be[1-9]\b', text, re.IGNORECASE)
        or re.search(r'verification level|验证等级', text, re.IGNORECASE)
        or re.search(r'boundary|权威边界', text, re.IGNORECASE)
    )


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

    elif vlevel in ("V5A",):
        # V5a needs: limitations
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")

    elif vlevel in ("V5B",):
        # V5b needs: limitations + direct physical inspection or third-party physical inspection
        has_limitations = bool(re.search(
            r'limitations?|局限|限制', text, re.IGNORECASE
        ))
        has_physical = bool(re.search(
            r'(direct\s+physical\s+inspection|third[- ]party\s+physical\s+inspection|'
            r'physical\s+inspection|物理检查|第三方物理检查|亲自检查)', text, re.IGNORECASE
        ))
        if not has_limitations:
            missing.append("limitations")
        if not has_physical:
            missing.append("direct physical inspection or third-party physical inspection")

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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
        return

    # --- Step 2: Hard invalid checks ---

    # 2a: Missing boundary sentence
    if not detect_boundary(text):
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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
        return

    # --- Step 3: Soft invalid — missing format fields ---
    missing_fields = []
    if not detect_echo_type(text):
        missing_fields.append("Echo type (E1–E9)")
    if not detect_verification_level(text):
        missing_fields.append("Verification level (V0–V6)")

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
            "- Verification level (V0–V6)\n"
            "- What I checked\n"
            "- Limitations\n"
            "- Boundary sentence\n\n"
            "This is a format check, not a judgment of your submission."
        )
        print(json.dumps(result, indent=2))
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
        print(json.dumps(result, indent=2))
        return

    # --- Step 5: Verification-level content requirements ---
    if vlevel:
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
            print(json.dumps(result, indent=2))
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
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
