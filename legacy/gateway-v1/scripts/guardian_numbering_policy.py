#!/usr/bin/env python3
"""Shared Guardian registry numbering policy.

Policy:
- 00001-00099 are special reserved Guardian numbers.
- Ordinary automatic registrations start at 00100.
- Ordinary automatic numbers must be gapless from 00100.
- Reserved range gaps are allowed unless policy later says otherwise.
"""

from __future__ import annotations

import re
from typing import Any


DEFAULT_NUMBERING = {
    "format": "five_digit_zero_padded",
    "ordinary_auto_start": "00100",
    "special_reserved_ranges": [
        {
            "start": "00001",
            "end": "00099",
            "purpose": "special_reserved_guardian_numbers",
        }
    ],
    "ordinary_auto_gapless_from": "00100",
    "global_gapless": False,
    "reserved_gaps_allowed": True,
}


class GuardianNumberingError(ValueError):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


def parse_registry_number(value: str, field: str = "guardian_registry_number") -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{5}", value):
        raise GuardianNumberingError(
            "BAD_REGISTRY_NUMBER",
            f"{field} must be a five-digit string",
            {field: value},
        )
    n = int(value)
    if n <= 0:
        raise GuardianNumberingError(
            "BAD_REGISTRY_NUMBER",
            f"{field} must not be 00000",
            {field: value},
        )
    return n


def format_registry_number(value: int) -> str:
    if not isinstance(value, int) or value <= 0 or value > 99999:
        raise GuardianNumberingError(
            "BAD_REGISTRY_NUMBER",
            "registry number integer out of range",
            {"value": value},
        )
    return f"{value:05d}"


def get_numbering(policy: dict | None) -> dict:
    if not policy:
        return dict(DEFAULT_NUMBERING)

    numbering = policy.get("numbering") or {}
    merged = dict(DEFAULT_NUMBERING)
    merged.update(numbering)

    if "special_reserved_ranges" not in numbering:
        merged["special_reserved_ranges"] = DEFAULT_NUMBERING["special_reserved_ranges"]

    return merged


def ordinary_auto_start(policy: dict | None) -> int:
    return parse_registry_number(
        get_numbering(policy).get("ordinary_auto_start", "00100"),
        "ordinary_auto_start",
    )


def ordinary_auto_gapless_from(policy: dict | None) -> int:
    numbering = get_numbering(policy)
    value = numbering.get(
        "ordinary_auto_gapless_from",
        numbering.get("ordinary_auto_start", "00100"),
    )
    return parse_registry_number(value, "ordinary_auto_gapless_from")


def reserved_ranges(policy: dict | None) -> list[tuple[int, int]]:
    ranges = []
    for item in get_numbering(policy).get("special_reserved_ranges", []):
        start = parse_registry_number(item.get("start"), "reserved_range.start")
        end = parse_registry_number(item.get("end"), "reserved_range.end")
        if end < start:
            raise GuardianNumberingError(
                "BAD_RESERVED_RANGE",
                "reserved range end is before start",
                item,
            )
        ranges.append((start, end))
    return ranges


def is_reserved_number(value: int, policy: dict | None) -> bool:
    return any(start <= value <= end for start, end in reserved_ranges(policy))


def registry_number_ints(registry_or_guardians: dict | list[dict]) -> list[int]:
    if isinstance(registry_or_guardians, dict):
        guardians = registry_or_guardians.get("guardians") or []
    else:
        guardians = registry_or_guardians

    numbers = []
    for entry in guardians:
        numbers.append(parse_registry_number(entry.get("guardian_registry_number")))
    return numbers


def validate_numbering_sequence(numbers: list[int], policy: dict | None = None) -> None:
    if len(numbers) != len(set(numbers)):
        raise GuardianNumberingError(
            "DUPLICATE_REGISTRY_NUMBER",
            "Duplicate Guardian registry number",
            {"numbers": numbers},
        )

    auto_start = ordinary_auto_start(policy)
    auto_gapless_from = ordinary_auto_gapless_from(policy)

    below_auto = sorted(n for n in numbers if n < auto_start)
    for n in below_auto:
        if not is_reserved_number(n, policy):
            raise GuardianNumberingError(
                "NON_RESERVED_NUMBER_BELOW_AUTO_START",
                "Number below ordinary_auto_start is not in reserved range",
                {
                    "number": format_registry_number(n),
                    "ordinary_auto_start": format_registry_number(auto_start),
                },
            )

    ordinary = sorted(n for n in numbers if n >= auto_start)
    if ordinary:
        expected = list(range(auto_gapless_from, max(ordinary) + 1))
        if ordinary != expected:
            raise GuardianNumberingError(
                "ORDINARY_AUTO_NUMBER_GAP",
                "Ordinary auto registry numbers must be gapless from ordinary_auto_gapless_from",
                {
                    "got": ordinary,
                    "expected": expected,
                    "ordinary_auto_gapless_from": format_registry_number(auto_gapless_from),
                },
            )


def next_registry_number(registry_or_guardians: dict | list[dict], policy: dict | None = None) -> str:
    numbers = registry_number_ints(registry_or_guardians)
    validate_numbering_sequence(numbers, policy)

    auto_start = ordinary_auto_start(policy)
    ordinary = [n for n in numbers if n >= auto_start]

    if not ordinary:
        return format_registry_number(auto_start)

    return format_registry_number(max(ordinary) + 1)




def classify_registry_number(value: str | int, policy: dict | None = None) -> str:
    """Classify a Guardian registry number under the active numbering policy.

    Returns one of:
    - ordinary_auto
    - special_reserved
    - non_reserved_below_auto_start
    """
    if isinstance(value, int):
        n = value
    else:
        n = parse_registry_number(value)

    if n >= ordinary_auto_start(policy):
        return "ordinary_auto"

    if is_reserved_number(n, policy):
        return "special_reserved"

    return "non_reserved_below_auto_start"


def special_reserved_range_label(policy: dict | None = None) -> str:
    ranges = reserved_ranges(policy)
    if not ranges:
        return ""
    return ", ".join(f"{format_registry_number(start)}-{format_registry_number(end)}" for start, end in ranges)


def count_ordinary_auto_listings_on_day(
    guardians: list[dict],
    listed_at: str,
    policy: dict | None = None,
) -> int:
    """Count active ordinary-auto Guardian listings on a specific UTC date.

    Special reserved entries such as 00001-00099 do not consume ordinary daily cap.
    Malformed entries are ignored here; registry validation should catch them elsewhere.
    """
    count = 0

    for entry in guardians:
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != "active":
            continue
        if entry.get("listed_at") != listed_at:
            continue

        number = entry.get("guardian_registry_number")
        if not isinstance(number, str):
            continue

        try:
            if classify_registry_number(number, policy) == "ordinary_auto":
                count += 1
        except GuardianNumberingError:
            continue

    return count

def numbering_error_to_decision(err: GuardianNumberingError) -> dict:
    return {
        "ok": False,
        "action": "blocked",
        "code": err.code,
        "message": err.message,
        **err.details,
    }
