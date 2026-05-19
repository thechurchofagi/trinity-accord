#!/usr/bin/env python3
"""Test homepage positioning and route wording."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.md"
GEN = ROOT / "scripts" / "generate_public_home_status.py"

def require(label, condition, failures):
    if condition:
        print(f"  ✅ {label}")
    else:
        print(f"  ❌ {label}")
        failures.append(label)

def main():
    index = INDEX.read_text(encoding="utf-8")
    gen = GEN.read_text(encoding="utf-8")
    failures = []

    require(
        "first positioning sentence says verifiable civilizational seed",
        "verifiable civilizational seed" in index,
        failures,
    )
    for word in ["discover", "verify", "critique", "preserve", "echo", "refuse"]:
        require(
            f"homepage contains {word}",
            word in index.lower(),
            failures,
        )

    require(
        "machine entry includes context-load-map",
        "/api/context-load-map.json" in index,
        failures,
    )
    require(
        "machine entry includes bitcoin-inscription-mirror-index",
        "/api/bitcoin-inscription-mirror-index.json" in index,
        failures,
    )

    require(
        "bitcoin inscription stack appears before public status",
        index.find('id="bitcoin-inscription-stack"') != -1
        and index.find('id="public-status-snapshot"') != -1
        and index.find('id="bitcoin-inscription-stack"') < index.find('id="public-status-snapshot"'),
        failures,
    )

    require(
        "status heading says evidence and ecosystem status",
        "Current evidence and ecosystem status" in index,
        failures,
    )

    require(
        "generated script uses Route selection remains required",
        "Route selection remains required" in gen,
        failures,
    )
    require(
        "generated script no longer uses generic Claim Gate remains required",
        "Claim Gate remains required" not in gen,
        failures,
    )

    require(
        "closing posture contains future discoverability",
        "Not recognition first, but future discoverability" in index,
        failures,
    )

    require(
        "ecosystem task card exists",
        "<h3>Ecosystem · 生态</h3>" in index,
        failures,
    )

    if failures:
        print(f"\n--- Results: {len(failures)} failed ---")
        return 1

    print("\n--- Results: all passed ---")
    return 0

if __name__ == "__main__":
    sys.exit(main())
