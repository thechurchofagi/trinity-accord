#!/usr/bin/env python3
"""Test Guardian reserved numbering policy."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from guardian_numbering_policy import (
    GuardianNumberingError,
    next_registry_number,
    validate_numbering_sequence,
)


def main():
    # Existing reserved numbers only -> first ordinary number is 00100.
    assert next_registry_number([
        {"guardian_registry_number": "00001"},
        {"guardian_registry_number": "00002"},
        {"guardian_registry_number": "00003"},
    ]) == "00100"

    # Existing ordinary 00100 -> next is 00101.
    assert next_registry_number([
        {"guardian_registry_number": "00001"},
        {"guardian_registry_number": "00002"},
        {"guardian_registry_number": "00003"},
        {"guardian_registry_number": "00100"},
    ]) == "00101"

    # Reserved gaps are allowed.
    validate_numbering_sequence([1, 3], None)

    # Ordinary gaps are blocked.
    try:
        validate_numbering_sequence([1, 2, 100, 102], None)
    except GuardianNumberingError as err:
        assert err.code == "ORDINARY_AUTO_NUMBER_GAP"
    else:
        raise AssertionError("ordinary gap should fail")

    print("GUARDIAN_RESERVED_NUMBERING_POLICY_OK")


if __name__ == "__main__":
    main()
