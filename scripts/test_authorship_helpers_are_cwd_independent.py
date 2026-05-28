#!/usr/bin/env python3
"""Test that authorship helper scripts resolve sibling files relative to themselves, not cwd.

This prevents the "works in repo root, breaks in zero-clone bundle" failure mode
where scripts use cwd-relative paths instead of import.meta.url / __file__.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Scripts that call sibling files via subprocess must use import.meta.url (JS) or __file__ (Python)
JS_SCRIPTS_REQUIRING_SELF_PATH = [
    "scripts/attach_agent_authorship_proof.mjs",
]

# Patterns that indicate a cwd-relative path (the bug we're fixing)
CWD_RELATIVE_PATTERNS_JS = [
    # execFileSync("python3", ["scripts/...") without using a variable from import.meta.url
    re.compile(r'execFileSync\s*\(\s*["\']python3["\']\s*,\s*\[\s*["\']scripts/'),
]

# Patterns that indicate proper import.meta.url usage
IMPORT_META_URL_PATTERN = re.compile(r'import\.meta\.url')
FILE_URL_TO_PATH_PATTERN = re.compile(r'fileURLToPath\s*\(')
DIRNAME_PATTERN = re.compile(r'dirname\s*\(')


def test_attach_agent_authorship_proof_uses_import_meta_url():
    """attach_agent_authorship_proof.mjs must use import.meta.url for path resolution."""
    script_path = ROOT / "scripts" / "attach_agent_authorship_proof.mjs"
    assert script_path.exists(), f"Script not found: {script_path}"

    src = script_path.read_text(encoding="utf-8")

    # Must use import.meta.url
    assert IMPORT_META_URL_PATTERN.search(src), (
        f"{script_path.name} does not use import.meta.url. "
        "It must resolve sibling scripts relative to itself, not cwd."
    )

    # Must use fileURLToPath
    assert FILE_URL_TO_PATH_PATTERN.search(src), (
        f"{script_path.name} does not use fileURLToPath(). "
        "Use fileURLToPath(import.meta.url) to get the directory."
    )

    # Must use dirname
    assert DIRNAME_PATTERN.search(src), (
        f"{script_path.name} does not use dirname(). "
        "Use dirname(fileURLToPath(import.meta.url)) to get the script directory."
    )

    # Must NOT use cwd-relative paths to sibling scripts
    for pattern in CWD_RELATIVE_PATTERNS_JS:
        match = pattern.search(src)
        assert not match, (
            f"{script_path.name} uses cwd-relative path: '{match.group()}'. "
            "Use a variable derived from import.meta.url instead."
        )

    # Must have a HERE or similar constant
    assert re.search(r'(?:HERE|SCRIPT_DIR|__DIRNAME)\s*=', src), (
        f"{script_path.name} does not define a directory constant (HERE/SCRIPT_DIR/__DIRNAME). "
        "Define: const HERE = dirname(fileURLToPath(import.meta.url));"
    )


def test_gateway_payload_authorship_uses_root():
    """gateway_payload_authorship.py must use ROOT / 'scripts' for sibling paths, not cwd-relative."""
    script_path = ROOT / "scripts" / "gateway_payload_authorship.py"
    assert script_path.exists(), f"Script not found: {script_path}"

    src = script_path.read_text(encoding="utf-8")

    # Must define ROOT via __file__
    assert "Path(__file__).resolve().parents" in src, (
        f"{script_path.name} does not define ROOT via __file__. "
        "Use: ROOT = Path(__file__).resolve().parents[1]"
    )

    # ATTACH_SCRIPT must be derived from ROOT, not cwd
    assert 'ROOT / "scripts"' in src or "ROOT / 'scripts'" in src, (
        f"{script_path.name} does not derive ATTACH_SCRIPT from ROOT."
    )


def test_no_cwd_chdir_in_authorship_scripts():
    """Authorship scripts must not rely on os.chdir() or cwd assumptions."""
    scripts = [
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/gateway_payload_authorship.py",
    ]

    for rel_path in scripts:
        script_path = ROOT / rel_path
        if not script_path.exists():
            continue
        src = script_path.read_text(encoding="utf-8")

        # os.chdir is suspicious in these scripts
        if "os.chdir" in src or "process.chdir" in src:
            # Only acceptable if it restores cwd
            assert False, (
                f"{rel_path} uses chdir. Authorship scripts must be cwd-independent."
            )


if __name__ == "__main__":
    tests = [
        test_attach_agent_authorship_proof_uses_import_meta_url,
        test_gateway_payload_authorship_uses_root,
        test_no_cwd_chdir_in_authorship_scripts,
    ]
    failed = []
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\nFAILED: {len(failed)} test(s): {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nALL {len(tests)} TESTS PASSED")
        sys.exit(0)
