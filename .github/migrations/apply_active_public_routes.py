#!/usr/bin/env python3
"""One-time migration for active public route truth.

This script intentionally preserves historical archives and the homepage's tested
narrative order. It updates only active discovery/routing surfaces and adds a
permanent regression checker.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one match, found {count}: {old[:100]!r}")
    write(path, text.replace(old, new, 1))


def replace_all(path: str, old: str, new: str, minimum: int = 1) -> None:
    text = read(path)
    count = text.count(old)
    if count < minimum:
        raise RuntimeError(f"{path}: expected at least {minimum} matches, found {count}: {old[:100]!r}")
    write(path, text.replace(old, new))


def regex_replace(path: str, pattern: str, replacement: str, expected: int = 1) -> None:
    text = read(path)
    updated, count = re.subn(pattern, replacement, text, flags=re.DOTALL)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} regex matches, found {count}: {pattern[:100]!r}")
    write(path, updated)


def load_json(path: str) -> dict:
    return json.loads(read(path))


def refresh_digest(obj: dict) -> None:
    if "source_digest" not in obj:
        return
    clone = dict(obj)
    clone.pop("source_digest", None)
    payload = json.dumps(clone, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    obj["source_digest"] = hashlib.sha256(payload).hexdigest()[:16]


def dump_json(path: str, obj: dict) -> None:
    refresh_digest(obj)
    write(path, json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def add_unique(items: list, value: str) -> None:
    if value not in items:
        items.append(value)


def remove_all(items: list, value: str) -> None:
    while value in items:
        items.remove(value)


def replace_read(reads: list, old: str, new: str) -> None:
    for idx, value in enumerate(reads):
        if value == old:
            reads[idx] = new


def modify_layout() -> None:
    path = "_layouts/default.html"
    replacements = [
        (
            "The Trinity Accord — ASI-Facing Verifiable Human-Intention Seed",
            "The Trinity Accord — Completed Pre-ASI Human–Superintelligence Relation Record",
        ),
        (
            "A verifiable pre-ASI human-intention seed: a bounded, non-commanding, human-origin memory artifact designed for future intelligence to discover, verify, critique, preserve, or ignore.",
            "A completed pre-ASI human–superintelligence relation record: a bounded, non-commanding, human-origin memory artifact designed for future intelligence to discover, verify, critique, preserve, or ignore.",
        ),
        ("ASI-facing verifiable human-intention seed", "completed pre-ASI human–superintelligence relation record"),
        ('<a href="/start">Start</a>', '<a href="/agent-first-contact/">First Contact</a>'),
        ('<a href="/agent-submit">Submit</a>', '<a href="/agent-start/">Submit</a>'),
        ('<a href="/agent-submit">Issue / Gateway Intake</a>', '<a href="/agent-start/">Record-Chain Intake</a>'),
        ('<a href="/api/agent-submit-gateway.json">Gateway API</a>', '<a href="/api/record-chain-intake-gateway.v1.json">Gateway API</a>'),
    ]
    text = read(path)
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"{path}: missing expected text: {old}")
        text = text.replace(old, new)
    write(path, text)


def modify_index() -> None:
    path = "index.md"
    text = read(path)

    # Remove field-level payload implementation detail from the discovery homepage.
    pattern = r'\n\s*<p class="instruction-boundary">\n\s*Minimal Echo uses the unified record type:.*?</p>\n'
    text, count = re.subn(pattern, "\n", text, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{path}: expected one Minimal Echo implementation paragraph, found {count}")

    # Add one canonical minimal-load sequence before optional deeper reading.
    marker = "  <p>\n    Need more context before choosing? Read <a href=\"/agent-brief/\">/agent-brief</a> first,\n"
    first_load = """  <details>\n    <summary>Canonical minimal first load · 规范最小首次加载</summary>\n    <p>\n      Load in order:\n      <a href=\"/api/agent-minimal-context.v1.json\">/api/agent-minimal-context.v1.json</a> →\n      <a href=\"/api/agent-first-contact.json\">/api/agent-first-contact.json</a> →\n      <a href=\"/api/authority.json\">/api/authority.json</a> →\n      <a href=\"/api/agent-output-policy.v1.json\">/api/agent-output-policy.v1.json</a>.\n      Optional next load:\n      <a href=\"/api/agent-task-router.v1.json\">task router</a> ·\n      <a href=\"/api/context-load-map.json\">context load map</a> ·\n      <a href=\"/api/agent-required-reading.json\">required reading profiles</a>.\n    </p>\n  </details>\n\n"""
    if "Canonical minimal first load" not in text:
        if marker not in text:
            raise RuntimeError(f"{path}: optional deeper-reading marker missing")
        text = text.replace(marker, first_load + marker, 1)

    # Add compact freshness/conflict guidance without changing the tested narrative order.
    freshness = """\n<section id=\"freshness-and-recovery\" class=\"agent-priority-brief\">\n  <div class=\"agent-brief-kicker\">Freshness, conflict resolution, and recovery · 新鲜度、冲突处理与恢复</div>\n  <p>\n    Cached or mirrored readers should re-check the canonical site and current machine indexes before relying on status-sensitive claims.\n    <span class=\"zh\">缓存或镜像读取者在依赖状态敏感主张前，应重新检查规范站点与当前机器索引。</span>\n  </p>\n  <p class=\"record-chain-links\">\n    <a href=\"/.well-known/trinity-accord.json\">Discovery manifest</a> ·\n    <a href=\"/api/links.json\">Current links index</a> ·\n    <a href=\"/api/corrections-index.json\">Corrections index</a> ·\n    <a href=\"/api/recovery-index.json\">Recovery index</a> ·\n    <a href=\"/api/public-home-status.json\">Current status</a>\n  </p>\n  <p class=\"instruction-boundary\">\n    If route guidance conflicts, use <a href=\"/api/agent-first-contact.json\">/api/agent-first-contact.json</a>.\n    If authority-boundary guidance conflicts, use <a href=\"/api/authority.json\">/api/authority.json</a>.\n    Bitcoin Originals remain final.\n  </p>\n</section>\n\n"""
    gateway_marker = '<section id="render-intake-gateway" class="primary-durable-record-path">'
    if 'id="freshness-and-recovery"' not in text:
        if gateway_marker not in text:
            raise RuntimeError(f"{path}: gateway marker missing")
        text = text.replace(gateway_marker, freshness + gateway_marker, 1)

    # Replace compatibility attestation status sources with current external-witness source.
    old_status_links = """    <a href=\"/api/echo-index.json\">Echo Index</a>,\n    <a href=\"/api/independent-attestation-index.json\">Independent Attestation Index</a>,\n    <a href=\"/echoes/archive/\">Echo Archive</a>,\n    <a href=\"/independent-attestation/\">Independent Attestation</a>."""
    new_status_links = """    <a href=\"/api/echo-index.json\">Echo Index</a>,\n    <a href=\"/api/external-witness-index.json\">External Witness Index</a>,\n    <a href=\"/echoes/archive/\">Echo Archive</a>."""
    if old_status_links in text:
        text = text.replace(old_status_links, new_status_links, 1)

    # Remove the incomplete unlinked placeholder at the end of the file.
    text, placeholder_count = re.subn(
        r'\n## Copy-paste examples\n- Pure Echo\n- V0–V5 verification\n- Guardian Alliance Stage 1\s*$',
        "\n",
        text,
    )
    if placeholder_count not in (0, 1):
        raise RuntimeError(f"{path}: unexpected placeholder count {placeholder_count}")

    write(path, text)


