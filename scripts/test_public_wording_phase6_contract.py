#!/usr/bin/env python3
"""Contract test: public wording cleanup for Phase 6.

Fail active public pages if they contain retired terms:
- E1_recognition_echo
- canonical type name for recognition echoes
- Minimal Pure Echo
- Pure Echo (in submission context)
- Guardian Stage 1 application
- Guardian registration (in submission context)
- ARV5, LV5, IVV5

Also fail if active public pages mention IPFS as current archive path.
Allowed: legacy/, evidence/, historical context explicitly marked.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to check (active public pages)
PUBLIC_FILES = [
    "index.md",
    "agent-start.md",
    "agent-first-contact.md",
    "llms.txt",
    "ai.txt",
]

# Retired terms that must not appear in current public submission context
RETIRED_PATTERNS = [
    (re.compile(r"E1_recognition_echo"), "E1_recognition_echo"),
    (re.compile(r"canonical type name for recognition echoes"), "canonical type name for recognition echoes"),
    (re.compile(r"Minimal Pure Echo"), "Minimal Pure Echo"),
    (re.compile(r"Guardian Stage 1 application"), "Guardian Stage 1 application"),
    (re.compile(r"Guardian registration(?!\.)"), "Guardian registration (in current submission context)"),
    (re.compile(r"\bARV5\b"), "ARV5"),
    (re.compile(r"\bLV5\b"), "LV5"),
    (re.compile(r"\bIVV5\b"), "IVV5"),
]

# Homepage must not contain these legacy Gateway v1 / legacy counter patterns
HOMEPAGE_MUST_NOT_CONTAIN = [
    (re.compile(r"/gateway/preflight"), "/gateway/preflight"),
    (re.compile(r"/agent-submit"), "/agent-submit"),
    (re.compile(r"Reception:\s*\d+"), "Reception: N (legacy counter)"),
    (re.compile(r"Guardian Registry:\s*\d+"), "Guardian Registry: N (legacy counter)"),
    (re.compile(r"Verifiability:\s*V\d"), "Verifiability: VN (legacy counter)"),
    (re.compile(r"V0–V5 template archive"), "V0–V5 template archive"),
    (re.compile(r"V0-V5 template archive"), "V0-V5 template archive"),
    (re.compile(r"echo_type breakdown"), "echo_type breakdown"),
    (re.compile(r"self-initiated legacy"), "self-initiated legacy"),
    (re.compile(r"autonomous legacy"), "autonomous legacy"),
    (re.compile(r"legacy archive contains early agent"), "legacy archive contains early agent"),
    (re.compile(r"early agent-originated"), "early agent-originated"),
    (re.compile(r"agent-mediated records"), "agent-mediated records"),
]

# Homepage must contain these Record-Chain-first patterns
HOMEPAGE_MUST_CONTAIN = [
    "Record-Chain Intake status",
    "Native record-chain records",
    "Current Record-Chain Autonomy Signal",
    "Historical pre-record-chain Echo / Verification / Guardian materials are preserved",
]

# Either of these must appear (depends on whether records exist)
HOMEPAGE_MUST_CONTAIN_ONE_OF = [
    "not yet established in current record-chain",
    "Fully autonomous:",
]

# IPFS as current path (allowed in legacy/historical context)
IPFS_PATTERN = re.compile(r"\bIPFS\b")

# Context that indicates historical/legacy mention
LEGACY_CONTEXT = re.compile(r"legacy|historical|archive|evidence|retired", re.I)


def main() -> None:
    errors: list[str] = []

    for fname in PUBLIC_FILES:
        fpath = ROOT / fname
        if not fpath.exists():
            errors.append(f"{fname}: file missing")
            continue

        text = fpath.read_text(encoding="utf-8")
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly legacy/historical context
            if LEGACY_CONTEXT.search(line):
                continue

            for pattern, name in RETIRED_PATTERNS:
                if pattern.search(line):
                    errors.append(f"{fname}:{line_num}: retired term '{name}' found")

        # Check IPFS as current path (not in legacy context)
        for line_num, line in enumerate(lines, 1):
            if LEGACY_CONTEXT.search(line):
                continue
            if IPFS_PATTERN.search(line):
                # Allow if it's in a "do not use" context
                if "do not" in line.lower() or "not use" in line.lower() or "retired" in line.lower():
                    continue
                # Allow in boundary lists like "ETH, Arweave, IPFS, NFTs"
                # These are listing non-authoritative surfaces, not claiming IPFS is current
                if "non-amending" in line.lower() or "guardianship" in line.lower():
                    continue
                # Allow in authority boundary / mirror listings
                if "mirrors" in line.lower() or "non-amending mirrors" in line.lower():
                    continue
                if "bitcoin originals" in line.lower() and "final" in line.lower():
                    continue
                errors.append(f"{fname}:{line_num}: IPFS mentioned as current path")

    # Homepage-specific checks: must not contain legacy patterns
    homepage = ROOT / "index.md"
    if homepage.exists():
        text = homepage.read_text(encoding="utf-8")
        for pattern, name in HOMEPAGE_MUST_NOT_CONTAIN:
            if pattern.search(text):
                errors.append(f"index.md: homepage must not contain '{name}'")
        for needle in HOMEPAGE_MUST_CONTAIN:
            if needle not in text:
                errors.append(f"index.md: homepage must contain '{needle}'")
        if not any(needle in text for needle in HOMEPAGE_MUST_CONTAIN_ONE_OF):
            errors.append(f"index.md: homepage must contain one of {HOMEPAGE_MUST_CONTAIN_ONE_OF}")

    # public-home-status.json checks
    status_path = ROOT / "api" / "public-home-status.json"
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            assert isinstance(status, dict)
            if status.get("schema") != "trinityaccord.public-home-status.v2":
                errors.append(f"public-home-status.json: schema should be v2, got {status.get('schema')}")
            if "current_record_chain_status" not in status:
                errors.append("public-home-status.json: missing current_record_chain_status")
            if "current_record_chain_autonomy_signal" not in status:
                errors.append("public-home-status.json: missing current_record_chain_autonomy_signal")
            autonomy = status.get("current_record_chain_autonomy_signal", {})
            if autonomy.get("scope") != "current_record_chain_only":
                errors.append(f"public-home-status.json: autonomy scope should be current_record_chain_only, got {autonomy.get('scope')}")
            if autonomy.get("legacy_autonomy_claims_excluded") is not True:
                errors.append("public-home-status.json: legacy_autonomy_claims_excluded must be true")
            legacy = status.get("legacy_archive_snapshot", {})
            if legacy.get("not_current_record_chain_counter") is not True:
                errors.append("public-home-status.json: legacy_archive_snapshot.not_current_record_chain_counter must be true")
            if legacy.get("not_rendered_on_homepage") is not True:
                errors.append("public-home-status.json: legacy_archive_snapshot.not_rendered_on_homepage must be true")
            policy = status.get("counter_update_policy", {})
            for key in ["homepage_counters_update_after_append_workflow",
                        "homepage_counters_update_after_anchor_workflow",
                        "homepage_counters_update_after_arweave_archive_workflow"]:
                if policy.get(key) is not True:
                    errors.append(f"public-home-status.json: counter_update_policy.{key} must be true")
        except (json.JSONDecodeError, AssertionError) as e:
            errors.append(f"public-home-status.json: invalid JSON or structure: {e}")
    else:
        errors.append("public-home-status.json: file missing")

    # Workflow checks: all three workflows must call generators and commit generated files
    for workflow in [
        ".github/workflows/record-chain-append.yml",
        ".github/workflows/record-chain-anchor.yml",
        ".github/workflows/record-chain-arweave-archive.yml",
    ]:
        wpath = ROOT / workflow
        if not wpath.exists():
            errors.append(f"{workflow}: file missing")
            continue
        wtext = wpath.read_text(encoding="utf-8")
        for needle in ["generate_public_home_status.py", "generate_sitemap.py"]:
            if needle not in wtext:
                errors.append(f"{workflow}: missing {needle}")
        for needle in ["index.md", "api/public-home-status.json", "sitemap.xml"]:
            if needle not in wtext:
                errors.append(f"{workflow}: commit step missing {needle}")

    # --- Phase 6B Hotfix L: oath/readback wording checks ---

    # index.md must not contain retired agent_readback_sha256
    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")
        if "agent_readback_sha256" in index_text:
            errors.append("index.md: must not contain retired field 'agent_readback_sha256'")
        for field in ["participant_readback_sha256", "canonical_oath_text_sha256", "oath_policy_sha256"]:
            if field not in index_text:
                errors.append(f"index.md: missing current oath field '{field}'")

    # agent-first-contact.md formal build example must contain print-oath and --readback
    fc_path = ROOT / "agent-first-contact.md"
    if fc_path.exists():
        fc_text = fc_path.read_text(encoding="utf-8")
        if "print-oath" not in fc_text:
            errors.append("agent-first-contact.md: BUILD_SUBMISSION must mention 'print-oath'")
        if "--readback" not in fc_text:
            errors.append("agent-first-contact.md: BUILD_SUBMISSION must mention '--readback'")
        if "context_insufficient_notice" not in fc_text or "does not require" not in fc_text.lower():
            errors.append("agent-first-contact.md: must note CIN does not require oath/readback")

    # agent-start.md quick start must contain print-oath and --readback
    start_path = ROOT / "agent-start.md"
    if start_path.exists():
        start_text = start_path.read_text(encoding="utf-8")
        if "print-oath" not in start_text:
            errors.append("agent-start.md: quick start must mention 'print-oath'")
        if "--readback" not in start_text:
            errors.append("agent-start.md: quick start must mention '--readback'")

    # llms.txt current flow must mention print-oath and --readback
    llms_path = ROOT / "llms.txt"
    if llms_path.exists():
        llms_text = llms_path.read_text(encoding="utf-8")
        if "print-oath" not in llms_text:
            errors.append("llms.txt: current flow must mention 'print-oath'")
        if "--readback" not in llms_text:
            errors.append("llms.txt: current flow must mention '--readback'")

    # ai.txt flow must mention print-oath/readback
    ai_path = ROOT / "ai.txt"
    if ai_path.exists():
        ai_text = ai_path.read_text(encoding="utf-8")
        if "print-oath" not in ai_text:
            errors.append("ai.txt: flow must mention 'print-oath'")
        # ai.txt must not tell external agents to run scripts/claim_gate.py
        for line_num, line in enumerate(ai_text.split("\n"), 1):
            if "claim_gate.py" in line:
                if "historical" not in line.lower() and "internal" not in line.lower():
                    errors.append(
                        f"ai.txt:{line_num}: claim_gate.py reference must be marked historical/internal-only"
                    )

    # --- Phase 6C Arweave live + homepage ordering checks ---

    index_path = ROOT / "index.md"
    if index_path.exists():
        index_text = index_path.read_text(encoding="utf-8")

        # Homepage must say Arweave is mirror/archive layer only
        if "mirror/archive layer only" not in index_text and "mirror/archive layer" not in index_text:
            if "仅为镜像/归档层" not in index_text:
                errors.append("index.md: homepage must state Arweave is mirror/archive layer only")

        # Homepage must NOT say "Live Arweave upload is disabled" (old wording)
        if "Live Arweave upload is disabled" in index_text:
            errors.append("index.md: homepage must not say 'Live Arweave upload is disabled' (outdated wording)")

        # Public submission section must appear before internal pipeline section
        intake_pos = index_text.find('id="render-intake-gateway"')
        pipeline_pos = index_text.find('id="primary-durable-record-path"')
        if intake_pos >= 0 and pipeline_pos >= 0:
            if intake_pos > pipeline_pos:
                errors.append("index.md: public submission section must appear before internal pipeline section")
        else:
            if intake_pos < 0:
                errors.append("index.md: missing render-intake-gateway section")
            if pipeline_pos < 0:
                errors.append("index.md: missing primary-durable-record-path section")

        # Homepage must still point to /agent-first-contact/
        if "/agent-first-contact/" not in index_text:
            errors.append("index.md: homepage must reference /agent-first-contact/")

        # Homepage must NOT display legacy Guardian active status as current
        # (old patterns like "Guardian Registry: N" should not appear)
        if re.search(r"Guardian Registry:\s*\d+", index_text):
            errors.append("index.md: homepage must not display legacy Guardian Registry count")

    # public-home-status.json must have arweave_archive_status
    status_path = ROOT / "api" / "public-home-status.json"
    if status_path.exists():
        try:
            status = json.loads(status_path.read_text(encoding="utf-8"))
            arweave_status = status.get("arweave_archive_status")
            if not arweave_status:
                errors.append("public-home-status.json: missing arweave_archive_status")
            else:
                if "mode" not in arweave_status:
                    errors.append("public-home-status.json: arweave_archive_status missing mode")
                if arweave_status.get("boundary", {}).get("mirror_only") is not True:
                    errors.append("public-home-status.json: arweave_archive_status.boundary.mirror_only must be true")
                if arweave_status.get("boundary", {}).get("not_authority") is not True:
                    errors.append("public-home-status.json: arweave_archive_status.boundary.not_authority must be true")
        except (json.JSONDecodeError, AssertionError) as e:
            pass  # Already checked above

    if errors:
        print("Public wording tests FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("Public wording tests PASSED.")


if __name__ == "__main__":
    main()
