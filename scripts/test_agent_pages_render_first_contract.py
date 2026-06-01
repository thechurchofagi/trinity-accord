#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGE_CANDIDATES = [
    "index.md",
    "agent-first-contact.md",
    "agent-first-contact/index.md",
    "agent-start.md",
    "agent-start/index.md",
    "llms.txt",
    "ai.txt",
]

REQUIRED_CURRENT_TERMS = [
    "record-chain",
    "Record-Chain Intake Gateway",
    "/record-chain/preflight",
    "/record-chain/submit",
]

OLD_GATEWAY_TERMS = [
    "/gateway/preflight",
    "/agent-submit",
    "/api/route-selector.v1.json",
    "/api/gateway-runtime-contract.v1.json",
    "/external-agent-copy-paste-examples/",
    "external-agent-copy-paste-examples",
    "Gateway v1",
]

# These words make an old Gateway mention acceptable.
# They indicate historical / negative / retired context.
ALLOW_CONTEXT_RE = re.compile(
    r"\b("
    r"do\s+not|don't|must\s+not|should\s+not|no\s+longer|"
    r"retired|historical|history|legacy|archive|archived|"
    r"replacement|replaced|old|previous|formerly|"
    r"not\s+active|not\s+current|not\s+primary|"
    r"deprecated|retire|retirement"
    r")\b",
    re.IGNORECASE,
)

# These words make an old Gateway mention suspicious if nearby.
# They indicate positive current instructions.
FORBID_CONTEXT_RE = re.compile(
    r"\b("
    r"primary|current|only|submit|submission|use|start|ready|"
    r"post|curl|download|generate|preflight|send|create|"
    r"recommended|required|must\s+use|should\s+use"
    r")\b",
    re.IGNORECASE,
)

# Old terms inside fenced code are allowed only if the surrounding block is
# clearly marked retired/historical/legacy. Otherwise they are suspicious.
FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def strip_allowed_historical_sections(text: str) -> str:
    """
    Remove sections that are clearly historical/legacy archive sections.
    This avoids false positives where pages correctly document old Gateway v1.
    Handles both markdown headings and HTML <details> blocks with legacy markers.
    """
    lines = text.splitlines()
    kept: list[str] = []
    skipping = False
    skip_level = None
    in_details_legacy = False

    heading_re = re.compile(r"^(#{1,6})\s+(.*)$")
    details_re = re.compile(r"<details", re.IGNORECASE)
    details_end_re = re.compile(r"</details>", re.IGNORECASE)
    legacy_marker_re = re.compile(
        r"legacy|historical|history|archive|retired|deprecated", re.IGNORECASE
    )

    for line in lines:
        # Handle <details> blocks with legacy markers in summary
        if details_re.search(line) or (in_details_legacy is False and "<details" in line.lower()):
            # Look ahead for legacy marker in summary
            in_details_legacy = False  # will be set if summary has legacy
        if "<summary>" in line.lower() and legacy_marker_re.search(line):
            in_details_legacy = True
        if in_details_legacy:
            kept.append("")  # blank line instead of content
            if details_end_re.search(line):
                in_details_legacy = False
            continue

        # Handle markdown heading sections
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).lower()

            if skipping and skip_level is not None and level <= skip_level:
                skipping = False
                skip_level = None

            if any(word in title for word in ["historical", "history", "legacy", "archive", "retired"]):
                skipping = True
                skip_level = level
                continue

        if not skipping:
            kept.append(line)

    return "\n".join(kept)


def context_window(text: str, start: int, end: int, radius: int = 220) -> str:
    return text[max(0, start - radius): min(len(text), end + radius)]


def check_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    # Required current path terms should appear somewhere in main agent-facing pages.
    if path.name in {"index.md", "agent-start.md", "llms.txt", "ai.txt"}:
        missing = [term for term in REQUIRED_CURRENT_TERMS if term not in text]
        if missing:
            fail(f"{path}: missing current Render-first terms: {missing}")

    main_text = strip_allowed_historical_sections(text)

    for term in OLD_GATEWAY_TERMS:
        for m in re.finditer(re.escape(term), main_text, re.IGNORECASE):
            window = context_window(main_text, m.start(), m.end())

            allowed = ALLOW_CONTEXT_RE.search(window) is not None
            forbidden = FORBID_CONTEXT_RE.search(window) is not None

            # If it is clearly negative/historical, allow it.
            if allowed:
                continue

            # If it is near positive instruction language, fail.
            if forbidden:
                fail(
                    f"{path}: old Gateway term appears in active instruction context: {term!r}\n"
                    f"Context:\n{window}"
                )

            # Neutral mentions in main sections are still suspicious.
            fail(
                f"{path}: old Gateway term appears outside historical/retired context: {term!r}\n"
                f"Context:\n{window}"
            )


def main() -> int:
    found = False
    for rel in PAGE_CANDIDATES:
        path = ROOT / rel
        if path.exists():
            found = True
            check_page(path)

    if not found:
        fail("No agent-facing pages found to test")

    print("PASS: agent pages are Render-first; old Gateway mentions are only historical/negative")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
