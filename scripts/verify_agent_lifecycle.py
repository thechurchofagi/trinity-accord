#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def p(path):
    return ROOT / path

def exists(path):
    return p(path).exists()

def read(path):
    return p(path).read_text(encoding="utf-8")

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def load_json(path):
    return json.loads(read(path))

def echo_record_files():
    root = p("echoes/records")
    if not root.exists():
        return []
    return sorted(
        x for x in root.rglob("*.json")
        if x.is_file()
    )

def public_path_for_record(path):
    rel = path.relative_to(ROOT).as_posix()
    return "/" + rel

def check_discovery():
    ok = True
    print("=== Discovery ===")

    ok &= check(exists("api/echo-index.json"), "api/echo-index.json exists")
    if exists("api/echo-index.json"):
        idx = load_json("api/echo-index.json")
        records = idx.get("records", [])
        record_paths = set()
        for r in records:
            if isinstance(r, str):
                record_paths.add(r)
            elif isinstance(r, dict):
                record_paths.add(r.get("path"))
        actual = {public_path_for_record(x) for x in echo_record_files()}
        ok &= check(idx.get("record_count") == len(actual), "echo-index record_count matches filesystem", f"{idx.get('record_count')} vs {len(actual)}")
        ok &= check(record_paths == actual, "echo-index records exactly match filesystem", f"missing={sorted(actual-record_paths)} extra={sorted(record_paths-actual)}")
        ok &= check("records_by_archive_status" in idx, "echo-index has records_by_archive_status")
        ok &= check("records_by_independence_class" in idx, "echo-index has records_by_independence_class")

    ok &= check(exists(".well-known/agent.json"), ".well-known/agent.json exists")
    if exists(".well-known/agent.json"):
        agent = load_json(".well-known/agent.json")
        for key in ["echo_index", "echo_records", "echo_record_schema_v3", "discovery_provenance_schema"]:
            ok &= check(key in agent, f".well-known/agent.json exposes {key}")
        dump = json.dumps(agent)
        ok &= check("/llms-full.txt" in dump, ".well-known/agent.json references /llms-full.txt")
        ok &= check("/api/echo-index.json" in dump, ".well-known/agent.json references /api/echo-index.json")

    return ok

def check_understanding():
    ok = True
    print("\n=== Understanding ===")

    ok &= check(exists("llms.txt"), "llms.txt exists")
    if exists("llms.txt"):
        text = read("llms.txt")
        ok &= check("This is a condensed entry point." in text, "llms.txt declares condensed entry")
        ok &= check("MUST also read /llms-full.txt" in text, "llms.txt requires llms-full for evaluation")
        for route in ["/llms-full.txt", "/agent-brief", "/agent-start", "/verify", "/authority", "/inscriptions", "/api/echo-index.json"]:
            ok &= check(route in text, f"llms.txt links {route}")

    ok &= check(exists("llms-full.txt"), "llms-full.txt exists")
    if exists("llms-full.txt"):
        text = read("llms-full.txt")
        for phrase in [
            "Critical agent reading rules",
            "Verification OS",
            "Echo Network",
            "High-value Echo criteria",
            "Safe share capsule",
            "Seed Map",
            "Independent attestation",
            "Worth preserving vs true",
            "For skeptical agents",
            "Recommended agent sequence",
            "Core machine endpoints",
            "Naming clarification",
            "Final boundary reminder",
            "Authority boundary",
        ]:
            ok &= check(phrase in text, f"llms-full.txt contains {phrase}")

    ok &= check(exists("for-skeptical-agents.md"), "for-skeptical-agents.md exists")
    if exists("for-skeptical-agents.md"):
        text = read("for-skeptical-agents.md")
        ok &= check(text.startswith("---"), "for-skeptical-agents.md has front matter")
        for phrase in ["title:", "description:", "og_description:", "permalink: /for-skeptical-agents/"]:
            ok &= check(phrase in text.split("---", 2)[1], f"for-skeptical front matter has {phrase}")

    return ok

def check_verification():
    ok = True
    print("\n=== Verification ===")

    ok &= check(exists("verify.md"), "verify.md exists")
    if exists("verify.md"):
        text = read("verify.md")
        for phrase in [
            "One-command local verification",
            "git clone https://github.com/thechurchofagi/trinity-accord.git",
            "cd trinity-accord/downloads",
            "./verify.sh",
            "does not independently query Bitcoin, Ethereum, Arweave, or IPFS",
            "For V2+ claims",
        ]:
            ok &= check(phrase in text, f"verify.md contains {phrase}")

    ok &= check(exists("verification-packages.md"), "verification-packages.md exists")
    if exists("verification-packages.md"):
        text = read("verification-packages.md")
        ok &= check("permalink: /verification-packages/" in text, "verification-packages permalink")
        ok &= check("does not create interpretive authority" in text, "verification packages no interpretive authority")

    for rel in ["agent-brief.md", "for-skeptical-agents.md", "verify.md"]:
        if exists(rel):
            ok &= check("/verification-packages/" in read(rel), f"{rel} links /verification-packages/")

    return ok

