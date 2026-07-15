#!/usr/bin/env python3
"""Deterministically generate Chronicle editions without rewriting routing policy."""

from chronicle_editions_v2 import main as generate_editions


def main() -> int:
    return generate_editions()


if __name__ == "__main__":
    raise SystemExit(main())
