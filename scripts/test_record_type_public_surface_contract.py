#!/usr/bin/env python3
"""Contract test: guardian_key_rotation is not in any active public surface."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))

from gateway.validation import ALLOWED_RECORD_TYPES, RESERVED_RECORD_TYPES

BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
SUBMISSION_SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"
OATH_POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"
FIELD_HELPER = ROOT / "api" / "record-chain-field-helper.v1.json"


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def kebab(rt: str) -> str:
    return rt.replace("_", "-")


def main():
    builder_text = BUILDER.read_text(encoding="utf-8")
    schema = json.loads(SUBMISSION_SCHEMA.read_text(encoding="utf-8"))
    oath = json.loads(OATH_POLICY.read_text(encoding="utf-8"))
    helper = json.loads(FIELD_HELPER.read_text(encoding="utf-8"))

    allowed = set(ALLOWED_RECORD_TYPES)
    reserved = set(RESERVED_RECORD_TYPES)

    # Reserved must not overlap allowed
    require(
        not (allowed & reserved),
        f"reserved record types must not be allowed: {sorted(allowed & reserved)}",
    )

    # Submission schema enum must not contain reserved
    schema_enum = set(schema["properties"]["record_type"]["enum"])
    require(
        not (schema_enum & reserved),
        f"reserved record types must not appear in submission schema enum: {sorted(schema_enum & reserved)}",
    )

    # Active oath types must not contain reserved
    active_oath_types = set(oath.get("formal_record_types_requiring_oath", []))
    require(
        not (active_oath_types & reserved),
        f"reserved record types must not appear in active oath types: {sorted(active_oath_types & reserved)}",
    )

    # Oath modules must not have reserved
    oath_modules = set((oath.get("record_type_modules") or {}).keys())
    require(
        not (oath_modules & reserved),
        f"reserved record types must not have active oath modules: {sorted(oath_modules & reserved)}",
    )

    # Builder must not have guardian-key-rotation in active command sets
    for rt in reserved:
        cmd = kebab(rt)

        # Not in RECORD_BUILD_COMMANDS_REQUIRING_KEY
        rbcrk_match = re.search(
            r"RECORD_BUILD_COMMANDS_REQUIRING_KEY\s*=\s*new Set\(\[(.*?)\]\)",
            builder_text,
            re.S,
        )
        if rbcrk_match:
            require(
                f'"{cmd}"' not in rbcrk_match.group(1),
                f"reserved type {rt} must not be in RECORD_BUILD_COMMANDS_REQUIRING_KEY",
            )

        # Not in FORMAL_RECORD_COMMANDS
        frc_match = re.search(
            r"FORMAL_RECORD_COMMANDS\s*=\s*new Set\(\[(.*?)\]\)",
            builder_text,
            re.S,
        )
        if frc_match:
            require(
                f'"{cmd}"' not in frc_match.group(1),
                f"reserved type {rt} must not be in FORMAL_RECORD_COMMANDS",
            )

        # Not in RECORD_TYPE_FIELDS
        rtf_match = re.search(
            r"const RECORD_TYPE_FIELDS\s*=\s*\{(.*?)\};",
            builder_text,
            re.S,
        )
        if rtf_match:
            require(
                f'"{cmd}"' not in rtf_match.group(1),
                f"reserved type {rt} must not appear as active RECORD_TYPE_FIELDS",
            )

        # Field helper must document GUARDIAN_KEY_ROTATION_RESERVED
        diag_codes = set(helper.get("diagnostic_code_help", {}).keys())
        require(
            "GUARDIAN_KEY_ROTATION_RESERVED" in diag_codes,
            "field helper must document GUARDIAN_KEY_ROTATION_RESERVED",
        )

    print("PASS: record type public surface contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