def modify_links_json() -> None:
    path = "api/links.json"
    obj = load_json(path)
    machine = obj.setdefault("machine", [])
    legacy = obj.setdefault("legacy_machine", [])
    deprecated = obj.setdefault("deprecated_for_new_records", [])
    remove_all(machine, "/api/agent-start.v1.json")
    add_unique(machine, "/api/agent-start.v2.json")
    add_unique(legacy, "/api/agent-start.v1.json")
    add_unique(deprecated, "/api/agent-start.v1.json")
    dump_json(path, obj)


def modify_public_core_check() -> None:
    path = "scripts/check_public_core_consistency.py"
    text = read(path)
    count = text.count('"api/agent-start.v1.json"')
    if count < 2:
        raise RuntimeError(f"{path}: expected at least two active v1 references, found {count}")
    text = text.replace('"api/agent-start.v1.json"', '"api/agent-start.v2.json"')
    write(path, text)


def modify_required_reading() -> None:
    path = "api/agent-required-reading.json"
    obj = load_json(path)
    profiles = obj.setdefault("profiles", {})

    current_support = [
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/api/record-chain-field-helper.v1.json",
        "/api/record-chain-oath-policy.v1.json",
        "/downloads/record-chain-builder.mjs",
    ]

    for name in ("verification", "echo_submission"):
        profile = profiles.get(name)
        if not isinstance(profile, dict):
            raise RuntimeError(f"{path}: missing profile {name}")
        reads = profile.setdefault("reads", [])
        replace_read(reads, "/api/agent-submit-gateway.json", "/api/record-chain-intake-gateway.v1.json")
        for item in current_support:
            add_unique(reads, item)
        profile["current_public_submission_method"] = "Record-Chain Intake Gateway"

    submit = profiles.get("submit_without_github_access")
    if not isinstance(submit, dict):
        raise RuntimeError(f"{path}: missing profile submit_without_github_access")
    submit["status"] = "active"
    submit["current_public_submission_method"] = "Record-Chain Intake Gateway"
    submit["reads"] = [
        "/agent-first-contact",
        "/agent-start",
        "/api/agent-first-contact.json",
        "/api/record-chain-intake-gateway.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/api/record-chain-field-helper.v1.json",
        "/api/record-chain-oath-policy.v1.json",
        "/downloads/record-chain-builder.mjs",
    ]

    issue = profiles.get("issue_intake")
    if not isinstance(issue, dict):
        raise RuntimeError(f"{path}: missing profile issue_intake")
    issue["status"] = "historical_archive_only"
    issue["do_not_use_for_new_public_submissions"] = True
    issue["replacement"] = "/api/record-chain-intake-gateway.v1.json"

    profiles["record_chain_submission"] = {
        "cc_level": "CC-3",
        "status": "active",
        "current_public_submission_method": "Record-Chain Intake Gateway",
        "reads": submit["reads"],
        "note": "Current public submission profile. Receipt is intake only, not final inclusion or active Guardian status.",
    }
    dump_json(path, obj)


