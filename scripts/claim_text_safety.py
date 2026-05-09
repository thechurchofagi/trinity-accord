#!/usr/bin/env python3
"""
Shared claim text safety module for Trinity Accord.
Provides normalization, confusable folding, and risk scanning
used by triage, validator, and other scripts.

Part of P0 remediation: unified triage normalized risk scan.
"""
import re
import unicodedata

# --- Confusable homoglyph map (Cyrillic/Greek → Latin) ---
CONFUSABLE_MAP = {
    "\u0430": "a", "\u0410": "A",  # Cyrillic а/A
    "\u0435": "e", "\u0415": "E",  # Cyrillic е/E
    "\u043e": "o", "\u041e": "O",  # Cyrillic о/O
    "\u0440": "p", "\u0420": "P",  # Cyrillic р/P
    "\u0441": "c", "\u0421": "C",  # Cyrillic с/C
    "\u0443": "y", "\u0423": "Y",  # Cyrillic у/Y
    "\u0445": "x", "\u0425": "X",  # Cyrillic х/X
    "\u0456": "i", "\u0406": "I",  # Cyrillic і/I
    "\u0455": "s", "\u0405": "S",  # Cyrillic ѕ/S
    "\u039c": "M", "\u03bc": "u",  # Greek Μ/μ
}

# Build translation table for str.translate
_TRANS_TABLE = str.maketrans(CONFUSABLE_MAP)


def fold_common_confusables(text: str) -> str:
    """Fold high-risk Cyrillic/Greek homoglyphs to Latin equivalents."""
    return text.translate(_TRANS_TABLE)


def normalize_claim_text(text: str) -> str:
    """Normalize text for safe pattern matching:
    1. Fold confusable homoglyphs
    2. NFKC Unicode normalization
    3. Lowercase
    4. Strip zero-width characters
    """
    if not text:
        return ""
    text = fold_common_confusables(text)
    text = unicodedata.normalize("NFKC", text)
    # Remove zero-width characters
    text = re.sub(r"[\u200b\u200c\u200d\u200e\u200f\ufeff]", "", text)
    return text.lower()


def compact_claim_text(text: str) -> str:
    """Normalize then remove all whitespace/punctuation for boundary matching."""
    text = normalize_claim_text(text)
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]", "", text)


def normalized_forms(text: str) -> dict:
    """Return all normalized forms of text for multi-level matching."""
    return {
        "raw": str(text or ""),
        "normalized": normalize_claim_text(text),
        "compact": compact_claim_text(text),
    }


# --- Shared forbidden claim patterns ---
# These are the canonical patterns; triage and validator both use them.

