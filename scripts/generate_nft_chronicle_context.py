#!/usr/bin/env python3
"""Compatibility entrypoint for deterministic NFT Chronicle generation."""

from chronicle_editions_v2 import main as generate_editions
from update_chronicle_read_routes import main as update_read_routes


def main() -> int:
    result = generate_editions()
    if result != 0:
        return result
    return update_read_routes()


if __name__ == "__main__":
    raise SystemExit(main())
