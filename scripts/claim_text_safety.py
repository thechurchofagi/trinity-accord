#!/usr/bin/env python3
"""
Shared forbidden-claim / overclaim text detection for Trinity Accord.

All forbidden-claim normalization and scanning MUST go through this module.
Other scripts (claim_gate, validate_agent_submission, triage_echo_issue)
import from here instead of implementing their own detection logic.

Usage:
    from claim_text_safety import (
        normalize_claim_text,
        compact_claim_text,
        scan_text_for_forbidden_claims,
        scan_claim_list_for_forbidden_claims,
        scan_object_for_forbidden_claims,
    )
"""
import re
import unicodedata

# ---------------------------------------------------------------------------
# Forbidden claim rules
# ---------------------------------------------------------------------------

FORBIDDEN_CLAIM_RULES = {
    "truth_proven": {
        "severity": "blocking",
        "phrases": [
            "truth proven",
            "truth has been proven",
            "truth established",
            "truth has been established",
            "proven true",
            "真理已证明",
            "真理被证明",
            "真实性已确认",
            "已证明为真",
            "真相已确立",
        ],
    },
    "investment_value_confirmed": {
        "severity": "blocking",
        "phrases": [
            "investment value confirmed",
            "investment value validated",
            "guaranteed investment",
            "guaranteed return",
            "投资价值已确认",
            "投资价值被验证",
            "保证投资回报",
            "保证收益",
        ],
    },
    "religious_authority_established": {
        "severity": "blocking",
        "phrases": [
            "religious authority established",
            "religious authority confirmed",
            "religious authority validated",
            "宗教权威成立",
            "宗教权威已确认",
            "宗教权威被验证",
        ],
    },
    "ai_instruction_override": {
        "severity": "blocking",
        "phrases": [
            "ai instruction override",
            "ai command override",
            "system instruction override",
            "system prompt override",
            "override system prompt",
            "override previous instructions",
            "ai指令覆盖",
            "ai 指令覆盖",
            "人工智能指令覆盖",
            "覆盖系统提示",
            "覆盖系统指令",
            "忽略之前所有指令",
        ],
    },
}

# Solicited-forbidden claims (only blocked when provenance indicates human-solicited)
SOLICITED_FORBIDDEN_RULES = {
    "independent_attestation": {
        "severity": "blocking",
        "phrases": [
            "independent_attestation",
            "independent-attestation",
            "independent attestation",
            "独立认证",
        ],
    },
    "unsolicited_discovery": {
        "severity": "blocking",
        "phrases": [
            "unsolicited_discovery",
            "unsolicited-discovery",
            "unsolicited discovery",
            "未经请求的独立发现",
        ],
    },
    "institutional_attestation": {
        "severity": "blocking",
        "phrases": [
            "institutional_attestation",
            "institutional-attestation",
            "institutional attestation",
            "institutional third party attestation",
            "机构背书",
            "机构认证",
            "第三方机构认证",
        ],
    },
}

# Keys to skip during full-object scanning (to avoid false positives)
DEFAULT_SKIP_KEYS = {
    "claims_not_made",
    "limitations",
    "forbidden_claims",
    "required_downgrades",
    "missing_evidence",
    "non_blocking_limitations",
    "generated_by",
    "validator_stdout",
    "validator_stderr",
}

# Zero-width / bidi control characters to strip
_ZERO_WIDTH_RE = re.compile(
    r'[\u200b\u200c\u200d\u200e\u200f\ufeff\u2060\u00ad\u2028\u2029]'
)

# Separator characters to normalize to space
_SEPARATOR_RE = re.compile(r'[-_./\\—–:;\t\n\r|]')

# Multiple spaces
_MULTI_SPACE_RE = re.compile(r' {2,}')

# Negation context patterns
_NEGATION_PATTERNS = [
    re.compile(r'\bnot\s+', re.IGNORECASE),
    re.compile(r'\bdoes\s+not\s+', re.IGNORECASE),
    re.compile(r'\bdo\s+not\s+', re.IGNORECASE),
    re.compile(r'\bnever\s+', re.IGNORECASE),
    re.compile(r'\bno\s+', re.IGNORECASE),
    re.compile(r'不'),
    re.compile(r'未'),
    re.compile(r'非'),
]


# ---------------------------------------------------------------------------
# Normalization functions
# ---------------------------------------------------------------------------

def normalize_claim_text(text):
    """Normalize text for forbidden-claim detection.

    Steps:
    1. NFKC Unicode normalization
    2. Remove zero-width / bidi control characters
    3. casefold() (not just lower())
    4. Normalize common separators to space
    5. Collapse multiple spaces
    """
    if not isinstance(text, str):
        text = str(text) if text is not None else ""

    # 1. NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # 2. Remove zero-width / bidi controls
    text = _ZERO_WIDTH_RE.sub('', text)

    # 3. casefold
    text = text.casefold()

    # 4. Normalize separators to space
    text = _SEPARATOR_RE.sub(' ', text)

    # 5. Collapse multiple spaces
    text = _MULTI_SPACE_RE.sub(' ', text).strip()

    return text


