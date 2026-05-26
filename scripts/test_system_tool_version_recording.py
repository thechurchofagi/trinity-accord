#!/usr/bin/env python3
"""Test: Key .mjs verifiers must include toolchain provenance markers."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

# The shared module must define the provenance collector with required fields
SHARED_MODULE = ROOT / "scripts" / "toolchain_provenance.mjs"

# These scripts must import and use the shared module
CONSUMER_SCRIPTS = [
    ROOT / "scripts" / "verify-full-evidence-chain.mjs",
    ROOT / "scripts" / "verify-ots-time-anchor.mjs",
    ROOT / "scripts" / "verify-release-assets.mjs",
    ROOT / "scripts" / "download-nft-cars.mjs",
]

missing = []

# Check shared module has required markers
if not SHARED_MODULE.exists():
    missing.append("scripts/toolchain_provenance.mjs: file missing")
else:
    shared_text = SHARED_MODULE.read_text(encoding="utf-8")
    for token in ["collectToolchainProvenance", "node_version", "ImageVersion", "ImageOS"]:
        if token not in shared_text:
            missing.append(f"toolchain_provenance.mjs: missing {token}")

# Check each consumer script imports the shared module and uses toolchain_provenance
for path in CONSUMER_SCRIPTS:
    if not path.exists():
        missing.append(f"{path.name}: file missing")
        continue
    text = path.read_text(encoding="utf-8")
    if "collectToolchainProvenance" not in text:
        missing.append(f"{path.name}: missing collectToolchainProvenance import")
    if "toolchain_provenance" not in text:
        missing.append(f"{path.name}: missing toolchain_provenance field")

if missing:
    print("FAIL: report toolchain provenance missing:")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("SYSTEM_TOOL_VERSION_RECORDING_OK")
