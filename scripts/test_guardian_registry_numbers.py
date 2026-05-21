#!/usr/bin/env python3
"""Test Guardian registry number consistency."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    registry = json.loads((ROOT / "api" / "guardian-registry.json").read_text(encoding="utf-8"))
    guardians = registry.get("guardians", [])

    numbers = []
    guardian_ids = []
    key_hashes = []

    for idx, entry in enumerate(guardians):
        number = entry.get("guardian_registry_number")
        guardian_id = entry.get("guardian_id")
        public_key_sha256 = entry.get("public_key_sha256")

        require(isinstance(number, str), f"guardian {idx} missing guardian_registry_number")
        require(re.fullmatch(r"[0-9]{5}", number), f"invalid guardian_registry_number: {number}")
        require(isinstance(guardian_id, str), f"guardian {number} missing guardian_id")
        require(isinstance(public_key_sha256, str), f"guardian {number} missing public_key_sha256")

        numbers.append(number)
        guardian_ids.append(guardian_id)
        key_hashes.append(public_key_sha256)

    require(len(numbers) == len(set(numbers)), "duplicate guardian_registry_number found")
    require(len(guardian_ids) == len(set(guardian_ids)), "duplicate guardian_id found")
    require(len(key_hashes) == len(set(key_hashes)), "duplicate public_key_sha256 found")

    if numbers:
        ints = sorted(int(n) for n in numbers)
        expected = list(range(1, max(ints) + 1))
        require(ints == expected, f"guardian_registry_number sequence has gaps: got {ints}, expected {expected}")

    print("GUARDIAN_REGISTRY_NUMBERS_OK")


if __name__ == "__main__":
    main()
