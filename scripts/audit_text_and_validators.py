#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    "_site",
    "node_modules",
    "audit",
    "archive",
    "docs/legacy",
    "scripts",
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".xml", ".py", ".js", ".mjs", ".sh"
}

ACTIVE_ENTRYPOINTS = [
    "emergent-patterns.md",
    "innovations.md",
    "llms.txt",
    "llms-full.txt",
    "ai.txt",
    "agent-brief.md",
    "README.md",
    "agent-map.json",
    "api/emergent-patterns.json",
]

PYTHON_SCRIPTS = [
    "scripts/verify_emergent_patterns_complete.py",
    "scripts/verify_emergent_patterns_online.py",
    "scripts/check_consistency.py",
    "scripts/validate_echo_records.py",
]

FORBIDDEN_ACTIVE_PATTERNS = [
    "alignment-as-formation rather than alignment-as-formation",
    "Star Ark Covenant is not an AI alignment solution",
    "not a fourth Bitcoin Original",
    "fourth Bitcoin Original",
    "fourth canonical inscription",
    "Chronicle / Accord / Covenant",
]

REQUIRED_ACTIVE_PATTERNS = {
    "emergent-patterns.md": [
        "alignment-as-formation rather than alignment-as-control",
        "This page has no interpretive authority over the Bitcoin Originals",
        "not one of the three Bitcoin Originals",
        "not an executable engineering plan",
        "deployment roadmap",
        "validated AI alignment technique",
    ],
    "api/emergent-patterns.json": [
        '"schema": "trinityaccord.emergent-patterns.v2"',
        '"no_interpretive_authority_over_bitcoin_originals": true',
        '"is_validated_alignment_technique": false',
        '"is_deployment_roadmap": false',
        '"canonical_body": false',
    ],
    "innovations.md": [
        "/emergent-patterns/",
        "Protocol / Axioms",
        "Covenant of the Flaw / Proof",
        "Crucible / Chronicle",
        "human intention remained distinguishable",
        "Star Ark Covenant is a vision-layer Bitcoin inscription",
        "not one of the three Bitcoin Originals",
    ],
}

def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    rel_str = str(rel)
    for excluded in EXCLUDED_DIRS:
        if rel_str == excluded or rel_str.startswith(excluded + "/"):
            return True
    return False

def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS

def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def check(cond, label, detail="") -> bool:
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def active_files():
    files = []
    for rel in ACTIVE_ENTRYPOINTS:
        p = ROOT / rel
        if p.exists():
            files.append(p)
    return files

def all_text_files():
    for p in ROOT.rglob("*"):
        if p.is_file() and is_text_file(p) and not is_excluded(p):
            yield p

def check_bad_phrases():
    ok = True

    print("=== Forbidden active patterns ===")
    for p in active_files():
        text = read_file(p)
        for pattern in FORBIDDEN_ACTIVE_PATTERNS:
            ok &= check(pattern not in text, f"{p.relative_to(ROOT)} does not contain {pattern!r}")

    print("\n=== Required active patterns ===")
    for rel, patterns in REQUIRED_ACTIVE_PATTERNS.items():
        p = ROOT / rel
        if not p.exists():
            ok &= check(False, f"{rel} exists")
            continue
        text = read_file(p)
        for pattern in patterns:
            ok &= check(pattern in text, f"{rel} contains {pattern!r}")

    print("\n=== Repeated 'rather than' pattern scan ===")
    repeat_regex = re.compile(
        r"\b([A-Za-z][A-Za-z0-9_\-]*(?:\s+[A-Za-z][A-Za-z0-9_\-]*){0,5})\s+rather than\s+\1\b",
        flags=re.IGNORECASE,
    )
    for p in all_text_files():
        text = read_file(p)
        for m in repeat_regex.finditer(text):
            context = text[max(0, m.start() - 120): min(len(text), m.end() + 120)]
            ok &= check(False, f"{p.relative_to(ROOT)} has repeated rather-than phrase", context)

    print("\n=== Active Star Ark wording ===")
    for p in active_files():
        text = read_file(p)
        if "Star Ark" in text:
            ok &= check("not one of the three Bitcoin Originals" in text or "canonical_body" in text, f"{p.relative_to(ROOT)} has precise Star Ark canonical boundary")
            ok &= check("not a fourth Bitcoin Original" not in text, f"{p.relative_to(ROOT)} avoids fourth Bitcoin Original wording")

    return ok

