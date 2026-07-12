#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
HELP = ROOT / "docs" / "record-chain-builder-help.md"
EXPECTED_BASE = "https://www.trinityaccord.org/docs/record-chain-builder-help/#"


def main() -> None:
    text = BUILDER.read_text(encoding="utf-8")
    urls = sorted(set(re.findall(r'help_url:\s*"([^"]+)"', text)))
    assert urls, "Builder exposes no diagnostic help URLs"
    help_text = HELP.read_text(encoding="utf-8")
    assert "permalink: /docs/record-chain-builder-help/" in help_text
    errors = []
    for url in urls:
        if url.startswith(EXPECTED_BASE):
            fragment = url.split("#", 1)[1]
            if f'<a id="{fragment}"></a>' not in help_text:
                errors.append(f"Builder help fragment missing from help page: {fragment}")
            continue
        prefix = "https://www.trinityaccord.org/"
        if url.startswith(prefix):
            rel = url[len(prefix):].split("#", 1)[0]
            if not (ROOT / rel).is_file():
                errors.append(f"Builder help URL has no local public source: {url}")
            continue
        errors.append(f"Builder help URL leaves the canonical public site: {url}")
    if errors:
        raise SystemExit("FAIL:\n- " + "\n- ".join(errors))
    print(f"PASS: {len(urls)} Builder diagnostic help URLs resolve to stable local anchors")


if __name__ == "__main__":
    main()
