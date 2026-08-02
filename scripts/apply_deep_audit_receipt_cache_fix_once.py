#!/usr/bin/env python3
"""Bound the process-local receipt cache discovered by the deep audit."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one patch target, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


def load_json(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path}: expected JSON object")
    return value


def write_json(path: str, value: dict) -> None:
    (ROOT / path).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    app_path = "apps/record_chain_intake_gateway/app.py"
    replace_once(
        app_path,
        '''# In-memory receipt store (ephemeral; resets on restart). Dry-run receipts\n# remain readable only in this process and are explicitly marked non-durable.\n_receipt_store: dict[str, dict[str, Any]] = {}\n_ephemeral_receipt_ids: set[str] = set()\n''',
        '''# In-memory receipt store (ephemeral; resets on restart). Durable receipts\n# remain authoritative in Git; this cache is bounded so a long-lived process\n# cannot retain every historical receipt forever. Dry-run receipts remain\n# explicitly non-durable and may be evicted at the same bounded capacity.\n_MAX_RECEIPT_CACHE_ENTRIES = max(\n    1, int(os.environ.get("TRINITY_RECEIPT_CACHE_MAX_ENTRIES", "512"))\n)\n_receipt_store: dict[str, dict[str, Any]] = {}\n_ephemeral_receipt_ids: set[str] = set()\n\n\ndef _cache_receipt(\n    receipt_id: str,\n    receipt: dict[str, Any],\n    *,\n    ephemeral: bool,\n) -> None:\n    """Insert or refresh one receipt and evict the oldest cache entries."""\n    _receipt_store.pop(receipt_id, None)\n    _receipt_store[receipt_id] = receipt\n    if ephemeral:\n        _ephemeral_receipt_ids.add(receipt_id)\n    else:\n        _ephemeral_receipt_ids.discard(receipt_id)\n\n    while len(_receipt_store) > _MAX_RECEIPT_CACHE_ENTRIES:\n        oldest_receipt_id = next(iter(_receipt_store))\n        _receipt_store.pop(oldest_receipt_id, None)\n        _ephemeral_receipt_ids.discard(oldest_receipt_id)\n''',
    )

    replace_once(
        app_path,
        '''    # Cache durable receipts and preserve immediate dry-run readback without\n    # presenting the latter as durable repository intake.\n    _receipt_store[receipt_id] = receipt_data\n    if _WRITE_MODE == "github_contents_pending":\n        _ephemeral_receipt_ids.discard(receipt_id)\n    else:\n        _ephemeral_receipt_ids.add(receipt_id)\n''',
        '''    # Cache durable receipts and preserve immediate dry-run readback without\n    # presenting the latter as durable repository intake.\n    _cache_receipt(\n        receipt_id,\n        receipt_data,\n        ephemeral=_WRITE_MODE != "github_contents_pending",\n    )\n''',
    )

    replace_once(
        app_path,
        '''            _receipt_store[receipt_id] = receipt  # update cache\n            _ephemeral_receipt_ids.discard(receipt_id)\n''',
        '''            _cache_receipt(receipt_id, receipt, ephemeral=False)\n''',
    )

    replace_once(
        app_path,
        '''        "record_draft_max_bytes": info["record_draft_max_bytes"],\n        "max_text_field_chars": info["max_text_field_chars"],\n''',
        '''        "record_draft_max_bytes": info["record_draft_max_bytes"],\n        "max_text_field_chars": info["max_text_field_chars"],\n        "receipt_cache_max_entries": _MAX_RECEIPT_CACHE_ENTRIES,\n''',
    )

    replace_once(
        "render.yaml",
        '''      - key: TRINITY_ENFORCE_PROTECTION_LAYER\n        value: "1"\n''',
        '''      - key: TRINITY_ENFORCE_PROTECTION_LAYER\n        value: "1"\n      - key: TRINITY_RECEIPT_CACHE_MAX_ENTRIES\n        value: "512"\n''',
    )

    replace_once(
        "scripts/render_manual_deploy.py",
        '''    "TRINITY_ENFORCE_PROTECTION_LAYER": "1",\n''',
        '''    "TRINITY_ENFORCE_PROTECTION_LAYER": "1",\n    "TRINITY_RECEIPT_CACHE_MAX_ENTRIES": "512",\n''',
    )

    policy = load_json("api/gateway-rate-limit-policy.v1.json")
    implementation = policy["implementation_status"]
    implementation["receipt_cache_maximum_entries"] = 512
    implementation["receipt_cache_oldest_entry_eviction"] = True
    implementation["durable_receipts_remain_repository_authoritative"] = True
    write_json("api/gateway-rate-limit-policy.v1.json", policy)

    test_path = ROOT / "tests/test_gateway_production_protection_guard.py"
    text = test_path.read_text(encoding="utf-8")
    marker = '''\ndef test_machine_contract_describes_layered_fail_closed_health() -> None:\n'''
    if text.count(marker) != 1:
        raise SystemExit("test insertion marker mismatch")
    addition = '''\ndef test_receipt_cache_is_bounded_and_cleans_ephemeral_index() -> None:\n    result = _run_isolated(\n        """\n        from apps.record_chain_intake_gateway import app as gateway\n\n        gateway._receipt_store.clear()\n        gateway._ephemeral_receipt_ids.clear()\n        maximum = gateway._MAX_RECEIPT_CACHE_ENTRIES\n        for index in range(maximum + 25):\n            receipt_id = f'rcg-test-{index:04d}'\n            gateway._cache_receipt(\n                receipt_id,\n                {'server_receipt_id': receipt_id},\n                ephemeral=True,\n            )\n        assert len(gateway._receipt_store) == maximum\n        assert len(gateway._ephemeral_receipt_ids) == maximum\n        assert 'rcg-test-0000' not in gateway._receipt_store\n        assert 'rcg-test-0000' not in gateway._ephemeral_receipt_ids\n\n        newest = f'rcg-test-{maximum + 24:04d}'\n        gateway._cache_receipt(\n            newest,\n            {'server_receipt_id': newest, 'durable': True},\n            ephemeral=False,\n        )\n        assert newest in gateway._receipt_store\n        assert newest not in gateway._ephemeral_receipt_ids\n        assert len(gateway._receipt_store) == maximum\n        """\n    )\n    assert result.returncode == 0, result.stdout + result.stderr\n\n'''
    test_path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")

    print("Applied bounded receipt-cache fix.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
