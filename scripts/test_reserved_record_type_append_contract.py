#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from trinity_record_chain import require_not_reserved_record_type

def require(cond, msg):
    if not cond:
        raise AssertionError(msg)

def main():
    bad = {"record_type": "guardian_key_rotation"}
    try:
        require_not_reserved_record_type(bad)
    except ValueError as exc:
        require("reserved" in str(exc).lower(), str(exc))
    else:
        raise AssertionError("guardian_key_rotation must be rejected by internal append layer")

    ok = {"record_type": "guardian_retirement"}
    require_not_reserved_record_type(ok)

    print("PASS: reserved record type append contract")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