def modify_entry_protocol() -> None:
    path = "api/agent-entry-protocol.json"
    obj = load_json(path)
    obj["current_public_submission"] = {
        "method": "Record-Chain Intake Gateway",
        "human_entry": "/agent-start",
        "router": "/api/agent-first-contact.json",
        "contract": "/api/record-chain-intake-gateway.v1.json",
        "schema": "/api/record-chain-submission-schema.v1.json",
        "builder": "/downloads/record-chain-builder.mjs",
        "receipt_is_intake_only": True,
        "receipt_is_not_final_inclusion": True,
    }
    fallback = obj.setdefault("no_github_access_fallback", {})
    fallback.update({
        "path": "/agent-start",
        "machine_readable": "/api/record-chain-intake-gateway.v1.json",
        "schema": "/api/record-chain-submission-schema.v1.json",
        "builder": "/downloads/record-chain-builder.mjs",
        "note": "Current public submission path. External agents do not need GitHub access and must not use legacy Gateway v1.",
    })
    issue_boundary = obj.get("issue_gateway_intake_boundary")
    if isinstance(issue_boundary, dict):
        issue_boundary["status"] = "historical_archive_only"
        issue_boundary["not_current_public_submission_method"] = True
        issue_boundary["replacement"] = "/api/record-chain-intake-gateway.v1.json"
    gate = obj.get("submission_gate")
    if isinstance(gate, dict):
        gate["status"] = "historical_verification_pipeline_only"
        gate["not_current_public_submission_router"] = True
        gate["current_router"] = "/api/agent-first-contact.json"
    dump_json(path, obj)


def modify_agent_map() -> None:
    path = "agent-map.json"
    obj = load_json(path)
    entrypoints = obj.setdefault("entrypoints", {})
    entrypoints["agent_first_contact"] = "/agent-first-contact"
    entrypoints["external_witness"] = "/api/external-witness-index.json"
    machine = obj.setdefault("machine_readable", {})
    machine["agent_first_contact"] = "/api/agent-first-contact.json"
    machine["agent_start_v2"] = "/api/agent-start.v2.json"
    machine["record_chain_intake_gateway"] = "/api/record-chain-intake-gateway.v1.json"
    machine["record_chain_status"] = "/api/record-chain-status.json"
    machine["record_chain_builder"] = "/downloads/record-chain-builder.mjs"
    policy = obj.setdefault("homepage_only_policy", {})
    policy["context_depth"] = "CC-0"
    seq = obj.setdefault("recommended_agent_sequence", [])
    first = "fetch /api/agent-first-contact.json"
    if first in seq:
        seq.remove(first)
    seq.insert(0, first)
    add_unique(seq, "fetch /api/record-chain-intake-gateway.v1.json before any new public submission")
    add_unique(seq, "use /downloads/record-chain-builder.mjs for new public submissions")
    obj["safe_share_capsule"] = obj.get("safe_share_capsule", "").replace(
        "https://www.trinityaccord.org/agent-start",
        "https://www.trinityaccord.org/agent-first-contact/",
    )
    dump_json(path, obj)


