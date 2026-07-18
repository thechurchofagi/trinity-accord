#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps/record_chain_intake_gateway/app.py"
TEST = ROOT / "apps/record_chain_intake_gateway/tests/test_deep_audit_round3.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one target, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    APP,
    '''# In-memory receipt store (ephemeral; resets on restart)
_receipt_store: dict[str, dict[str, Any]] = {}
''',
    '''# In-memory receipt store (ephemeral; resets on restart). Dry-run receipts
# remain readable only in this process and are explicitly marked non-durable.
_receipt_store: dict[str, dict[str, Any]] = {}
_ephemeral_receipt_ids: set[str] = set()
''',
)
replace_once(
    APP,
    '''    # Cache only receipts that became durable. A dry-run receipt is returned
    # in the immediate response but must not masquerade as retrievable intake.
    if _WRITE_MODE == "github_contents_pending":
        _receipt_store[receipt_id] = receipt_data
''',
    '''    # Cache durable receipts and preserve immediate dry-run readback without
    # presenting the latter as durable repository intake.
    _receipt_store[receipt_id] = receipt_data
    if _WRITE_MODE == "github_contents_pending":
        _ephemeral_receipt_ids.discard(receipt_id)
    else:
        _ephemeral_receipt_ids.add(receipt_id)
''',
)
replace_once(
    APP,
    '''            _receipt_store[receipt_id] = receipt  # update cache
            return await _build_receipt_envelope(receipt, receipt_id, receipt_path)
''',
    '''            _receipt_store[receipt_id] = receipt  # update cache
            _ephemeral_receipt_ids.discard(receipt_id)
            return await _build_receipt_envelope(receipt, receipt_id, receipt_path)
''',
)
replace_once(
    APP,
    '''            _receipt_store.pop(receipt_id, None)  # evict corrupt cache
            raise HTTPException(
''',
    '''            _receipt_store.pop(receipt_id, None)  # evict corrupt cache
            _ephemeral_receipt_ids.discard(receipt_id)
            raise HTTPException(
''',
)
replace_once(
    APP,
    '''        if backend_error is None:
            return await _build_receipt_envelope(cached, receipt_id, receipt_path)
        # Backend errored but we have verified cache — return cache with warning
        # Don't mutate the receipt; put warnings in the envelope instead.
        envelope_warnings = [{
            "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
            "message": "Durable receipt storage could not be read; a hash-verified in-memory cache entry was returned.",
            "receipt_path": receipt_path,
            "retryable": True,
        }]
        return await _build_receipt_envelope(cached, receipt_id, receipt_path, envelope_warnings=envelope_warnings)
''',
    '''        envelope_warnings: list[dict[str, Any]] = []
        if receipt_id in _ephemeral_receipt_ids:
            envelope_warnings.append({
                "code": "RECEIPT_NON_DURABLE_DRY_RUN",
                "message": "This hash-verified receipt exists only in process memory because the submission used dry-run mode; it is not durable intake.",
                "receipt_path": receipt_path,
                "retryable": False,
            })
        if backend_error is None:
            return await _build_receipt_envelope(
                cached,
                receipt_id,
                receipt_path,
                envelope_warnings=envelope_warnings or None,
            )
        # Backend errored but we have verified cache — return cache with warning.
        # Don't mutate the receipt; put warnings in the envelope instead.
        envelope_warnings.append({
            "code": "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE",
            "message": "Durable receipt storage could not be read; a hash-verified in-memory cache entry was returned.",
            "receipt_path": receipt_path,
            "retryable": True,
        })
        return await _build_receipt_envelope(
            cached,
            receipt_id,
            receipt_path,
            envelope_warnings=envelope_warnings,
        )
''',
)
replace_once(
    TEST,
    '''    assert data["created_pending_records"] == []
    assert data["receipt_id"] not in app_module._receipt_store
''',
    '''    assert data["created_pending_records"] == []
    assert data["receipt_id"] in app_module._receipt_store
    retrieved = client.get(f"/record-chain/receipt/{data['receipt_id']}")
    assert retrieved.status_code == 200
    assert any(
        warning.get("code") == "RECEIPT_NON_DURABLE_DRY_RUN"
        for warning in retrieved.json().get("envelope_warnings", [])
        if isinstance(warning, dict)
    )
''',
)
print("DEEP_AUDIT_ROUND3_DRY_RUN_CACHE_FIXED")