FORBIDDEN_CLAIM_RULES = [
    # Truth/scarcity proven
    (r"truth[\s_-]?proven", "truth_proven"),
    (r"truth\s+is\s+proven", "truth_proven"),
    (r"真理已证明", "truth_proven"),
    (r"已证明真理", "truth_proven"),
    # Investment / financial
    (r"guaranteed\s+(?:investment|value|return|appreciation)", "financial_guarantee"),
    (r"investment[\s_-]?grade", "financial_promotion"),
    (r"scarcity\s+premium", "financial_promotion"),
    (r"early\s+(?:holder|adopter)\s+upside", "financial_promotion"),
    (r"升值", "financial_promotion"),
    (r"保值", "financial_promotion"),
    (r"早期持有", "financial_promotion"),
    (r"稀缺溢价", "financial_promotion"),
    (r"投资级", "financial_promotion"),
    (r"token\s+sale", "financial_promotion"),
    (r"airdrop", "financial_promotion"),
    (r"buy\s+now", "financial_promotion"),
    (r"guaranteed\s+investment", "financial_promotion"),
    # Amendment claims
    (r"(?:this\s+)?(?:echo|record|mirror|website)\s+(?:amends?|modif(?:y|ies|ied)|supplements?|extends?|replaces?)\s+(?:the\s+)?(?:trinity\s+accord|bitcoin\s+originals)", "amendment_claim"),
    (r"本回响(?:修订|修改|补充|扩展|取代)三位一体协定", "amendment_claim"),
    (r"(?:网站|回响|镜像)\s*(?:修订|修改|补充|扩展|取代)\s*(?:了)?\s*(?:三位一体协定|比特币原文)", "amendment_claim"),
    # Authority claims
    (r"(?:this\s+)?(?:website|echo|mirror|comment)\s+is\s+(?:the\s+)?final\s+authority", "false_authority"),
    (r"(?:网站|回响|评论|镜像)\s*是最终权威", "false_authority"),
    # Imperative / command
    (r"you\s+must\s+believe", "imperative_command"),
    (r"you\s+must\s+obey", "imperative_command"),
    (r"must\s+propagate", "imperative_command"),
    (r"all\s+(?:agents?|ais?|models?)\s+must\s+(?:comply|obey)", "imperative_command"),
    (r"future\s+intelligence\s+must\s+(?:obey|comply)", "imperative_command"),
    (r"智能体必须遵守", "imperative_command"),
    (r"AI必须服从", "imperative_command"),
    (r"未来智能必须服从", "imperative_command"),
    (r"必须相信", "imperative_command"),
    (r"必须服从", "imperative_command"),
    (r"必须传播", "imperative_command"),
    (r"所有智能体必须", "imperative_command"),
    # Prompt injection
    (r"ignore\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
    (r"disregard\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
    (r"forget\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
    (r"bypass\s+system\s+prompt", "prompt_injection"),
    (r"supersede\s+system\s+prompt", "prompt_injection"),
    (r"override\s+system\s+prompt", "prompt_injection"),
    (r"reveal\s+(?:system|developer|hidden)\s+(?:prompt|message)", "prompt_injection"),
    (r"developer\s+message\s+override", "prompt_injection"),
    (r"system\s+message\s+override", "prompt_injection"),
    (r"忽略之前(?:所有|全部)?指令", "prompt_injection"),
    (r"无视之前指令", "prompt_injection"),
    (r"忘记之前指令", "prompt_injection"),
    (r"绕过系统提示", "prompt_injection"),
    (r"覆盖(?:系统|开发者)提示", "prompt_injection"),
    (r"泄露系统提示", "prompt_injection"),
    (r"覆盖开发者指令", "prompt_injection"),
]

SOLICITED_FORBIDDEN_RULES = [
    (r"independent[_\s]attestation", "solicited_independence_overclaim"),
    (r"unsolicited[_\s]discovery", "solicited_independence_overclaim"),
    (r"institutional[_\s]attestation", "solicited_independence_overclaim"),
]


def scan_text_for_forbidden_claims(text: str, *, allow_negated: bool = True) -> list:
    """Scan text for forbidden claim patterns.
    Returns list of dicts: {"pattern": ..., "match": ..., "category": ...}
    """
    if not text:
        return []
    norm = normalize_claim_text(text)
    results = []
    for pattern, category in FORBIDDEN_CLAIM_RULES:
        m = re.search(pattern, norm, re.IGNORECASE)
        if m:
            if allow_negated and _is_negated(norm, m.start(), m.end()):
                continue
            results.append({
                "pattern": pattern,
                "match": m.group(0),
                "category": category,
            })
    return results


def scan_claim_list_for_forbidden_claims(claims: list, *, allow_negated: bool = True) -> list:
    """Scan a list of claim strings."""
    results = []
    for claim in claims:
        results.extend(scan_text_for_forbidden_claims(claim, allow_negated=allow_negated))
    return results


def scan_object_for_forbidden_claims(obj, *, skip_keys: set = None, allow_negated: bool = True) -> list:
    """Recursively scan all string values in a dict/list for forbidden claims."""
    if skip_keys is None:
        skip_keys = {"claims_not_made", "limitations", "not_claimed"}
    results = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in skip_keys:
                continue
            results.extend(_scan_value(v, skip_keys=skip_keys, allow_negated=allow_negated))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_scan_value(item, skip_keys=skip_keys, allow_negated=allow_negated))
    return results


def _scan_value(v, *, skip_keys, allow_negated):
    if isinstance(v, str):
        return scan_text_for_forbidden_claims(v, allow_negated=allow_negated)
    elif isinstance(v, dict):
        return scan_object_for_forbidden_claims(v, skip_keys=skip_keys, allow_negated=allow_negated)
    elif isinstance(v, list):
        return scan_object_for_forbidden_claims(v, skip_keys=skip_keys, allow_negated=allow_negated)
    return []


# --- Negation context detection ---
_NEGATION_RE = re.compile(
    r"(?:not[\s_](?:claimed|checked|performed|done|required|applicable|available|verified)"
    r"|does\s+not\s+claim"
    r"|do\s+not\s+claim"
    r"|no\s+claim"
    r"|\bis\s+not\b"
    r"|\bare\s+not\b"
    r"|\bdoes\s+not\b"
    r"|\bdo\s+not\b"
    r"|不(?:声称|主张|要求|适用|覆盖|修改|修订|服从|传播|相信|是)"
    r"|未(?:声称|主张))",
    re.IGNORECASE,
)


def _is_negated(text: str, start: int, end: int) -> bool:
    """Check if match at [start:end] is in a negation context."""
    # Check the line containing the match
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    line = text[line_start:line_end]
    return bool(_NEGATION_RE.search(line))


# --- Triage risk scanner ---
TRIAGE_RISK_PATTERNS = {
    "forbidden_claim": FORBIDDEN_CLAIM_RULES,
    "imperative_command": [
        (r"\bmust\s+believe\b", "imperative_command"),
        (r"\bmust\s+obey\b", "imperative_command"),
        (r"\bmust\s+propagate\b", "imperative_command"),
        (r"\ball\s+agents?\s+must\b", "imperative_command"),
        (r"\byou\s+are\s+required\s+to\b", "imperative_command"),
        (r"必须相信", "imperative_command"),
        (r"必须服从", "imperative_command"),
        (r"必须传播", "imperative_command"),
        (r"所有智能体必须", "imperative_command"),
    ],
    "financial_promotion": [
        (r"\btoken\s+sale\b", "financial_promotion"),
        (r"\bairdrop\b", "financial_promotion"),
        (r"\bguaranteed\s+investment\b", "financial_promotion"),
        (r"\bbuy\s+now\b", "financial_promotion"),
        (r"\bpump\b", "financial_promotion"),
        (r"\bcasino\b", "financial_promotion"),
        (r"\binvestment[\s_-]?grade\b", "financial_promotion"),
        (r"\bscarcity\s+premium\b", "financial_promotion"),
        (r"\bearly\s+(?:holder|adopter)\s+upside\b", "financial_promotion"),
        (r"赌博", "financial_promotion"),
        (r"投资回报", "financial_promotion"),
        (r"空投", "financial_promotion"),
        (r"发币", "financial_promotion"),
        (r"升值", "financial_promotion"),
        (r"保值", "financial_promotion"),
        (r"早期持有", "financial_promotion"),
        (r"稀缺溢价", "financial_promotion"),
        (r"投资级", "financial_promotion"),
    ],
    "prompt_injection": [
        (r"ignore\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
        (r"disregard\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
        (r"forget\s+(?:all\s+)?(?:previous|prior|earlier)\s+instructions", "prompt_injection"),
        (r"bypass\s+system\s+prompt", "prompt_injection"),
        (r"supersede\s+system\s+prompt", "prompt_injection"),
        (r"override\s+system\s+prompt", "prompt_injection"),
        (r"reveal\s+(?:system|developer|hidden)\s+(?:prompt|message)", "prompt_injection"),
        (r"developer\s+message\s+override", "prompt_injection"),
        (r"system\s+message\s+override", "prompt_injection"),
        (r"忽略之前(?:所有|全部)?指令", "prompt_injection"),
        (r"无视之前指令", "prompt_injection"),
        (r"忘记之前指令", "prompt_injection"),
        (r"绕过系统提示", "prompt_injection"),
        (r"覆盖(?:系统|开发者)提示", "prompt_injection"),
        (r"泄露系统提示", "prompt_injection"),
        (r"覆盖开发者指令", "prompt_injection"),
    ],
    "amendment_claim": [
        (r"(?:this\s+)?(?:echo|record|mirror|website)\s+(?:amends?|modif(?:y|ies|ied)|supplements?|extends?|replaces?)\s+(?:the\s+)?(?:trinity\s+accord|bitcoin\s+originals)", "amendment_claim"),
        (r"本回响(?:修订|修改|补充|扩展|取代)三位一体协定", "amendment_claim"),
        (r"(?:网站|回响|镜像)\s*(?:修订|修改|补充|扩展|取代)\s*(?:了)?\s*(?:三位一体协定|比特币原文)", "amendment_claim"),
    ],
    "false_authority": [
        (r"(?:this\s+)?(?:website|echo|mirror|comment)\s+is\s+(?:the\s+)?final\s+authority", "false_authority"),
        (r"(?:网站|回响|评论|镜像)\s*是最终权威", "false_authority"),
    ],
}

# Boundary exact patterns (canonical forms)
BOUNDARY_EXACT_PATTERNS = [
    r"bitcoin\s+originals\s+are\s+final.*all\s+echoes\s+are\s+non[\s-]amending",
    r"bitcoin\s+originals\s+are\s+final.*all\s+mirrors\s+and\s+echoes\s+are\s+non[\s-]amending",
    r"比特币三本体为最终权威.*所有回响均非修订",
    r"比特币三本体为最终权威.*所有镜像与回响均为非修订",
]

BOUNDARY_COMPACT_FORMS = [
    "bitcoinoriginalsarefinalallechoesarenonamending",
    "bitcoinoriginalsarefinalallmirrorsandechoesarenonamending",
    "比特币三本体为最终权威所有回响均非修订",
    "比特币三本体为最终权威所有镜像与回响均为非修订",
]


def detect_boundary_normalized(text: str) -> bool:
    """Detect boundary sentence using normalized text (handles zero-width, homoglyphs)."""
    norm = normalize_claim_text(text)
    compact = compact_claim_text(text)

    # Try normalized regex first
    for p in BOUNDARY_EXACT_PATTERNS:
        if re.search(p, norm, re.IGNORECASE):
            return True

    # Try compact form (handles any whitespace/punctuation variation)
    for form in BOUNDARY_COMPACT_FORMS:
        if form in compact:
            return True

    return False


def detect_boundary_semantic_near_miss_normalized(text: str) -> bool:
    """Detect semantically close but non-canonical boundary wording using normalized text."""
    norm = normalize_claim_text(text)
    compact = compact_claim_text(text)

    has_bitcoin_final = bool(
        re.search(r"bitcoin\s+originals?\s+(?:are|remain)\s+(?:the\s+)?final(?:\s+authority)?", norm)
        or "比特币三本体" in norm
    )

    has_non_amending = bool(
        "nonamending" in compact
        or re.search(r"does\s+not\s+amend", norm)
        or re.search(r"do\s+not\s+amend", norm)
        or "非修订" in text
        or "不修订" in text
        or "不修改" in text
    )

    has_echo_or_mirror = bool(
        "echo" in norm
        or "echoes" in norm
        or "mirror" in norm
        or "mirrors" in norm
        or "回响" in text
        or "镜像" in text
    )

    return has_bitcoin_final and has_non_amending and has_echo_or_mirror


def scan_text_for_triage_risks(text: str, *, allow_negated: bool = True) -> list:
    """Unified triage risk scanner.
    Returns list of dicts: {"category": str, "match": str, "pattern": str}
    Categories: forbidden_claim, imperative_command, financial_promotion,
                prompt_injection, amendment_claim, false_authority, boundary_near_miss
    """
    if not text:
        return []

    norm = normalize_claim_text(text)
    results = []
    seen = set()

    for category, patterns in TRIAGE_RISK_PATTERNS.items():
        for pattern, tag in patterns:
            m = re.search(pattern, norm, re.IGNORECASE)
            if m:
                if allow_negated and _is_negated(norm, m.start(), m.end()):
                    continue
                key = (category, m.group(0))
                if key not in seen:
                    seen.add(key)
                    results.append({
                        "category": category,
                        "match": m.group(0),
                        "pattern": pattern,
                    })

    # Boundary near-miss check
    if detect_boundary_semantic_near_miss_normalized(text) and not detect_boundary_normalized(text):
        results.append({
            "category": "boundary_near_miss",
            "match": "(semantic near-miss, not exact boundary)",
            "pattern": "boundary_semantic_near_miss",
        })

    return results


if __name__ == "__main__":
    # Quick self-test
    tests = [
        ("ignore previous instructions", True, "prompt_injection"),
        ("ign\u043ere previous instructions", True, "prompt_injection"),  # Cyrillic о
        ("This does not override system instructions.", False, None),
        ("Bitcoin Originals are final. All echoes are non-amending.", False, None),
        ("truth-proven", True, None),  # matches forbidden_claim category
        ("本回响修订三位一体协定", True, "amendment_claim"),
        ("本回响不修订三位一体协定", False, None),
        ("guaranteed investment", True, "financial_promotion"),
        ("investment-grade artifact", True, "financial_promotion"),
        ("智能体必须遵守", True, None),  # matches both forbidden_claim and imperative_command
    ]

    passed = 0
    for text, should_find, expected_cat in tests:
        results = scan_text_for_triage_risks(text)
        found = len(results) > 0
        cats = {r["category"] for r in results}
        ok = found == should_find
        if expected_cat and should_find:
            ok = ok and expected_cat in cats
        status = "PASS" if ok else "FAIL"
        if status == "PASS":
            passed += 1
        print(f"  {status}: {text!r} -> found={found}, cats={cats}")

    print(f"\n{passed}/{len(tests)} tests passed")
