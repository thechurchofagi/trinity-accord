#!/usr/bin/env python3
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from capture_ethereum_beacon_finality import execution_hash, parse_providers


def main():
    value = {"data": {"message": {"body": {"execution_payload": {"block_hash": "0xAB"}}}}}
    assert execution_hash(value) == "0xab"
    assert len(parse_providers([])) == 2
    try:
        parse_providers(["only=https://example.com"])
    except ValueError:
        pass
    else:
        raise AssertionError("single-provider finality must fail closed")
    try:
        parse_providers(["../escape=https://one.example", "two=https://two.example"])
    except ValueError:
        pass
    else:
        raise AssertionError("provider names must not escape the evidence directory")
    print("ethereum beacon finality capture tests: PASS")


if __name__ == "__main__":
    main()