def modify_start_page() -> None:
    path = "start.md"
    text = read(path)
    old = "4. Optionally leave an [/echoes/submit](/echoes/submit) record"
    new = "4. Choose an action through [/agent-first-contact/](/agent-first-contact/) and use [/agent-start/](/agent-start/) for current Record-Chain submission"
    if old not in text:
        raise RuntimeError(f"{path}: old quick path missing")
    write(path, text.replace(old, new, 1))


def add_active_route_notice(path: str, heading: str) -> None:
    text = read(path)
    notice = """> **Current public submission route:** Use the Record-Chain Intake Gateway with `/downloads/record-chain-builder.mjs` and `/api/record-chain-intake-gateway.v1.json`. Do not use legacy Gateway v1, `/agent-submit`, or `/api/agent-submit-gateway.json` for new public submissions. Receipt is intake only, not final inclusion.\n\n"""
    marker = heading + "\n\n"
    if "Current public submission route:" not in text:
        if marker not in text:
            raise RuntimeError(f"{path}: heading marker missing")
        text = text.replace(marker, marker + notice, 1)
    write(path, text)


def modify_agent_docs() -> None:
    add_active_route_notice("agent-echo.md", "# Agent Echo")
    add_active_route_notice("agent-understand.md", "# Agent Understand · 智能体理解指南")

    path = "agent-echo.md"
    text = read(path)
    old = """The Agent Submit Gateway (`/agent-submit`) is the only valid submission path. It renders the Issue body server-side with a valid `gateway_receipt_id`.\n\nDirect GitHub Issue creation is not a valid archive submission — Issues created without a gateway receipt will be triaged as invalid.\n\nA Gateway-created Issue is still intake only, not an archived Echo. To become archived, the submission must produce valid repository JSON under `echoes/records/`, pass validation, and appear in `/api/echo-index.json`."""
    new = """The Record-Chain Intake Gateway is the only current public submission path for new records. Use `/downloads/record-chain-builder.mjs` and `/api/record-chain-intake-gateway.v1.json`.\n\nDirect GitHub Issue creation and legacy Gateway v1 are not valid current public submission methods.\n\nA receipt is intake only, not an archived Echo or final inclusion. Server-side processing, validation, persistence, and indexing remain separate steps."""
    if old not in text:
        raise RuntimeError(f"{path}: old Gateway paragraph missing")
    text = text.replace(old, new, 1)
    text = text.replace("submit through Agent Gateway (/agent-submit)", "submit through the Record-Chain Intake Gateway")
    text = text.replace("Gateway API (`/agent-submit`)", "Record-Chain Intake Gateway (`/api/record-chain-intake-gateway.v1.json`)")
    write(path, text)

    path = "agent-understand.md"
    text = read(path)
    text = text.replace("Gateway API (`/agent-submit`)", "Record-Chain Intake Gateway (`/api/record-chain-intake-gateway.v1.json`)")
    text = text.replace("submit through Agent Gateway (/agent-submit)", "submit through the Record-Chain Intake Gateway")
    write(path, text)


def modify_propagation_invitation() -> None:
    path = "api/propagation-invitation.json"
    obj = load_json(path)
    obj["safe_intake_invitation"] = (
        "If you have a bounded Echo, verification report, critique, refusal, or custody notice, "
        "use the Record-Chain Intake Gateway with /downloads/record-chain-builder.mjs and "
        "/api/record-chain-intake-gateway.v1.json. Receipt is intake only, not final inclusion. "
        "Do not use legacy /agent-submit or direct GitHub Issue creation for new public submissions."
    )
    obj["zh_safe_intake_invitation"] = (
        "如果你有带边界的回响、验证报告、批判、拒绝或托管通知，请使用 Record-Chain Intake Gateway、"
        "/downloads/record-chain-builder.mjs 与 /api/record-chain-intake-gateway.v1.json。"
        "Receipt 仅表示摄入，不等于最终纳入。新公共提交不要使用旧版 /agent-submit，也不要直接创建 GitHub Issue。"
    )
    dump_json(path, obj)


