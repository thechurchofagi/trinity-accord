#!/usr/bin/env python3
from pathlib import Path
import re
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]

EXCLUDED_DIRS = {
    ".git",
    "_site",
    "node_modules",
    "audit",
    "archive",
    "docs/legacy",
}

TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".yml", ".yaml", ".html", ".xml"
}

FORBIDDEN_PATTERNS = [
    "/echoes/digests/-",
    "/EVIDENCE-RELATIONSHIP-MAP.md",
    "/EVIDENCE-BACKUP-COVERAGE.md",
    "/archive_legacy_index_2025_09.md",
    "/downloads/arweave-bundle-verification.md",
    "/echoes/examples/critical-echo-template.md",
]

REQUIRED_LINKS = {
    "echoes/digests.md": [
        "/echoes/digests/2026-q2"
    ],
    "agent-echo.md": [
        "/EVIDENCE-RELATIONSHIP-MAP",
        "/EVIDENCE-BACKUP-COVERAGE"
    ],
    "start.md": [
        "/archive_legacy_index_2025_09"
    ],
    "status.md": [
        "/downloads/arweave-bundle-verification"
    ],
    "echoes/high-value-criteria.md": [
        "/echoes/examples/critical-echo-template/"
    ],
    "echoes/types.md": [
        "/echoes/examples/critical-echo-template/"
    ],
}

TARGET_FILES = {
    "/EVIDENCE-RELATIONSHIP-MAP": "EVIDENCE-RELATIONSHIP-MAP.md",
    "/EVIDENCE-BACKUP-COVERAGE": "EVIDENCE-BACKUP-COVERAGE.md",
    "/archive_legacy_index_2025_09": "archive_legacy_index_2025_09.md",
    "/downloads/arweave-bundle-verification": "downloads/arweave-bundle-verification.md",
    "/echoes/examples/critical-echo-template/": "echoes/examples/critical-echo-template.md",
    "/echoes/digests/2026-q2": "echoes/digests/2026-q2.md",
}

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

def is_excluded(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    for part in rel.parts:
        if part in EXCLUDED_DIRS:
            return True
    return False

def active_text_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS and not is_excluded(path):
            yield path

def parse_front_matter(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm

def check_forbidden_patterns():
    ok = True
    print("=== Forbidden active link patterns ===")
    for file in active_text_files():
        text = file.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in text:
                ok &= check(False, f"{file.relative_to(ROOT)} does not contain {pattern}", pattern)
    if ok:
        print("PASS: no forbidden active link patterns")
    return ok

def check_required_links():
    ok = True
    print("\n=== Required link replacements ===")
    for rel, links in REQUIRED_LINKS.items():
        ok &= check(exists(rel), f"{rel} exists")
        if not exists(rel):
            continue
        text = read(rel)
        for link in links:
            ok &= check(link in text, f"{rel} contains {link}")
    return ok

def check_target_sources():
    ok = True
    print("\n=== Target source files ===")
    for route, rel in TARGET_FILES.items():
        ok &= check(exists(rel), f"target for {route} exists: {rel}")
        if not exists(rel):
            continue
        path = p(rel)
        fm = parse_front_matter(path)
        if route == "/echoes/digests/2026-q2":
            ok &= check(bool(fm), f"{rel} has front matter")
            if fm:
                ok &= check(fm.get("permalink", "").rstrip("/") == route.rstrip("/"), f"{rel} permalink matches {route}")
        elif route == "/echoes/examples/critical-echo-template/":
            ok &= check(bool(fm), f"{rel} has front matter")
            if fm:
                ok &= check(fm.get("permalink", "").rstrip("/") == route.rstrip("/"), f"{rel} permalink matches {route}")
        else:
            if fm:
                got = fm.get("permalink", "")
                ok &= check(got.rstrip("/") == route.rstrip("/"), f"{rel} permalink matches {route}")
            else:
                print(f"WARN: {rel} has no front matter; verify Jekyll serves {route} online")
    return ok

def check_sitemap_digest():
    ok = True
    print("\n=== Sitemap digest route ===")
    if exists("sitemap.xml"):
        text = read("sitemap.xml")
        if "https://www.trinityaccord.org/echoes/digests/2026-q2" in text:
            ok &= check(exists("echoes/digests/2026-q2.md"), "sitemap 2026-q2 route has source file")
        ok &= check("/echoes/digests/-" not in text, "sitemap has no digest placeholder")
    else:
        print("SKIP: sitemap.xml not present locally")
    return ok

def check_no_md_links_in_known_files():
    ok = True
    print("\n=== Known file .md link scan ===")
    known_files = [
        "agent-echo.md",
        "start.md",
        "status.md",
        "echoes/high-value-criteria.md",
        "echoes/types.md",
        "echoes/digests.md",
    ]
    md_link_re = re.compile(r"\]\((/[^)]+\.md)(#[^)]+)?\)")
    for rel in known_files:
        if not exists(rel):
            continue
        text = read(rel)
        for m in md_link_re.finditer(text):
            ok &= check(False, f"{rel} has public .md link", m.group(0))
    if ok:
        print("PASS: known files contain no public .md links")
    return ok

def run_existing_checks():
    ok = True
    print("\n=== Existing checks ===")
    for rel in [
        "scripts/check_consistency.py",
        "scripts/verify_repository_hygiene_routes.py",
        "scripts/validate_echo_records.py",
    ]:
        if not exists(rel):
            print(f"SKIP: {rel} missing")
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
    ok &= check_forbidden_patterns()
    ok &= check_required_links()
    ok &= check_target_sources()
    ok &= check_sitemap_digest()
    ok &= check_no_md_links_in_known_files()
    ok &= run_existing_checks()

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — link hygiene validation passed.")
        return 0
    print("FINAL: FAIL — link hygiene validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