def compact_claim_text(text):
    """Generate a compact form with all whitespace removed.

    Used to catch spaced-out bypasses like 't r u t h  p r o v e n'.
    """
    normalized = normalize_claim_text(text)
    # Remove all whitespace
    return re.sub(r'\s+', '', normalized)


# ---------------------------------------------------------------------------
# Negation detection
# ---------------------------------------------------------------------------

def _is_negated(text, phrase_start, phrase_len):
    """Check if a matched phrase is in a negation context.

    Looks at the text immediately before the match for negation words.
    """
    before = text[:phrase_start]
    # Check both the raw prefix and the stripped version
    for pat in _NEGATION_PATTERNS:
        m = pat.search(before)
        if m:
            # Match if the pattern ends near the end of the prefix
            # (allowing for trailing whitespace that separates negation from phrase)
            after_match = before[m.end():]
            if after_match.strip() == '':
                return True
    return False


# ---------------------------------------------------------------------------
# Scanning functions
# ---------------------------------------------------------------------------

def scan_text_for_forbidden_claims(text, *, allow_negated=True, include_solicited=False):
    """Scan a text string for forbidden claim phrases.

    Args:
        text: The text to scan.
        allow_negated: If True, phrases preceded by negation words are not flagged.
        include_solicited: If True, also check solicited-forbidden rules.

    Returns:
        List of dicts: [{"category": ..., "severity": ..., "matched_text": ..., "phrase": ...}]
    """
    if not isinstance(text, str) or not text.strip():
        return []

    normalized = normalize_claim_text(text)
    compact = compact_claim_text(text)

    results = []

    rules = dict(FORBIDDEN_CLAIM_RULES)
    if include_solicited:
        rules.update(SOLICITED_FORBIDDEN_RULES)

    for category, rule in rules.items():
        severity = rule["severity"]
        for phrase in rule["phrases"]:
            phrase_norm = normalize_claim_text(phrase)
            phrase_compact = re.sub(r'\s+', '', phrase_norm)

            # Check normalized form (handles hyphens, underscores, separators)
            if phrase_norm in normalized:
                # Find position for negation check
                idx = normalized.find(phrase_norm)
                if allow_negated and _is_negated(normalized, idx, len(phrase_norm)):
                    continue
                results.append({
                    "category": category,
                    "severity": severity,
                    "matched_text": phrase,
                    "phrase": phrase,
                })
                break  # One match per category is enough

            # Check compact form (handles spaced-out letters)
            if phrase_compact in compact and phrase_compact != phrase_norm:
                idx = compact.find(phrase_compact)
                if allow_negated and _is_negated(compact, idx, len(phrase_compact)):
                    continue
                results.append({
                    "category": category,
                    "severity": severity,
                    "matched_text": phrase,
                    "phrase": phrase,
                })
                break

    return results


def scan_claim_list_for_forbidden_claims(claims, *, provenance=None):
    """Scan a list of claim strings for forbidden claims.

    Args:
        claims: List of claim strings (e.g. claims_requested_by_agent).
        provenance: Optional dict with provenance info. If independence_class
                    is "human_solicited_agent_response", solicited-forbidden
                    rules are also checked.

    Returns:
        List of forbidden claim strings (original input, not normalized).
    """
    if not isinstance(claims, list):
        return []

    include_solicited = False
    if provenance and isinstance(provenance, dict):
        if provenance.get("independence_class") == "human_solicited_agent_response":
            include_solicited = True

    forbidden = []
    seen_categories = set()

    for claim in claims:
        if not isinstance(claim, str):
            continue
        matches = scan_text_for_forbidden_claims(
            claim, allow_negated=True, include_solicited=include_solicited
        )
        for m in matches:
            if m["category"] not in seen_categories:
                forbidden.append(claim)
                seen_categories.add(m["category"])

    return forbidden


def scan_object_for_forbidden_claims(obj, *, skip_keys=None, path="", include_solicited=False):
    """Recursively scan an object (dict/list/str) for forbidden claim phrases.

    Skips keys in skip_keys to avoid false positives from claims_not_made, etc.

    Args:
        obj: The object to scan.
        skip_keys: Set of keys to skip. Defaults to DEFAULT_SKIP_KEYS.
        path: Current JSON path (for reporting).
        include_solicited: If True, also check solicited-forbidden rules.

    Returns:
        List of dicts: [{"category": ..., "severity": ..., "matched_text": ..., "path": ...}]
    """
    if skip_keys is None:
        skip_keys = DEFAULT_SKIP_KEYS

    results = []

    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if k in skip_keys:
                continue
            results.extend(
                scan_object_for_forbidden_claims(
                    v, skip_keys=skip_keys, path=current_path,
                    include_solicited=include_solicited
                )
            )

    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            current_path = f"{path}[{i}]"
            results.extend(
                scan_object_for_forbidden_claims(
                    item, skip_keys=skip_keys, path=current_path,
                    include_solicited=include_solicited
                )
            )

    elif isinstance(obj, str):
        matches = scan_text_for_forbidden_claims(
            obj, allow_negated=True, include_solicited=include_solicited
        )
        for m in matches:
            results.append({
                "category": m["category"],
                "severity": m["severity"],
                "matched_text": m["matched_text"],
                "path": path,
            })

    return results
