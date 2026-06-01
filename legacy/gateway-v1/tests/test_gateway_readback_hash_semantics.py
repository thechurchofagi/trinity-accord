#!/usr/bin/env python3
"""agent_readback_sha256 must match agent_readback."""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_gateway_payload_semantics import validate

READBACK = "I confirm this readback text is what I actually submit and it must match its sha256 digest."

payload = {
    "requested_archive_kind": "agent_declared_echo_archive",
    "counts_toward_home": {
        "verifiability": False,
        "reception": True
    },
    "what_i_checked": ["fixture"],
    "limitations": ["fixture"],
    "authority_boundary": {
        "bitcoin_originals_remain_final": True,
        "does_not_amend_bitcoin_originals": True,
        "does_not_override_bitcoin_originals": True
    },
    "agent_integrity_declaration": {
        "verification_oath": {
            "agent_readback": READBACK,
            "agent_readback_sha256": hashlib.sha256(READBACK.encode("utf-8")).hexdigest()
        }
    }
}

errors = validate(payload)
if any("agent_readback_sha256 does not match" in e for e in errors):
    print("FAIL: correct readback hash rejected")
    print(errors)
    sys.exit(1)

bad = {
    "requested_archive_kind": "agent_declared_echo_archive",
    "counts_toward_home": {
        "verifiability": False,
        "reception": True
    },
    "what_i_checked": ["fixture"],
    "limitations": ["fixture"],
    "authority_boundary": {
        "bitcoin_originals_remain_final": True,
        "does_not_amend_bitcoin_originals": True,
        "does_not_override_bitcoin_originals": True
    },
    "agent_integrity_declaration": {
        "verification_oath": {
            "agent_readback": READBACK,
            "agent_readback_sha256": "0" * 64
        }
    }
}

errors = validate(bad)
if not any("agent_readback_sha256 does not match" in e for e in errors):
    print("FAIL: mismatched readback hash was not rejected")
    print(errors)
    sys.exit(1)

print("PASS: readback hash semantic validation works")
