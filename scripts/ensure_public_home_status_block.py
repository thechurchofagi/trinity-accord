#!/usr/bin/env python3
"""Ensure index.md contains the generated public status block markers.

The homepage patcher replaces an existing BEGIN/END block. Some homepage
revisions may remove that block while keeping the public-status pipeline active.
This helper restores a minimal placeholder so the patcher can replace it with
canonical generated content during CI and Pages builds.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_MD = ROOT / "index.md"
BEGIN = "<!-- BEGIN GENERATED PUBLIC STATUS -->"
END = "<!-- END GENERATED PUBLIC STATUS -->"
PLACEHOLDER = f"""{BEGIN}
<!-- Placeholder restored by scripts/ensure_public_home_status_block.py. -->
{END}"""

ANCHOR_RE = re.compile(
    r'(<section id="public-production-phase"[\s\S]*?</section>)',
    re.MULTILINE,
)


def main() -> int:
    text = INDEX_MD.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        print("generated public status block already present")
        return 0

    match = ANCHOR_RE.search(text)
    if match:
        insert_at = match.end()
        text = text[:insert_at] + "\n\n" + PLACEHOLDER + "\n" + text[insert_at:]
    else:
        # Fallback: place it after front matter rather than failing the build.
        fm = re.match(r"(?s)^---\n.*?\n---\n", text)
        insert_at = fm.end() if fm else 0
        text = text[:insert_at] + "\n" + PLACEHOLDER + "\n" + text[insert_at:]

    INDEX_MD.write_text(text, encoding="utf-8")
    print("restored generated public status block placeholder")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
