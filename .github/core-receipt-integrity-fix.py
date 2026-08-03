from pathlib import Path

app_path = Path('apps/record_chain_intake_gateway/app.py')
app = app_path.read_text(encoding='utf-8')

anchor = '''def _record_chain_record_sha256(record: dict[str, Any]) -> str:\n    """Recompute the canonical Record-Chain record hash (newline included)."""\n'''
helper = '''def _verify_receipt_route_binding(\n    receipt: dict[str, Any],\n    *,\n    receipt_id: str,\n    receipt_path: str,\n) -> None:\n    """Bind a receipt body to the requested core-app route and canonical paths."""\n    if not isinstance(receipt, dict):\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_NOT_OBJECT",\n                "message": "Receipt JSON root is not an object.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    if receipt.get("server_receipt_id") != receipt_id:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_ID_BINDING_INVALID",\n                "message": "Receipt server_receipt_id does not match the requested receipt ID.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    if receipt.get("receipt_path") != receipt_path:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_PATH_BINDING_INVALID",\n                "message": "Receipt receipt_path does not match its canonical durable path.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    record_type = receipt.get("record_type")\n    if not isinstance(record_type, str) or record_type not in ALLOWED_RECORD_TYPES:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_RECORD_TYPE_INVALID",\n                "message": "Receipt record_type is not an accepted formal record type.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    match = re.fullmatch(r"rcg-(\\d{4})(\\d{2})\\d{2}-[a-f0-9]{12}(?:[a-f0-9]{12})?", receipt_id)\n    if match is None:\n        raise HTTPException(status_code=500, detail={"code": "RECEIPT_ID_BINDING_INVALID"})\n    date_prefix = f"{match.group(1)}/{match.group(2)}"\n    expected_submission_path = (\n        f"record-chain/intake/submissions/{date_prefix}/{receipt_id}.submission.json"\n    )\n    expected_pending_path = f"record-chain/pending/{receipt_id}.{record_type}.pending.json"\n    if receipt.get("intake_submission_path") != expected_submission_path:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_SUBMISSION_PATH_BINDING_INVALID",\n                "message": "Receipt intake_submission_path is not canonically bound.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    if receipt.get("pending_file_path") != expected_pending_path:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_PENDING_PATH_BINDING_INVALID",\n                "message": "Receipt pending_file_path is not canonically bound.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n\n\nasync def _verify_receipt_stored_submission(\n    receipt: dict[str, Any],\n    *,\n    receipt_id: str,\n    receipt_path: str,\n) -> None:\n    """Re-read and canonical-hash the persisted submission referenced by a receipt."""\n    submission_path = receipt.get("intake_submission_path")\n    expected_sha256 = receipt.get("stored_submission_sha256")\n    if not isinstance(submission_path, str) or not submission_path:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_PATH_MISSING",\n                "message": "Receipt does not identify a persisted submission path.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    if not isinstance(expected_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", expected_sha256):\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_HASH_INVALID",\n                "message": "Receipt stored_submission_sha256 is missing or invalid.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n            },\n        )\n    submission_text = await get_file_text(submission_path)\n    if submission_text is None:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_MISSING",\n                "message": "Receipt points to a persisted submission that is not visible.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n                "submission_path": submission_path,\n            },\n        )\n    try:\n        stored_submission = parse_json_strict(submission_text)\n    except Exception as exc:\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_INVALID_JSON",\n                "message": f"Persisted submission is not strict JSON: {exc}",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n                "submission_path": submission_path,\n            },\n        ) from exc\n    if not isinstance(stored_submission, dict):\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_NOT_OBJECT",\n                "message": "Persisted submission JSON root is not an object.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n                "submission_path": submission_path,\n            },\n        )\n    actual_sha256 = sha256_canonical_json(stored_submission)\n    if not hmac.compare_digest(actual_sha256, expected_sha256):\n        raise HTTPException(\n            status_code=500,\n            detail={\n                "code": "RECEIPT_STORED_SUBMISSION_HASH_MISMATCH",\n                "message": "Persisted submission canonical SHA-256 does not match the immutable receipt.",\n                "receipt_id": receipt_id,\n                "receipt_path": receipt_path,\n                "submission_path": submission_path,\n            },\n        )\n\n\n'''
if app.count(anchor) != 1:
    raise SystemExit('record hash anchor mismatch')
app = app.replace(anchor, helper + anchor)

old_sig = '''async def _build_receipt_envelope(\n    receipt: dict[str, Any],\n    receipt_id: str,\n    receipt_path: str,\n    envelope_warnings: list[str | dict[str, Any]] | None = None,\n) -> dict[str, Any]:\n'''
new_sig = '''async def _build_receipt_envelope(\n    receipt: dict[str, Any],\n    receipt_id: str,\n    receipt_path: str,\n    *,\n    receipt_url_binding_verified: bool,\n    stored_submission_hash_verified: bool,\n    envelope_warnings: list[str | dict[str, Any]] | None = None,\n) -> dict[str, Any]:\n'''
if app.count(old_sig) != 1:
    raise SystemExit('envelope signature mismatch')
