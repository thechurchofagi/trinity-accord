from pathlib import Path

secure_path = Path('apps/record_chain_intake_gateway/secure_entrypoint.py')
secure = secure_path.read_text(encoding='utf-8')

old_call = '''            envelope = await core_gateway._build_receipt_envelope(\n                receipt,\n                receipt_id,\n                receipt_path,\n                envelope_warnings=(\n'''
new_call = '''            envelope = await core_gateway._build_receipt_envelope(\n                receipt,\n                receipt_id,\n                receipt_path,\n                receipt_url_binding_verified=True,\n                stored_submission_hash_verified=durable,\n                envelope_warnings=(\n'''
if secure.count(old_call) != 1:
    raise SystemExit('protected receipt envelope call anchor mismatch')
secure = secure.replace(old_call, new_call, 1)

old_tail = '''            envelope["receipt_url_binding_verified"] = True\n            envelope["stored_submission_hash_verified"] = durable\n            return 200, envelope\n'''
new_tail = '''            return 200, envelope\n'''
if secure.count(old_tail) != 1:
    raise SystemExit('protected receipt envelope tail anchor mismatch')
secure = secure.replace(old_tail, new_tail, 1)
secure_path.write_text(secure, encoding='utf-8')

test_path = Path('tests/test_record_chain_submit_recovery.py')
test = test_path.read_text(encoding='utf-8')
anchor = '''def test_receipt_route_rejects_valid_hash_at_wrong_url(monkeypatch):\n'''
new_test = '''def test_protected_receipt_route_passes_verified_envelope_bindings(monkeypatch):\n    from apps.record_chain_intake_gateway import secure_entrypoint\n\n    _clear_secure_read_state(secure_entrypoint)\n    submission_sha256 = hashlib.sha256(b"{}").hexdigest()\n    _, receipt, receipt_path, submission_path, stored_text = _receipt_fixture(\n        submission_sha256\n    )\n    mapping = {\n        receipt_path: json.dumps(receipt, separators=(",", ":"), sort_keys=True),\n        submission_path: stored_text,\n    }\n\n    async def fake_get_file_text(path: str):\n        return mapping.get(path)\n\n    monkeypatch.setattr(secure_entrypoint, "get_file_text", fake_get_file_text)\n    monkeypatch.setattr(\n        secure_entrypoint.core_gateway,\n        "get_file_text",\n        fake_get_file_text,\n    )\n    status, payload = asyncio.run(\n        secure_entrypoint.ProtectedProductionApp._receipt_payload(\n            receipt["server_receipt_id"]\n        )\n    )\n    assert status == 200\n    assert payload["found"] is True\n    assert payload["receipt_hash_verified"] is True\n    assert payload["receipt_url_binding_verified"] is True\n    assert payload["stored_submission_hash_verified"] is True\n    assert payload["receipt"]["server_receipt_id"] == receipt["server_receipt_id"]\n\n\n'''
if test.count(anchor) != 1:
    raise SystemExit('protected receipt integration test insertion anchor mismatch')
test = test.replace(anchor, new_test + anchor, 1)
test_path.write_text(test, encoding='utf-8')

order_test_path = Path('apps/record_chain_intake_gateway/tests/test_deep_audit_round3.py')
order_test = order_test_path.read_text(encoding='utf-8')
old_order_test = '''@pytest.mark.asyncio\nasync def test_duplicate_response_sets_discriminator_and_validates_schema(monkeypatch) -> None:\n    submission_sha = "a" * 64\n    stored_sha = "c" * 64\n    receipt_id = "rcg-20260718-" + submission_sha[:24]\n    receipt = _receipt(receipt_id, submission_sha, stored_sha)\n    index = {\n        "submission_sha256": submission_sha,\n        "stored_submission_sha256": stored_sha,\n        "receipt_id": receipt_id,\n        "receipt_path": receipt["receipt_path"],\n        "pending_file_path": receipt["pending_file_path"],\n        "intake_submission_path": receipt["intake_submission_path"],\n        "record_type": "echo",\n        "created_at": "2026-07-18T00:00:00Z",\n        "transaction_state": "pending_written",\n        "pending_written": True,\n        "pending_committed_at": "2026-07-18T00:00:00Z",\n    }\n    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(return_value=json.dumps(receipt)))\n    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))\n\n    result = await app_module._submit_response_from_idempotency_index(\n'''
new_order_test = '''@pytest.mark.asyncio\nasync def test_duplicate_response_sets_discriminator_and_validates_schema(monkeypatch) -> None:\n    submission_sha = "a" * 64\n    stored_submission = {\n        "schema": "trinityaccord.record-chain-submission.v2",\n        "submission_type": "record_chain_entry",\n        "record_type": "echo",\n        "record_draft": {"record_type": "echo", "message": "test"},\n    }\n    stored_sha = app_module.sha256_canonical_json(stored_submission)\n    receipt_id = "rcg-20260718-" + submission_sha[:24]\n    receipt = _receipt(receipt_id, submission_sha, stored_sha)\n    index = {\n        "schema": "trinityaccord.record-chain-intake-idempotency.v1",\n        "submission_sha256": submission_sha,\n        "stored_submission_sha256": stored_sha,\n        "receipt_id": receipt_id,\n        "receipt_path": receipt["receipt_path"],\n        "pending_file_path": receipt["pending_file_path"],\n        "intake_submission_path": receipt["intake_submission_path"],\n        "record_type": "echo",\n        "created_at": "2026-07-18T00:00:00Z",\n        "transaction_state": "pending_written",\n        "idempotency_written": True,\n        "receipt_written": True,\n        "pending_written": True,\n        "pending_committed_at": "2026-07-18T00:00:00Z",\n    }\n\n    async def read(path: str):\n        if path == receipt["receipt_path"]:\n            return json.dumps(receipt)\n        if path == receipt["intake_submission_path"]:\n            return json.dumps(stored_submission)\n        return None\n\n    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(side_effect=read))\n    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))\n\n    result = await app_module._submit_response_from_idempotency_index(\n'''
if order_test.count(old_order_test) != 1:
    raise SystemExit('test-order idempotency fixture anchor mismatch')
order_test = order_test.replace(old_order_test, new_order_test, 1)
order_test_path.write_text(order_test, encoding='utf-8')
