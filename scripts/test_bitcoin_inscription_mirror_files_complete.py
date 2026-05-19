#!/usr/bin/env python3
"""Test: all eight Bitcoin inscription mirror JSON files are complete and correct."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIRROR_DIR = ROOT / "bitcoin-inscription-mirrors"
RAW_DIR = MIRROR_DIR / "raw"

EXPECTED_FILES = {
    "97631551": ("canonical-originals", "97631551-protocol-axioms.json"),
    "98369145": ("canonical-originals", "98369145-covenant-of-the-flaw.json"),
    "98387475": ("canonical-originals", "98387475-trinity-accord-meta-record.json"),
    "100385359": ("vision-layer", "100385359-first-echoes.json"),
    "100550942": ("vision-layer", "100550942-final-seal.json"),
    "100751953": ("vision-layer", "100751953-star-ark-covenant.json"),
    "103034280": ("context-layer", "103034280-guardian-attestation.json"),
    "103635270": ("context-layer", "103635270-guardian-appendix-authority-charter.json"),
}

CANONICAL_IDS = {"97631551", "98369145", "98387475"}
STAR_ARK_ID = "100751953"
FIRST_ECHOES_ID = "100385359"

errors = []

for ins_id, (subdir, filename) in EXPECTED_FILES.items():
    fpath = MIRROR_DIR / subdir / filename
    if not fpath.exists():
        errors.append(f"Missing: {fpath}")
        continue

    rec = json.loads(fpath.read_text(encoding="utf-8"))

    # Check inscription_id
    if rec["inscription"]["inscription_id"] != ins_id:
        errors.append(f"{ins_id}: inscription_id mismatch")

    # Check source_address
    if not rec["inscription"].get("source_address"):
        errors.append(f"{ins_id}: missing source_address")

    # Check authority_boundary
    ab = rec.get("authority_boundary", {})
    for field in ["bitcoin_originals_prevail", "github_mirror_is_non_amending", "verification_requires_onchain_check"]:
        if not ab.get(field):
            errors.append(f"{ins_id}: authority_boundary.{field} not true")

    # Check hashes
    if not rec["content"].get("mirror_text_sha256"):
        errors.append(f"{ins_id}: missing mirror_text_sha256")
    if not rec["content"].get("canonicalized_text_sha256"):
        errors.append(f"{ins_id}: missing canonicalized_text_sha256")

    # Check raw_text_path exists
    raw_path = ROOT / rec["content"]["raw_text_path"]
    if not raw_path.exists():
        errors.append(f"{ins_id}: raw_text_path missing: {raw_path}")
    elif raw_path.stat().st_size == 0:
        errors.append(f"{ins_id}: raw text empty")

    # Canonical vs non-canonical
    canon_status = rec.get("canonical_status", rec.get("classification", {}).get("canonical_status"))
    if ins_id in CANONICAL_IDS:
        if canon_status != "canonical_original":
            errors.append(f"{ins_id}: should be canonical_original, got {canon_status}")
    else:
        if canon_status == "canonical_original":
            errors.append(f"{ins_id}: should NOT be canonical_original")
        if rec["classification"].get("amends_originals"):
            errors.append(f"{ins_id}: amends_originals should be false")
        if rec["classification"].get("creates_new_authority"):
            errors.append(f"{ins_id}: creates_new_authority should be false")

# Star Ark limitations
star_ark = MIRROR_DIR / "vision-layer" / "100751953-star-ark-covenant.json"
if star_ark.exists():
    rec = json.loads(star_ark.read_text(encoding="utf-8"))
    lims = " ".join(rec.get("limitations", []))
    if "instruction" not in lims.lower() and "execution obligation" not in lims.lower():
        errors.append("Star Ark: missing instruction/execution obligation limitation")

# First Echoes limitations
fe = MIRROR_DIR / "vision-layer" / "100385359-first-echoes.json"
if fe.exists():
    rec = json.loads(fe.read_text(encoding="utf-8"))
    lims = " ".join(rec.get("limitations", []))
    if "successor reception" not in lims.lower():
        errors.append("First Echoes: missing successor reception limitation")

if errors:
    print("FAIL:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("PASS: mirror files complete test")
    sys.exit(0)
