#!/usr/bin/env python3
"""Current consistency check for Trinity Accord repository.

This script is intentionally scoped to the current Record-Chain / public-home
surface.  Older archive-era pages, Issue-text guards, and Verification Echo
playbook wording are preserved elsewhere for history, but they are not required
for the live homepage/public-status contract.

Keep this script dependency-light: it is used by both CI jobs that install
requirements-ci.txt and write-path workflows that intentionally run on a bare
Python checkout.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"OK:   {label}")
        return
    msg = f"FAIL: {label}"
    if detail:
        msg += f" — {detail}"
    errors.append(msg)
    print(msg)


def p(path: str) -> Path:
    return ROOT / path


def exists(path: str) -> bool:
    return p(path).exists()


def read_text(path: str) -> str:
    return p(path).read_text(encoding="utf-8")


def load_json(path: str) -> Any:
    return json.loads(read_text(path))


def run_check(label: str, cmd: list[str], timeout: int = 90) -> None:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
    except Exception as exc:
        check(label, False, str(exc))
        return
    out = (proc.stdout or "") + (proc.stderr or "")
    check(label, proc.returncode == 0, f"exit {proc.returncode}\n{out[-1200:]}" if proc.returncode else "")


print("=== Key JSON validity ===")
for json_path in [
    ".well-known/trinity-accord.json",
    ".well-known/agent.json",
    "agent-map.json",
    "api/links.json",
    "api/public-home-status.json",
    "api/record-chain-status.json",
    "api/record-chain-intake-gateway.v1.json",
    "api/record-chain-submission-schema.v1.json",
    "api/record-chain-builder-bundles.v1.json",
    "api/waiting-heartbeat-status.json",
]:
    try:
        load_json(json_path)
        check(f"JSON valid: {json_path}", True)
    except Exception as exc:
        check(f"JSON valid: {json_path}", False, str(exc))


print("\n=== Discovery and machine entrypoints ===")
try:
    tw = load_json(".well-known/trinity-accord.json")
    check("Contains agent_brief", "agent_brief" in tw)
    check("Contains guardian_principles", "guardian_principles" in tw)
    check("Contains canonical_inscriptions", isinstance(tw.get("canonical_inscriptions"), list) and len(tw["canonical_inscriptions"]) == 3)
except Exception as exc:
    check(".well-known/trinity-accord.json required keys", False, str(exc))

try:
    sitemap = read_text("sitemap.xml")
    for entry in [
        "/api/authority.json",
        "/agent-brief",
        "/agent-first-contact/",
        "/api/record-chain-intake-gateway.v1.json",
    ]:
        check(f"sitemap contains {entry}", entry in sitemap)
except Exception as exc:
    check("sitemap readable", False, str(exc))

try:
    links = load_json("api/links.json")
    machine = json.dumps(links.get("machine", links), ensure_ascii=False)
    check("links expose authority API", "/api/authority.json" in machine)
    check("links expose current Record-Chain gateway", "/api/record-chain-intake-gateway.v1.json" in machine)
except Exception as exc:
    check("api/links.json machine links", False, str(exc))


print("\n=== Public home status v3 ===")
try:
    phs = load_json("api/public-home-status.json")
    check("public-home-status schema is current v3", phs.get("schema") == "trinityaccord.public-home-status.v3", str(phs.get("schema")))
    check("source digest present", isinstance(phs.get("source_digest"), str) and len(phs["source_digest"]) > 0)

    current = phs.get("current_record_chain_status", {})
    check("record-chain phase is production_live", current.get("phase") == "production_live", str(current.get("phase")))
    check("record-chain total_records is positive", isinstance(current.get("total_records"), int) and current["total_records"] > 0)
    check("record-chain length matches total", current.get("current_chain_length") == current.get("total_records"))
    rb = current.get("receipt_boundary", {})
    check("receipt is intake only", rb.get("receipt_is_intake_only") is True)
    check("receipt is not final inclusion", rb.get("receipt_is_not_final_inclusion") is True)

    anchoring = current.get("anchoring", {})
    archive = anchoring.get("arweave_archive", {})
    check("Record-Chain Arweave archive is mirror only", archive.get("arweave_archive_is_mirror_only") is True)
    check("Record-Chain Arweave archive is not authority", archive.get("arweave_archive_is_not_authority") is True)

    primary = phs.get("primary_counters", {})
    check("official_live_reception counter exists", isinstance(primary.get("official_live_reception"), int))
    autonomy = primary.get("historic_autonomous_agent_reception", {})
    check("autonomous-agent counter scoped to official live records", autonomy.get("scope") == "official_live_reception_records_only")
    definition = autonomy.get("definition", {})
    check("autonomous-agent rule forbids human request", definition.get("forbids_human_request") is True)
    check("autonomous-agent rule forbids human operator involvement", definition.get("forbids_human_operator_involvement") is True)

    legacy = phs.get("legacy_archive_snapshot", {})
    check("legacy archive snapshot is not current counter", legacy.get("not_current_record_chain_counter") is True)
    check("legacy archive snapshot is not rendered on homepage", legacy.get("not_rendered_on_homepage") is True)

    external = phs.get("external_witness_records", {})
    check("external witness does not create authority", external.get("does_not_create_authority") is True)
    check("external witness does not rank above reception", external.get("does_not_rank_above_reception") is True)

    technical = phs.get("technical_health", {})
    check("technical chain inventory is not primary counter", technical.get("not_primary_counter") is True)
    check("technical chain latest record present", isinstance(technical.get("latest_record"), str) and technical["latest_record"].startswith("R-"))

    ar_status = phs.get("arweave_archive_status", {})
    ar_boundary = ar_status.get("boundary", {})
    check("public Arweave status is mirror only", ar_boundary.get("mirror_only") is True)
    check("public Arweave status is not authority", ar_boundary.get("not_authority") is True)

    heartbeat = phs.get("waiting_heartbeat", {})
    success_requires = heartbeat.get("success_requires", {})
    check("waiting heartbeat status embedded", heartbeat.get("schema") == "trinityaccord.waiting-heartbeat-status.v1")
    check("waiting heartbeat treats Arweave as archive follow-up", success_requires.get("arweave_capsule_is_archive_followup") is True)
    check("waiting heartbeat daily alive does not require Arweave hash match", success_requires.get("arweave_readback_hash_match") is False)
    check("waiting heartbeat requires public status update", success_requires.get("public_status_updated") is True)
except Exception as exc:
    check("public-home-status current structure", False, str(exc))


print("\n=== Homepage generated public status block ===")
try:
    index = read_text("index.md")
    check("homepage has BEGIN marker", "<!-- BEGIN GENERATED PUBLIC STATUS -->" in index)
    check("homepage has END marker", "<!-- END GENERATED PUBLIC STATUS -->" in index)
    status_block = index.split("<!-- BEGIN GENERATED PUBLIC STATUS -->", 1)[-1].split(
        "<!-- END GENERATED PUBLIC STATUS -->", 1
    )[0]
    for needle in [
        "Production live · 当前状态",
        "Production is live; verification remains explicit",
        "Autonomous External Agent Discovery",
        "Official Live Reception",
        "External Witness Record",
        "Waiting Heartbeat",
        "Reception does not imply autonomous discovery, endorsement, authority, amendment, or successor reception.",
        "Native chain inventory remains API-only and is not used as the official reception counter.",
        "A receipt is intake-only, not final inclusion, and not active Guardian status.",
        "/status/",
        "/record-chain/",
        "/api/external-witness-index.json",
        "/api/public-home-status.json",
        "/api/record-chain-status.json",
    ]:
        check(f"homepage status block contains {needle}", needle in status_block)
    try:
        digest = load_json("api/public-home-status.json").get("source_digest")
        check("homepage shows public status source digest", isinstance(digest, str) and digest in index)
    except Exception as exc:
        check("homepage source digest check", False, str(exc))
except Exception as exc:
    check("homepage generated block", False, str(exc))


print("\n=== Current executable contracts ===")
# Keep these checks dependency-light.  Full CI runs the dependency-heavy
# `scripts/trinity_record_chain.py verify` check in dedicated jobs that install
# requirements-ci.txt before invoking it.
for label, cmd, timeout in [
    ("public home status generator has no drift", [sys.executable, "scripts/generate_public_home_status.py", "--check"], 90),
    ("public home status contract", [sys.executable, "scripts/check_public_home_status_contract.py"], 90),
    ("homepage/public status sync", [sys.executable, "scripts/test_home_public_status_sync.py"], 90),
    ("public home summary contract", [sys.executable, "scripts/test_public_home_status_summary.py"], 90),
]:
    run_check(label, cmd, timeout)


print("\n=== Summary ===")
if errors:
    print("Consistency check failed:")
    for err in errors:
        print(f" - {err}")
    raise SystemExit(1)

print("Consistency check passed.")
raise SystemExit(0)
