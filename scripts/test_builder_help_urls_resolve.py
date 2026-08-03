#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
HELP = ROOT / "docs" / "record-chain-builder-help.md"
EXPECTED_BASE = "https://www.trinityaccord.org/docs/record-chain-builder-help/#"


def verified_builder_runtime() -> str:
    manifest = json.loads(
        (ROOT / "api" / "record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )
    canonical = manifest["canonical_builder"]
    layers = [
        (BUILDER, canonical),
        (
            ROOT / "downloads" / "record-chain-builder-recovery.mjs",
            canonical["recovery_wrapper"],
        ),
        (
            ROOT / "downloads" / "record-chain-builder-core.mjs",
            canonical["core"],
        ),
    ]
    texts: list[str] = []
    for path, contract in layers:
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == contract["sha256"], (
            f"Builder layer manifest sha256 is stale: {path.name}"
        )
        assert len(raw) == contract["size_bytes"], (
            f"Builder layer manifest size_bytes is stale: {path.name}"
        )
        texts.append(raw.decode("utf-8"))
    return "\n".join(texts)


def main() -> None:
    text = verified_builder_runtime()
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
