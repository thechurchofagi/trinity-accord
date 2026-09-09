#!/usr/bin/env python3
"""Apply narrow Registry metadata compatibility shims to pinned OP source."""

from __future__ import annotations

import argparse
import hashlib
import pathlib


PATCHES = {
    "op-core/superchain/types.go": (
        "a5ce3dcf86ea9ca8ed95a6ec7055b070eeb8091db523242be481b652a7439f71",
        'type ChainConfig struct {\n\tName                 string       `toml:"name"`\n',
        (
            'type ChainConfig struct {\n'
            '\tName                 string       `toml:"name"`\n'
            '\tSuperchainLevel      uint64       `toml:"superchain_level"`\n'
        ),
    ),
    "op-core/superchain/superchain.go": (
        "4d4b9cb0a28602369b37bf3fe9eafe95502c6b17b683c24f9554b189f0d1b59d",
        'type Superchain struct {\n\tName                   string         `toml:"name"`\n',
        (
            'type Superchain struct {\n'
            '\tName                   string         `toml:"name"`\n'
            '\tProtocolVersionsAddr   common.Address `toml:"protocol_versions_addr"`\n'
        ),
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch_text(text: str, needle: str, replacement: str) -> str:
    if replacement in text:
        raise ValueError("pinned OP source is already patched")
    if text.count(needle) != 1:
        raise ValueError("pinned OP source layout changed")
    return text.replace(needle, replacement, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("optimism_root", type=pathlib.Path)
    args = parser.parse_args()
    for relative, (expected_hash, needle, replacement) in PATCHES.items():
        path = args.optimism_root / relative
        raw = path.read_bytes()
        if sha256(raw) != expected_hash:
            raise SystemExit(f"pinned OP {relative} hash mismatch; refusing compatibility patch")
        patched = patch_text(raw.decode(), needle, replacement)
        path.write_text(patched)
        print(f"[OP REGISTRY COMPAT PATCH] path={path} patched_sha256={sha256(path.read_bytes())}")


if __name__ == "__main__":
    main()
