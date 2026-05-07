#!/usr/bin/env python3
"""Final red-team regression: download-arweave workflow must fail closed and reject hashless verified archive commits."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / ".github" / "workflows" / "download-arweave.yml"
text = path.read_text(encoding="utf-8")

errors = []

if 'NO EXPECTED HASH' not in text:
    errors.append("workflow must explicitly reject missing expected hashes")

if 'if [ "$FAIL" -ne 0 ]' not in text:
    errors.append("workflow must exit non-zero when FAIL > 0")

if re.search(r'OK \(no expected hash\).*PASS=\$\(\(PASS \+ 1\)\)', text, re.DOTALL):
    errors.append("hashless downloads must not increment PASS")

if re.search(r'download_and_verify\s+"[^"]+"\s+"archive/[^"]+"\s+""', text):
    errors.append("download_and_verify must not write archive/ destinations with empty expected hash")

if 'dist/unverified-arweave' not in text and 'nft-recovery-package' in text:
    errors.append("hashless main recovery package must be moved to dist/unverified-arweave or given expected hash")

if "download_availability_only" not in text:
    errors.append("workflow must define download_availability_only for hashless availability-only downloads")

if re.search(r'download_and_verify\s+"[^"]+"\s+"dist/unverified-arweave/[^"]+"\s+""', text):
    errors.append("availability-only dist/unverified-arweave downloads must use download_availability_only, not download_and_verify")

if errors:
    print("DOWNLOAD_ARWEAVE_FAIL_CLOSED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("DOWNLOAD_ARWEAVE_FAIL_CLOSED_OK")