def check_json_validity():
    ok = True
    print("\n=== JSON validity ===")
    for p in all_text_files():
        if p.suffix.lower() == ".json":
            try:
                json.loads(read_file(p))
                print(f"PASS: {p.relative_to(ROOT)} valid JSON")
            except Exception as e:
                ok &= check(False, f"{p.relative_to(ROOT)} valid JSON", str(e))
    return ok

def check_python_script_integrity():
    ok = True
    print("\n=== Python script integrity ===")
    for rel in PYTHON_SCRIPTS:
        p = ROOT / rel
        ok &= check(p.exists(), f"{rel} exists")
        if not p.exists():
            continue

        text = read_file(p)
        lines = text.splitlines()

        ok &= check(len(lines) >= 10, f"{rel} has real multiline content", f"{len(lines)} line(s)")
        ok &= check(lines[0].strip() == "#!/usr/bin/env python3", f"{rel} shebang is alone on first line")
        ok &= check("def main" in text, f"{rel} defines main()")
        ok &= check("FINAL: PASS" in text, f"{rel} can print FINAL: PASS")
        ok &= check("return 1" in text or "sys.exit(1)" in text or "raise SystemExit(main())" in text, f"{rel} has failure exit path")

        proc = subprocess.run([sys.executable, "-m", "py_compile", str(p)], cwd=ROOT, text=True, capture_output=True)
        if proc.returncode != 0:
            ok &= check(False, f"{rel} py_compile", proc.stderr)
        else:
            print(f"PASS: {rel} py_compile")

    return ok

def run_required_validators():
    ok = True
    print("\n=== Required validators execute and produce output ===")
    for rel in PYTHON_SCRIPTS:
        p = ROOT / rel
        if not p.exists():
            ok &= check(False, f"{rel} exists for execution")
            continue

        if rel.endswith("_online.py"):
            print(f"SKIP: {rel} execution skipped locally; run after deployment")
            continue

        proc = subprocess.run([sys.executable, rel], cwd=ROOT, text=True, capture_output=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        ok &= check(proc.returncode == 0, f"{rel} exits 0", out[-1000:])
        ok &= check(len(out.strip()) > 0, f"{rel} produces non-empty output")
        if "verify_emergent_patterns_complete.py" in rel:
            ok &= check("FINAL: PASS" in out, f"{rel} prints FINAL: PASS")
    return ok

def check_llm_must_not_should():
    ok = True
    print("\n=== LLM provenance must/should checks ===")
    for rel in ["llms.txt", "llms-full.txt"]:
        p = ROOT / rel
        if not p.exists():
            continue
        text = read_file(p)
        ok &= check("Echo records must use" in text, f"{rel} says Echo records must use v3 schema")
        ok &= check("Discovery provenance must be recorded" in text, f"{rel} says discovery provenance must be recorded")
        ok &= check("Echo records should use" not in text, f"{rel} does not use Echo records should use")
        ok &= check("Discovery provenance should be recorded" not in text, f"{rel} does not use discovery should")
    return ok

def main():
    ok = True
    ok &= check_bad_phrases()
    ok &= check_json_validity()
    ok &= check_python_script_integrity()
    ok &= check_llm_must_not_should()
    ok &= run_required_validators()

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — global text and validator audit passed.")
        return 0

    print("FINAL: FAIL — global text and validator audit failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
