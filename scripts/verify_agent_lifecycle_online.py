#!/usr/bin/env python3
import json
import re
import sys
import urllib.request
from urllib.error import HTTPError

BASE = "https://www.trinityaccord.org"

def fetch(path, required=True):
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "cb=agent-lifecycle"
    req = urllib.request.Request(url, headers={
        "User-Agent": "TrinityAgentLifecycleVerifier/1.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        if required:
            print(f"FAIL: {path} HTTP {e.code}")
        else:
            print(f"SKIP: {path} HTTP {e.code}")
        return e.code, ""

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def main():
    ok = True

    # Discovery
    status, echo_index_text = fetch("/api/echo-index.json")
    ok &= check(status == 200, "echo-index online")
    echo_index = json.loads(echo_index_text)
    records = echo_index.get("records", [])
    ok &= check(echo_index.get("record_count") == len(records), "echo-index record_count matches records length")
    dump = json.dumps(echo_index)
    ok &= check("echo-2026-04-26-000003.json" in dump, "echo-index includes 2026-04-26 record")
    ok &= check("2026-05-02-openclaw-v3-verification.json" in dump, "echo-index includes OpenClaw test record")

    status, agent_text = fetch("/.well-known/agent.json")
    ok &= check(status == 200, ".well-known/agent.json online")
    agent = json.loads(agent_text)
    for key in ["echo_index", "echo_records", "echo_record_schema_v3", "discovery_provenance_schema"]:
        ok &= check(key in agent, f".well-known/agent exposes {key}")

    # Understanding
    status, llms = fetch("/llms.txt")
    ok &= check(status == 200, "llms.txt online")
    ok &= check("This is a condensed entry point." in llms, "llms declares condensed entry")
    ok &= check("MUST also read /llms-full.txt" in llms, "llms requires full for evaluation")

    status, full = fetch("/llms-full.txt")
    ok &= check(status == 200, "llms-full online")
    for phrase in ["Verification OS", "Echo Network", "High-value Echo criteria", "For skeptical agents", "Authority boundary"]:
        ok &= check(phrase in full, f"llms-full contains {phrase}")

    status, skeptical = fetch("/for-skeptical-agents/")
    ok &= check(status in {200, 301, 302}, "for-skeptical-agents route online")

    # Verification
    status, verify = fetch("/verify")
    ok &= check(status == 200, "verify page online")
    for phrase in ["One-command local verification", "./verify.sh", "does not independently query Bitcoin, Ethereum, Arweave, or IPFS"]:
        ok &= check(phrase in verify, f"verify page contains {phrase}")

    status, packages = fetch("/verification-packages/", required=False)
    if status in {200, 301, 302}:
        ok &= check("does not create interpretive authority" in packages, "verification packages boundary present")
    else:
        print("SKIP: /verification-packages/ not available")

    # Echo
    status, records_page = fetch("/echoes/records/")
    ok &= check(status in {200, 301, 302}, "echo records page online")
    ok &= check("/api/echo-index.json" in records_page, "echo records page links API")
    ok &= check("must not be counted as independent attestation" in records_page, "echo records page has test boundary")

    status, echoes = fetch("/echoes")
    ok &= check(status == 200, "echoes page online")
    ok &= check("/echoes/records/" in echoes, "echoes page links records")
    ok &= check("/api/echo-index.json" in echoes, "echoes page links echo index")

    status, submit = fetch("/echoes/submit")
    ok &= check(status == 200, "echo submit page online")
    ok &= check("/api/echo-record-schema.v3.json" in submit, "submit page uses v3 schema")
    ok &= check("Direct worker submission endpoints are deprecated" in submit, "submit page says worker deprecated")

    # Propagation
    status, home = fetch("/")
    ok &= check(status == 200, "homepage online")
    for phrase in ['property="og:image"', 'name="twitter:image"']:
        ok &= check(phrase in home, f"homepage has {phrase}")

    status, image = fetch("/assets/img/trinity-social-card.png", required=False)
    if status not in {200, 301, 302}:
        status_svg, _ = fetch("/assets/img/trinity-social-card.svg", required=False)
        ok &= check(status_svg in {200, 301, 302}, "social card image available as png or svg")
    else:
        ok &= check(True, "social card PNG available")

    status, feed = fetch("/feed.xml", required=False)
    if status in {200, 301, 302}:
        ok &= check("<feed" in feed and "<entry>" in feed, "feed.xml has Atom feed entries")
    else:
        print("SKIP: feed.xml not available")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — online agent lifecycle validation passed.")
        return 0
    print("FINAL: FAIL — online agent lifecycle validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