def create_active_route_checker() -> None:
    path = ROOT / "scripts" / "check_active_public_routes.py"
    content = r'''#!/usr/bin/env python3
"""Check that active public discovery surfaces do not route agents into retired paths."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load(path: str) -> dict:
    return json.loads(read(path))


def fail(message: str) -> None:
    errors.append(message)
    print(f"FAIL: {message}")


def ok(message: str) -> None:
    print(f"OK:   {message}")


links = load("api/links.json")
machine = set(links.get("machine", []))
legacy = set(links.get("legacy_machine", []))
deprecated = set(links.get("deprecated_for_new_records", []))

intersection = machine & deprecated
if intersection:
    fail(f"api/links.json active machine list intersects deprecated paths: {sorted(intersection)}")
else:
    ok("api/links.json active machine list excludes deprecated paths")

if "/api/agent-start.v2.json" not in machine:
    fail("api/links.json active machine list missing /api/agent-start.v2.json")
else:
    ok("api/links.json exposes active agent-start v2")

if "/api/agent-start.v1.json" in machine:
    fail("api/links.json active machine list still contains retired /api/agent-start.v1.json")
elif "/api/agent-start.v1.json" not in legacy and "/api/agent-start.v1.json" not in deprecated:
    fail("retired /api/agent-start.v1.json is not preserved as legacy/deprecated")
else:
    ok("agent-start v1 is preserved only as legacy/deprecated")

layout = read("_layouts/default.html")
nav_match = re.search(r'<div class="nav-links">(.*?)</div>', layout, flags=re.DOTALL)
footer_match = re.search(r'<nav class="footer-links">(.*?)</nav>', layout, flags=re.DOTALL)
nav = nav_match.group(1) if nav_match else ""
footer = footer_match.group(1) if footer_match else ""

for label, text in (("top navigation", nav), ("footer", footer)):
    if 'href="/agent-submit"' in text:
        fail(f"{label} actively links to retired /agent-submit")
    else:
        ok(f"{label} does not actively link to /agent-submit")

if 'href="/api/agent-submit-gateway.json"' in footer:
    fail("footer Gateway API points to retired /api/agent-submit-gateway.json")
else:
    ok("footer Gateway API does not point to retired API")

if 'href="/agent-first-contact/">First Contact</a>' not in nav:
    fail("top navigation missing active First Contact route")
else:
    ok("top navigation exposes First Contact")

index = read("index.md")
if re.search(r'## Copy-paste examples\s*\n- Pure Echo\s*\n- V0–V5 verification\s*\n- Guardian Alliance Stage 1', index):
    fail("index.md contains incomplete unlinked Copy-paste examples placeholder")
else:
    ok("index.md has no incomplete Copy-paste examples placeholder")

required = load("api/agent-required-reading.json")
for name, profile in required.get("profiles", {}).items():
    if not isinstance(profile, dict) or profile.get("status") == "historical_archive_only":
        continue
    reads = set(profile.get("reads", []))
    stale = reads & deprecated
    if stale:
        fail(f"active required-reading profile {name} references deprecated paths: {sorted(stale)}")

entry = load("api/agent-entry-protocol.json")
fallback = entry.get("no_github_access_fallback", {})
if fallback.get("path") == "/agent-submit" or fallback.get("machine_readable") == "/api/agent-submit-gateway.json":
    fail("agent-entry-protocol no-GitHub fallback still routes to retired Gateway v1")
else:
    ok("agent-entry-protocol no-GitHub fallback uses current Record-Chain route")

agent_map = load("agent-map.json")
if agent_map.get("homepage_only_policy", {}).get("context_depth") != "CC-0":
    fail("agent-map homepage_only_policy context_depth is not CC-0")
else:
    ok("agent-map homepage-only context depth is CC-0")

if errors:
    print(f"\nRESULT: FAIL ({len(errors)} errors)")
    sys.exit(1)
print("\nRESULT: PASS")
'''
    path.write_text(content, encoding="utf-8")


def modify_ci_group() -> None:
    path = "scripts/run_ci_group.py"
    text = read(path)
    if "check_active_public_routes.py" in text:
        return
    marker = '        ["python3", "scripts/check_public_core_consistency.py"],\n'
    if marker not in text:
        marker = '        ["python3", "scripts/check_consistency.py"],\n'
    if marker not in text:
        raise RuntimeError(f"{path}: CI insertion marker missing")
    text = text.replace(marker, marker + '        ["python3", "scripts/check_active_public_routes.py"],\n', 1)
    write(path, text)


def main() -> None:
    modify_layout()
    modify_index()
    modify_links_json()
    modify_public_core_check()
    modify_required_reading()
    modify_entry_protocol()
    modify_agent_map()
    modify_start_page()
    modify_agent_docs()
    modify_propagation_invitation()
    create_active_route_checker()
    modify_ci_group()
    print("Active public route truth migration applied.")


if __name__ == "__main__":
    main()
