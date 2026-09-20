"""Exercise scheduling without network requests, keys or paid uploads."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/research_arweave_allowance.mjs'


class AllowanceTests(unittest.TestCase):
    def check_gate(self, *, paid=True, resume=False, mismatch=False, branch='main', limit='1', malformed=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'record-chain').mkdir()
            ledger = root / 'record-chain/arweave-wallet-ledger.json'
            entries = [{'status': 'paid', 'kind': 'research_paper_ots_archive',
                        'paid_at': datetime.now(timezone.utc).isoformat()}] if paid else []
            ledger.write_text('invalid' if malformed else json.dumps({'entries': entries}))
            batch = root / 'batch'
            batch.mkdir()
            (batch / 'status.json').write_text('{"state":"READY_FOR_ARWEAVE"}')
            (batch / 'arweave-bundle.json').write_bytes(b'fixed payload')
            if resume:
                (batch / 'arweave-receipt.json').write_text(json.dumps({
                    'tx_id': 'existing-transaction',
                    'payload_sha256': 'wrong' if mismatch else hashlib.sha256(b'fixed payload').hexdigest(),
                }))
            output = root / 'output'
            env = {**os.environ, 'NODE_OPTIONS': '', 'GITHUB_OUTPUT': str(output),
                   'GITHUB_STEP_SUMMARY': str(root / 'summary'), 'GITHUB_REF_NAME': branch,
                   'ARWEAVE_DAILY_RESEARCH_PAPER_OTS_UPLOAD_LIMIT': limit}
            result = subprocess.run(['node', str(SCRIPT), str(batch)], cwd=root, env=env,
                                    text=True, capture_output=True, timeout=10)
            self.assertEqual(json.loads((batch / 'status.json').read_text())['state'], 'READY_FOR_ARWEAVE')
            scheduling = batch / 'scheduling-status.json'
            return result.returncode, output.read_text() if output.exists() else '', (
                json.loads(scheduling.read_text()) if scheduling.exists() else {})

    def test_exhausted_allowance_defers_without_claiming_completion(self):
        rc, out, status = self.check_gate()
        self.assertEqual(rc, 0)
        self.assertEqual(out, 'allowed=false\n')
        self.assertEqual(status['state'], 'DEFERRED_DAILY_ALLOWANCE')

    def test_unused_allowance_can_reach_existing_guard(self):
        rc, out, _ = self.check_gate(paid=False)
        self.assertEqual((rc, out), (0, 'allowed=true\n'))

    def test_same_transaction_readback_does_not_need_another_allowance(self):
        rc, out, status = self.check_gate(resume=True)
        self.assertEqual((rc, out), (0, 'allowed=true\n'))
        self.assertTrue(status['recorded_transaction_resume'])

    def test_payload_mismatch_and_invalid_ledger_fail_closed(self):
        for kwargs in ({'resume': True, 'mismatch': True}, {'malformed': True}, {'limit': '2'}):
            with self.subTest(kwargs=kwargs):
                rc, out, _ = self.check_gate(**kwargs)
                self.assertNotEqual(rc, 0)
                self.assertEqual(out, '')

    def test_non_main_and_zero_allowance_do_not_start_paid_uploads(self):
        for kwargs in ({'branch': 'feature'}, {'limit': '0'}):
            with self.subTest(kwargs=kwargs):
                rc, out, _ = self.check_gate(paid=False, **kwargs)
                self.assertEqual((rc, out), (0, 'allowed=false\n'))


if __name__ == '__main__':
    unittest.main()
