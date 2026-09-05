#!/usr/bin/env python3
"""Minimal, deterministic yq compatibility for Optimism's bundle builder.

The pinned Optimism sync script only invokes ``yq -r '.chain_id' FILE``.
Using Python's standard-library TOML parser avoids introducing an unpinned yq
binary into the proof toolchain while deliberately rejecting every other use.
"""
import pathlib
import sys
import tomllib


def main() -> None:
    if len(sys.argv) != 4 or sys.argv[1:3] != ["-r", ".chain_id"]:
        raise SystemExit("supported invocation: yq -r '.chain_id' FILE")
    value = tomllib.loads(pathlib.Path(sys.argv[3]).read_text())["chain_id"]
    if not isinstance(value, int) or value <= 0:
        raise SystemExit("chain_id must be a positive TOML integer")
    print(value)


if __name__ == "__main__":
    main()
