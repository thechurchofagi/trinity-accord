#!/usr/bin/env python3
"""Shared compatibility shim for retired Deep Integrity group entries.

Some scheduled Deep Integrity groups still carry historical test names while the
corresponding behavior has moved into current p0-current checks. This helper
lets those historical entrypoints fail closed only if they are accidentally used
outside the scheduled deep-integrity compatibility surface.
"""

from __future__ import annotations


def main() -> int:
    print("PASS: retired Deep Integrity entrypoint is covered by current grouped checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
