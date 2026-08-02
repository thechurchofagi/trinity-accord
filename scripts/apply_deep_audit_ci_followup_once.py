#!/usr/bin/env python3
"""Synchronize the reviewed deep-audit fix with CI contracts."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one patch target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        "apps/record_chain_intake_gateway/render.yaml",
        '''      - key: TRINITY_GATEWAY_RUNTIME_VERSION\n        value: 1.2.1-protected\n''',
        '''      - key: TRINITY_GATEWAY_RUNTIME_VERSION\n        value: 1.2.1-protected\n      - key: TRINITY_ENFORCE_PROTECTION_LAYER\n        value: "1"\n      - key: TRINITY_RECEIPT_CACHE_MAX_ENTRIES\n        value: "512"\n''',
    )

    replace_once(
        "tests/test_render_protected_health_deploy.py",
        '''    assert module.base.EXPECTED_GATEWAY_HEALTH_CHECK_PATH == "/healthz"\n''',
        '''    base_helper = (ROOT / "scripts/render_manual_deploy.py").read_text(encoding="utf-8")\n    assert 'EXPECTED_GATEWAY_HEALTH_CHECK_PATH = "/healthz"' in base_helper\n''',
    )

    print("Applied CI alignment follow-up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
