#!/usr/bin/env python3
"""Final red-team regression: DAG verifier must honor CLI inputs and not reference undefined manifestItem."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "verify-dag-and-signed-cids.mjs"
text = path.read_text(encoding="utf-8")

errors = []

if "const args = process.argv.slice(2)" not in text:
    errors.append("script must parse process.argv")

if "RELEASE_TAG" not in text:
    errors.append("script must define RELEASE_TAG")

if "getReleaseByTag(RELEASE_TAG)" not in text:
    errors.append("script must use RELEASE_TAG in getReleaseByTag")

if "input_parameters" not in text or "release_tag" not in text:
    errors.append("DAG-CID-AUDIT report must include input_parameters.release_tag")

if re.search(r"\bmanifestItem\b", text):
    errors.append("generic manifestItem must not appear; use scoped digestManifestItem/mediaDigestManifestItem")

if "findDigestManifestItem" not in text and "digestManifestItem" not in text:
    errors.append("expected scoped digest manifest lookup helper/variable not found")

if "parseBoundedInt" not in text:
    errors.append("concurrency must be parsed with bounded integer validation")

if errors:
    print("VERIFY_DAG_MANIFEST_ITEM_DEFINED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("VERIFY_DAG_MANIFEST_ITEM_DEFINED_OK")
