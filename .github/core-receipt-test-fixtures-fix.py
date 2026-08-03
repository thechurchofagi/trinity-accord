from pathlib import Path

path = Path('apps/record_chain_intake_gateway/tests/test_receipt.py')
text = path.read_text(encoding='utf-8')

old_helper = '''    def _make_receipt(self, receipt_id: str = "rcg-20260613-abcdef123456") -> dict:\n        """Build a test receipt with valid receipt_sha256."""\n        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256\n        receipt = {"server_receipt_id": receipt_id, "accepted": True}\n        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)\n        return receipt\n'''
new_helper = '''    def _make_stored_submission(self) -> dict:\n        return {\n            "schema": "trinityaccord.record-chain-submission.v2",\n            "submission_type": "record_chain_entry",\n            "record_type": "echo",\n            "record_draft": {"record_type": "echo", "message": "test"},\n        }\n\n    def _make_receipt(self, receipt_id: str = "rcg-20260613-abcdef123456") -> dict:\n        """Build a canonically path-bound receipt and matching stored hash."""\n        from apps.record_chain_intake_gateway.gateway.canonical import sha256_canonical_json\n        from apps.record_chain_intake_gateway.gateway.receipts import compute_receipt_sha256\n\n        stored_submission = self._make_stored_submission()\n        receipt = {\n            "server_receipt_id": receipt_id,\n            "accepted": True,\n            "record_type": "echo",\n            "receipt_path": (\n                f"record-chain/intake/receipts/2026/06/{receipt_id}.receipt.json"\n            ),\n            "intake_submission_path": (\n                f"record-chain/intake/submissions/2026/06/{receipt_id}.submission.json"\n            ),\n            "pending_file_path": f"record-chain/pending/{receipt_id}.echo.pending.json",\n            "stored_submission_sha256": sha256_canonical_json(stored_submission),\n        }\n        receipt["receipt_sha256"] = compute_receipt_sha256(receipt)\n        return receipt\n\n    def _durable_reader(self, receipt: dict, *, tampered: bool = False):\n        stored_submission = self._make_stored_submission()\n        if tampered:\n            stored_submission = {**stored_submission, "tampered": True}\n\n        async def read(path: str):\n            if path == receipt["receipt_path"]:\n                return json.dumps(receipt)\n            if path == receipt["intake_submission_path"]:\n                return json.dumps(stored_submission)\n            return None\n\n        return read\n'''
if text.count(old_helper) != 1:
    raise SystemExit('receipt helper anchor mismatch')
text = text.replace(old_helper, new_helper)

old_first = '''        with patch(\n            "apps.record_chain_intake_gateway.app.get_file_text",\n            new_callable=AsyncMock,\n            return_value=json.dumps(receipt),\n        ):\n            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")\n        assert resp.status_code == 200\n        body = resp.json()\n        assert body["receipt"]["server_receipt_id"] == "rcg-20260613-abcdef123456"\n        assert body["receipt_hash_verified"] is True\n'''
new_first = '''        with patch(\n            "apps.record_chain_intake_gateway.app.get_file_text",\n            new=AsyncMock(side_effect=self._durable_reader(receipt)),\n        ):\n            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")\n        assert resp.status_code == 200\n        body = resp.json()\n        assert body["receipt"]["server_receipt_id"] == "rcg-20260613-abcdef123456"\n        assert body["receipt_hash_verified"] is True\n        assert body["receipt_url_binding_verified"] is True\n        assert body["stored_submission_hash_verified"] is True\n'''
if text.count(old_first) != 1:
    raise SystemExit('durable receipt test anchor mismatch')
text = text.replace(old_first, new_first)

old_second = '''        with patch(\n            "apps.record_chain_intake_gateway.app.get_file_text",\n            new_callable=AsyncMock,\n            return_value=json.dumps(receipt),\n        ):\n            client.get("/record-chain/receipt/rcg-20260613-abcdef123456")\n        assert _receipt_store.get("rcg-20260613-abcdef123456") is not None\n'''
new_second = '''        with patch(\n            "apps.record_chain_intake_gateway.app.get_file_text",\n            new=AsyncMock(side_effect=self._durable_reader(receipt)),\n        ):\n            client.get("/record-chain/receipt/rcg-20260613-abcdef123456")\n        assert _receipt_store.get("rcg-20260613-abcdef123456") is not None\n'''
if text.count(old_second) != 1:
    raise SystemExit('durable cache test anchor mismatch')
text = text.replace(old_second, new_second)

old_success_read = '''        async def read(path: str):\n            if path.startswith("record-chain/intake/receipts/"):\n                return json.dumps(receipt)\n            return None\n'''
new_success_read = '''        async def read(path: str):\n            if path == receipt["receipt_path"]:\n                return json.dumps(receipt)\n            if path == receipt["intake_submission_path"]:\n                return json.dumps(self._make_stored_submission())\n            return None\n'''
if text.count(old_success_read) != 1:
    raise SystemExit('success reader anchor mismatch')
text = text.replace(old_success_read, new_success_read)

old_invalid_read = '''        async def read(path: str):\n            if path.startswith("record-chain/intake/receipts/"):\n                return json.dumps(receipt)\n            if path.startswith("record-chain/receipt-status/"):\n                return json.dumps({"schema": "wrong"})\n            return None\n'''
new_invalid_read = '''        async def read(path: str):\n            if path == receipt["receipt_path"]:\n                return json.dumps(receipt)\n            if path == receipt["intake_submission_path"]:\n                return json.dumps(self._make_stored_submission())\n            if path.startswith("record-chain/receipt-status/"):\n                return json.dumps({"schema": "wrong"})\n            return None\n'''
if text.count(old_invalid_read) != 1:
    raise SystemExit('invalid final-status reader anchor mismatch')
text = text.replace(old_invalid_read, new_invalid_read)

insert_anchor = '''    def test_durable_hit_updates_cache(self, client: TestClient) -> None:\n'''
new_test = '''    def test_durable_stored_submission_hash_mismatch_fails_closed(self, client: TestClient) -> None:\n        receipt = self._make_receipt()\n        with patch(\n            "apps.record_chain_intake_gateway.app.get_file_text",\n            new=AsyncMock(side_effect=self._durable_reader(receipt, tampered=True)),\n        ):\n            resp = client.get("/record-chain/receipt/rcg-20260613-abcdef123456")\n        assert resp.status_code == 500\n        assert resp.json()["detail"]["code"] == "RECEIPT_STORED_SUBMISSION_HASH_MISMATCH"\n\n'''
if text.count(insert_anchor) != 1:
    raise SystemExit('new tamper test insertion anchor mismatch')
text = text.replace(insert_anchor, new_test + insert_anchor)

cache_assert_anchor = '''        assert any(\n            w.get("code") == "RECEIPT_DURABLE_LOOKUP_FAILED_RETURNED_MEMORY_CACHE"\n            for w in body.get("envelope_warnings", [])\n        )\n'''
cache_assert_new = cache_assert_anchor + '''        assert body["receipt_url_binding_verified"] is True\n        assert body["stored_submission_hash_verified"] is False\n'''
if text.count(cache_assert_anchor) != 1:
    raise SystemExit('cache binding assertion anchor mismatch')
text = text.replace(cache_assert_anchor, cache_assert_new)

path.write_text(text, encoding='utf-8')
