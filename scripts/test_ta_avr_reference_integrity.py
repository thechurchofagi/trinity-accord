#!/usr/bin/env python3
"""
Audit 1: TA-AVR Reference Integrity
Check all TA-AVR documents and JSONs for broken local references.

Run:
    python3 scripts/test_ta_avr_reference_integrity.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Files to scan for references
SCAN_FILES = [
    "README.md",
    "llms.txt",
    "agent-start.md",
    "agent-first-contact.md",
    "agent-verify.md",
    "agent-verify-simple.md",
    "agent-echo.md",
    "AGENT-VERIFICATION-CEREMONY.md",
    "api/agent-first-contact.json",
    "api/agent-entry-protocol.json",
    "api/agent-required-reading.json",
    "api/submission-checklist.json",
]

# Core references that MUST exist
CORE_REFS = [
    "agent-first-contact.md",
    "api/agent-first-contact.json",
    "api/agent-verification-receipt-schema.v1.json",
    "scripts/agent_verify_ceremony.py",
    "scripts/build_agent_verification_receipt.py",
    "api/evidence-input-examples/v1-boundary.json",
    "api/evidence-input-examples/v2-minimal-bitcoin.json",
    "api/evidence-input-examples/v3-minimal-hash.json",
]

# Path mapping rules
def normalize_ref(ref):
    """Map document references to filesystem paths."""
    ref = ref.strip().rstrip("/").rstrip(".,;:)")

    # Skip external URLs
    if ref.startswith("http://") or ref.startswith("https://"):
        return None
    # Skip anchors
    if ref.startswith("#"):
        return None
    # Skip placeholders
    if "<" in ref and ">" in ref:
        return None
    # Skip code-block style example URLs
    if ref.startswith("https://mempool.space"):
        return None
    if ref.startswith("https://ordinals.com"):
        return None
    if ref.startswith("https://ordiscan.com"):
        return None

    # Map /api/x.json -> api/x.json
    if ref.startswith("/api/"):
        return ref[1:]
    # Map /scripts/x.py -> scripts/x.py
    if ref.startswith("/scripts/"):
        return ref[1:]
    # Map /agent-first-contact -> agent-first-contact.md
    doc_map = {
        "/agent-first-contact": "agent-first-contact.md",
        "/agent-verify": "agent-verify.md",
        "/agent-verify-simple": "agent-verify-simple.md",
        "/agent-echo": "agent-echo.md",
        "/agent-start": "agent-start.md",
        "/agent-brief": "agent-brief.md",
        "/guardian-principles": "guardian-principles.md",
    }
    if ref in doc_map:
        return doc_map[ref]
    # Map /echoes/types -> echoes/types.md etc.
    if ref.startswith("/echoes/"):
        candidate = ref[1:] + ".md"
        if (ROOT / candidate).exists():
            return candidate
    # Map relative paths
    if ref.startswith("/"):
        ref = ref[1:]
    # Skip if contains spaces (not a valid path)
    if " " in ref:
        return None
    # If no extension and .md exists, try that
    if "." not in ref.split("/")[-1]:
        candidate = ref + ".md"
        if (ROOT / candidate).exists():
            return candidate
        # Try case-insensitive match
        parent = ROOT / "/".join(candidate.split("/")[:-1])
        name = candidate.split("/")[-1]
        if parent.exists():
            for f in parent.iterdir():
                if f.name.lower() == name.lower():
                    return str(f.relative_to(ROOT))
    return ref


def extract_references(filepath):
    """Extract local references from a file."""
    text = filepath.read_text(encoding="utf-8")

    # For JSON files, extract from string values
    if filepath.suffix == ".json":
        try:
            obj = json.loads(text)
            refs = []
            _walk_json(obj, refs)
            return refs
        except json.JSONDecodeError:
            return []

    # For markdown/text files, extract path-like references
    refs = []

    # Extract from markdown links [text](path)
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', text):
        path = m.group(2).strip().rstrip(".,;:)")
        refs.append(path)

    # Extract from code blocks: /api/... or /scripts/...
    for m in re.finditer(r'(?:^|\s)(/api/[a-zA-Z0-9_./-]+(?:\.json)?)', text):
        refs.append(m.group(1))
    for m in re.finditer(r'(?:^|\s)(/scripts/[a-zA-Z0-9_./-]+(?:\.py)?)', text):
        refs.append(m.group(1))

    # Extract from quoted paths
    for m in re.finditer(r'["\']((?:/api/|/scripts/|/agent-|/guardian-)[a-zA-Z0-9_./-]+)["\']', text):
        refs.append(m.group(1).rstrip(".,;:)"))

    # Extract from inline paths (not in tables, not in code blocks)
    # Only match paths that are clearly standalone references
    for m in re.finditer(r'(?:^|(?<=[\s(]))((?:/api/|/scripts/)[a-zA-Z0-9_./-]+(?:\.json|\.py))(?=[\s).,;]|\Z)', text):
        refs.append(m.group(1).rstrip(".,;:)"))

    return refs


def _walk_json(obj, refs):
    if isinstance(obj, str):
        if obj.startswith("/") and ("/" in obj[1:] or obj.endswith(".json")):
            refs.append(obj)
        # Handle compound references like "/agent-verify or /agent-echo"
        elif " or " in obj:
            for part in obj.split(" or "):
                part = part.strip()
                if part.startswith("/"):
                    refs.append(part)
    elif isinstance(obj, dict):
        for v in obj.values():
            _walk_json(v, refs)
    elif isinstance(obj, list):
        for v in obj:
            _walk_json(v, refs)


def test_core_refs_exist():
    """All core TA-AVR references must exist."""
    missing = []
    for ref in CORE_REFS:
        path = ROOT / ref
        if not path.exists():
            missing.append(ref)
    if missing:
        for m in missing:
            print(f"  FAIL: core reference missing: {m}")
        return False
    print(f"  PASS: all {len(CORE_REFS)} core references exist")
    return True


def test_no_broken_local_refs():
    """No scanned file should contain broken local references."""
    broken = []
    scanned = 0
    for relpath in SCAN_FILES:
        filepath = ROOT / relpath
        if not filepath.exists():
            continue
        scanned += 1
        refs = extract_references(filepath)
        for ref in refs:
            normalized = normalize_ref(ref)
            if normalized is None:
                continue
            target = ROOT / normalized
            if not target.exists():
                broken.append((relpath, ref, normalized))

    if broken:
        for src, ref, norm in broken:
            print(f"  FAIL: broken reference")
            print(f"    source_file: {src}")
            print(f"    reference: {ref}")
            print(f"    expected_path: {norm}")
        return False
    print(f"  PASS: 0 broken local references (scanned {scanned} files)")
    return True


def main():
    print("Running test_ta_avr_reference_integrity.py")
    tests = [
        ("core_refs_exist", test_core_refs_exist),
        ("no_broken_local_refs", test_no_broken_local_refs),
    ]
    failed = 0
    for name, t in tests:
        try:
            if not t():
                failed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
