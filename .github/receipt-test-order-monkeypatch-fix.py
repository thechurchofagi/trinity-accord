from pathlib import Path

path = Path('apps/record_chain_intake_gateway/tests/test_deep_audit_round3.py')
text = path.read_text(encoding='utf-8')
old = '''    monkeypatch.setattr(app_module, "get_file_text", AsyncMock(side_effect=read))\n    monkeypatch.setattr(app_module, "get_file_sha", AsyncMock(return_value="pending-sha"))\n\n    result = await app_module._submit_response_from_idempotency_index(\n'''
new = '''    from apps.record_chain_intake_gateway import secure_entrypoint\n\n    file_text_mock = AsyncMock(side_effect=read)\n    file_sha_mock = AsyncMock(return_value="pending-sha")\n    monkeypatch.setattr(app_module, "get_file_text", file_text_mock)\n    monkeypatch.setattr(app_module, "get_file_sha", file_sha_mock)\n    monkeypatch.setattr(secure_entrypoint, "get_file_text", file_text_mock)\n\n    result = await app_module._submit_response_from_idempotency_index(\n'''
if text.count(old) != 1:
    raise SystemExit('production-order dependency patch anchor mismatch')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