app = app.replace(old_sig, new_sig)

old_result = '''        "receipt_path": receipt_path,\n        "receipt_hash_verified": True,\n        "final_status": {\n'''
new_result = '''        "receipt_path": receipt_path,\n        "receipt_hash_verified": True,\n        "receipt_url_binding_verified": receipt_url_binding_verified,\n        "stored_submission_hash_verified": stored_submission_hash_verified,\n        "final_status": {\n'''
if app.count(old_result) != 1:
    raise SystemExit('envelope result mismatch')
app = app.replace(old_result, new_result)

old_durable = '''            _cache_receipt(receipt_id, receipt, ephemeral=False)\n            return await _build_receipt_envelope(receipt, receipt_id, receipt_path)\n'''
new_durable = '''            _verify_receipt_route_binding(\n                receipt,\n                receipt_id=receipt_id,\n                receipt_path=receipt_path,\n            )\n            await _verify_receipt_stored_submission(\n                receipt,\n                receipt_id=receipt_id,\n                receipt_path=receipt_path,\n            )\n            _cache_receipt(receipt_id, receipt, ephemeral=False)\n            return await _build_receipt_envelope(\n                receipt,\n                receipt_id,\n                receipt_path,\n                receipt_url_binding_verified=True,\n                stored_submission_hash_verified=True,\n            )\n'''
if app.count(old_durable) != 1:
    raise SystemExit('durable receipt return mismatch')
app = app.replace(old_durable, new_durable)

old_cache_hash = '''        hash_ok, hash_err = verify_receipt_sha256(cached)\n        if not hash_ok:\n'''
new_cache_hash = '''        hash_ok, hash_err = verify_receipt_sha256(cached)\n        if not hash_ok:\n'''
if app.count(old_cache_hash) != 1:
    raise SystemExit('cache hash anchor mismatch')
# Route binding is added after the corrupt-cache branch so corrupt entries are still evicted first.

old_after_corrupt = '''                },\n            )\n        envelope_warnings: list[dict[str, Any]] = []\n'''
new_after_corrupt = '''                },\n            )\n        _verify_receipt_route_binding(\n            cached,\n            receipt_id=receipt_id,\n            receipt_path=receipt_path,\n        )\n        envelope_warnings: list[dict[str, Any]] = []\n'''
if app.count(old_after_corrupt) != 1:
    raise SystemExit('cache route-binding insertion mismatch')
app = app.replace(old_after_corrupt, new_after_corrupt)

old_no_backend = '''        if backend_error is None:\n            return await _build_receipt_envelope(\n                cached,\n                receipt_id,\n                receipt_path,\n                envelope_warnings=envelope_warnings or None,\n            )\n'''
new_no_backend = '''        if backend_error is None:\n            if receipt_id not in _ephemeral_receipt_ids:\n                envelope_warnings.append({\n                    "code": "RECEIPT_DURABLE_ARTIFACT_NOT_VISIBLE_RETURNED_MEMORY_CACHE",\n                    "message": "The durable receipt artifact was not visible; a route-bound, hash-verified memory cache entry was returned without stored-submission verification.",\n                    "receipt_path": receipt_path,\n                    "retryable": True,\n                })\n            return await _build_receipt_envelope(\n                cached,\n                receipt_id,\n                receipt_path,\n                receipt_url_binding_verified=True,\n                stored_submission_hash_verified=False,\n                envelope_warnings=envelope_warnings or None,\n            )\n'''
if app.count(old_no_backend) != 1:
    raise SystemExit('cache no-backend return mismatch')
app = app.replace(old_no_backend, new_no_backend)

old_backend_return = '''        return await _build_receipt_envelope(\n            cached,\n            receipt_id,\n            receipt_path,\n            envelope_warnings=envelope_warnings,\n        )\n'''
new_backend_return = '''        return await _build_receipt_envelope(\n            cached,\n            receipt_id,\n            receipt_path,\n            receipt_url_binding_verified=True,\n            stored_submission_hash_verified=False,\n            envelope_warnings=envelope_warnings,\n        )\n'''
if app.count(old_backend_return) != 1:
    raise SystemExit('cache backend-error return mismatch')
app = app.replace(old_backend_return, new_backend_return)

app_path.write_text(app, encoding='utf-8')

test_path = Path('apps/record_chain_intake_gateway/tests/test_deep_audit_round3.py')
test = test_path.read_text(encoding='utf-8')
old_assertion = '''    assert cache_warning["message"]\n    Draft202012Validator(_load_schema("record-chain-receipt-response.v1.json")).validate(payload)\n'''
new_assertion = '''    assert cache_warning["message"]\n    assert payload["receipt_url_binding_verified"] is True\n    assert payload["stored_submission_hash_verified"] is False\n    Draft202012Validator(_load_schema("record-chain-receipt-response.v1.json")).validate(payload)\n'''
if test.count(old_assertion) != 1:
    raise SystemExit('cache fallback test anchor mismatch')
test = test.replace(old_assertion, new_assertion)

test_path.write_text(test, encoding='utf-8')
