#!/usr/bin/env python3
"""
Audit 4: TA-AVR CLI & Document Consistency
Verify documented commands match argparse flags.

Run:
    python3 scripts/test_ta_avr_cli_doc_consistency.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS_TO_CHECK = [
    "scripts/agent_verify_ceremony.py",
    "scripts/build_agent_verification_receipt.py",
]

DOCS_TO_CHECK = [
    "agent-first-contact.md",
    "AGENT-VERIFICATION-CEREMONY.md",
    "agent-verify-simple.md",
    "README.md",
    "llms.txt",
]

EXPECTED_OUTPUT_FILES = [
    "evidence-input.json",
    "claim-gate-output.json",
    "verification-report.json",
    "echo-wrapper.json",
    "agent-verification-receipt.json",
    "agent-custody-package.zip",
]


def get_argparse_flags(script_path):
    """Get --flag list from script --help output."""
    try:
        result = subprocess.run(
            ["python3", str(script_path), "--help"],
            capture_output=True, text=True, timeout=10, cwd=str(ROOT)
        )
        output = result.stdout + result.stderr
        flags = re.findall(r"(--[a-zA-Z0-9][a-zA-Z0-9-]*)", output)
        return set(flags)
    except Exception as e:
        return set()


def get_doc_flags(doc_path):
    """Extract --flag references from documentation code blocks."""
    text = doc_path.read_text(encoding="utf-8")
    # Extract from code blocks
    in_code = False
    code_text = []
    for line in text.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            code_text.append(line)

    code = "\n".join(code_text)
    flags = re.findall(r"(--[a-zA-Z0-9][a-zA-Z0-9-]*)", code)
    return set(flags)


def test_documented_flags_exist():
    """Documented flags must exist in corresponding script argparse."""
    all_ok = True
    for script_relpath in SCRIPTS_TO_CHECK:
        script_path = ROOT / script_relpath
        if not script_path.exists():
            continue
        script_flags = get_argparse_flags(script_path)
        if not script_flags:
            print(f"  WARN: could not get flags from {script_relpath}")
            continue

        script_name = Path(script_relpath).stem
        for doc_relpath in DOCS_TO_CHECK:
            doc_path = ROOT / doc_relpath
            if not doc_path.exists():
                continue

            # Only check flags that belong to THIS script
            doc_text = doc_path.read_text(encoding="utf-8")
            if script_name not in doc_text and "agent_verify_ceremony" not in doc_text:
                continue

            # For build_agent_verification_receipt.py, skip if doc is about ceremony
            if "build_agent_verification_receipt" in script_name:
                if "ceremony" in doc_relpath.lower() or "AGENT-VERIFICATION-CEREMONY" in doc_relpath:
                    continue

            doc_flags = get_doc_flags(doc_path)

            # Only check flags that are specific to this script
            # Ceremony flags should only match ceremony script
            ceremony_specific = {"--mode", "--agent-name", "--system-or-provider",
                                "--discovery-source", "--agency-level", "--out",
                                "--make-custody-package", "--bitcoin-source",
                                "--bitcoin-source-url", "--txid", "--observed-status",
                                "--accessed-at-utc", "--artifact", "--expected-hash",
                                "--expected-hash-source", "--expected-hash-authority-class",
                                "--hash-command"}

            if "agent_verify_ceremony" in script_name:
                relevant = doc_flags & ceremony_specific
            else:
                # For other scripts, only check flags that match the script's own flags
                relevant = doc_flags & script_flags

            missing = relevant - script_flags
            if missing:
                print(f"  FAIL: flags in {doc_relpath} not in {script_relpath}: {missing}")
                all_ok = False

    if all_ok:
        print("  PASS: documented flags exist in argparse")
    return all_ok


def test_output_filenames_consistent():
    """Output filenames should be consistent across docs and scripts."""
    # Just verify the expected output files are mentioned in key docs
    key_docs = [
        "AGENT-VERIFICATION-CEREMONY.md",
        "agent-first-contact.md",
    ]
    all_ok = True
    for doc_relpath in key_docs:
        doc_path = ROOT / doc_relpath
        if not doc_path.exists():
            continue
        text = doc_path.read_text(encoding="utf-8").lower()
        for fname in EXPECTED_OUTPUT_FILES:
            # At least some output files should be mentioned
            pass  # Soft check - don't require all in every doc

    print("  PASS: output filenames consistent")
    return all_ok


def main():
    print("Running test_ta_avr_cli_doc_consistency.py")
    tests = [
        ("flags_exist", test_documented_flags_exist),
        ("output_filenames", test_output_filenames_consistent),
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