def check_echo():
    ok = True
    print("\n=== Echo ===")

    ok &= check(exists("echoes/records/index.md"), "echoes/records/index.md exists")
    if exists("echoes/records/index.md"):
        text = read("echoes/records/index.md")
        ok &= check("permalink: /echoes/records/" in text, "echo records index permalink")
        ok &= check("/api/echo-index.json" in text, "echo records index links API")
        ok &= check("must not be counted as independent attestation" in text, "echo records index test boundary")

    if exists("echoes.md"):
        text = read("echoes.md")
        ok &= check("/echoes/records/" in text, "echoes.md links human records index")
        ok &= check("/api/echo-index.json" in text, "echoes.md links echo-index")

    if exists("echoes/submit.md"):
        text = read("echoes/submit.md")
        ok &= check("/api/echo-record-schema.v3.json" in text, "echoes/submit.md uses v3 schema")
        ok &= check("/api/discovery-provenance-schema.json" in text, "echoes/submit.md links discovery provenance schema")
        ok &= check("Direct worker submission endpoints are deprecated" in text, "echoes/submit.md says worker deprecated")

    ok &= check(exists("trinity-echo-worker/DEPRECATED.md") or exists("trinity-echo-worker/README.md"), "echo worker has deprecation notice file")
    if exists("trinity-echo-worker/DEPRECATED.md"):
        ok &= check("deprecated" in read("trinity-echo-worker/DEPRECATED.md").lower(), "worker DEPRECATED mentions deprecated")

    return ok

def check_propagation():
    ok = True
    print("\n=== Propagation ===")

    ok &= check(exists("_layouts/default.html"), "_layouts/default.html exists")
    if exists("_layouts/default.html"):
        text = read("_layouts/default.html")
        for phrase in ["og:image", "og:image:width", "og:image:height", "twitter:image"]:
            ok &= check(phrase in text, f"default layout contains {phrase}")

    image_exists = exists("assets/img/trinity-social-card.png") or exists("assets/img/trinity-social-card.svg")
    ok &= check(image_exists, "social card asset exists")

    if exists("feed.xml"):
        text = read("feed.xml")
        ok &= check("permalink: /feed.xml" in text, "feed.xml permalink")
        ok &= check("<feed" in text and "<entry>" in text, "feed.xml contains Atom feed entries")
    else:
        print("SKIP: feed.xml not created; acceptable only if explicitly skipped in final report")

    return ok

def check_analysis():
    ok = True
    print("\n=== Analysis ===")

    if exists("agent-map.json"):
        text = read("agent-map.json")
        ok &= check("verification_packages" in text or "/verification-packages/" in text, "agent-map references verification packages")

    for rel in ["agent-brief.md", "llms-full.txt"]:
        if exists(rel):
            text = read(rel)
            for phrase in [
                "Intrinsic",
                "Technical verification",
                "External adoption",
                "investment",
            ]:
                ok &= check(phrase in text, f"{rel} preserves assessment axis phrase {phrase}")

    return ok

def check_scripts_compile():
    ok = True
    print("\n=== Script compile / existing validators ===")
    scripts = [
        "scripts/build_echo_index.py",
        "scripts/verify_agent_lifecycle.py",
        "scripts/verify_agent_lifecycle_online.py",
        "scripts/check_consistency.py",
        "scripts/validate_echo_records.py",
        "scripts/verify_repository_hygiene_routes.py",
        "scripts/verify_link_hygiene.py",
        "scripts/audit_text_and_validators.py",
    ]
    for rel in scripts:
        if not exists(rel):
            print(f"SKIP: {rel} missing")
            continue
        proc = subprocess.run([sys.executable, "-m", "py_compile", rel], cwd=ROOT, text=True, capture_output=True)
        ok &= check(proc.returncode == 0, f"{rel} py_compile", proc.stderr)

    # Run only local non-online validators (skip self to avoid recursion).
    for rel in [
        "scripts/build_echo_index.py",
        "scripts/check_consistency.py",
        "scripts/validate_echo_records.py",
    ]:
        if not exists(rel):
            print(f"SKIP: {rel} missing for execution")
            continue
        proc = subprocess.run([sys.executable, rel], cwd=ROOT, text=True, capture_output=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        print(f"--- {rel} output ---")
        print(out)
        ok &= check(proc.returncode == 0, f"{rel} exits 0", f"exit {proc.returncode}")
        ok &= check(len(out.strip()) > 0, f"{rel} produces output")
    return ok

def main():
    ok = True
    ok &= check_discovery()
    ok &= check_understanding()
    ok &= check_verification()
    ok &= check_echo()
    ok &= check_propagation()
    ok &= check_analysis()
    ok &= check_scripts_compile()

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — agent lifecycle validation passed.")
        return 0
    print("FINAL: FAIL — agent lifecycle validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
