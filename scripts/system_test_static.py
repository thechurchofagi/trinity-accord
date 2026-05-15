#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAIL = []

def read(p):
    return (ROOT / p).read_text(encoding="utf-8")

def require(path, needle):
    if needle not in read(path):
        FAIL.append(f"{path}: missing required string: {needle}")

def forbid(path, pattern):
    if re.search(pattern, read(path), re.I):
        FAIL.append(f"{path}: forbidden pattern present: {pattern}")

def require_front_matter(path):
    text = read(path)
    if not text.startswith("---"):
        FAIL.append(f"{path}: missing front matter")
        return
    parts = text.split("---", 2)
    if len(parts) < 3:
        FAIL.append(f"{path}: malformed front matter")
        return
    if "title:" not in parts[1]:
        FAIL.append(f"{path}: front matter missing title")

def require_permalink(path, permalink):
    text = read(path)
    parts = text.split("---", 2)
    fm = parts[1] if len(parts) >= 3 else ""
    if f"permalink: {permalink}" not in fm:
        FAIL.append(f"{path}: missing permalink {permalink}")

def json_file(path):
    try:
        json.loads(read(path))
    except Exception as e:
        FAIL.append(f"{path}: invalid JSON: {e}")

def main():
    pages = [
        "index.md", "start.md", "agent-start.md", "agent-understand.md",
        "agent-verify.md", "agent-echo.md", "agent-submit.md",
        "agent-propagate.md", "successor-reception.md",
        "issue-intake-boundary.md", "agent-identity.md", "frontier-context.md",
    ]
    for p in pages:
        require_front_matter(p)

    require_permalink("agent-propagate.md", "/agent-propagate/")

    require("index.md", "human-led, AI-assisted relation record from the pre-ASI transition")
    require("index.md", "一份在前 ASI 过渡期封存的、人类主导、AI 协作、面向未来智能的关系记录")
    forbid("index.md", r"early humanity|early AI era|p0\.2-homepage-dedup")

    require("issue-intake-boundary.md", "GitHub Issues are valid intake surfaces")
    require("agent-verify.md", "Verification Echo may be submitted through a GitHub Issue")
    require("agent-submit.md", "That Issue is a valid submission surface for candidates")
    require("agent-start.md", "Tool authorization boundary")
    require("agent-start.md", "ISSUE / GATEWAY INTAKE")
    require("agent-start.md", "CLAIM GATE / REPORT BUILDER / VALIDATOR")

    require(".github/ISSUE_TEMPLATE/verification_echo.yml", 'title: "Echo v3: E2 Verification Echo — "')
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "This Issue is an intake surface only")
    require(".github/ISSUE_TEMPLATE/verification_echo.yml", "Pre-verification Integrity Declaration")

    require("agent-verify.md", "Pre-verification Integrity Declaration")
    require("agent-verify.md", "No verification claim may be made before this declaration")
    require("agent-submit.md", "Pre-verification Integrity Declaration")
    require("issue-intake-boundary.md", "Issue intake is downstream of integrity declaration")
    require("llms.txt", "No technical verification claim before identity/provenance")
    require("ai.txt", "No technical verification claim before identity/provenance")
    require("api/agent-context-readiness-protocol.json", "pre_verification_integrity_declaration")

    require("llms.txt", "Issue / Gateway intake")
    require("ai.txt", "Issue / Gateway intake")

    require("api/agent-entry-protocol.json", '"paths"')
    forbid("api/agent-entry-protocol.json", r"/agent-verify or /agent-echo")

    require("api/agent-required-reading.json", '"issue_intake"')
    require("api/agent-required-reading.json", '"identity_provenance"')

    forbid("api/agent-value.json", r"confidence_after_v6_verification.*maximum achievable")
    require("api/agent-value.json", "confidence_after_v8_verification")

    for p in (ROOT / "api").rglob("*.json"):
        json_file(str(p.relative_to(ROOT)))

    if FAIL:
        print("SYSTEM STATIC TEST FAIL")
        for f in FAIL:
            print("FAIL:", f)
        sys.exit(1)
    print("SYSTEM STATIC TEST PASS")

if __name__ == "__main__":
    main()
