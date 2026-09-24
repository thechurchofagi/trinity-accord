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
    def check_gate(self, *, paid=True, resume=False, mismatch=False, branch='main', limit='1', malformed=False, cost='1'):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'record-chain').mkdir()
            ledger = root / 'record-chain/arweave-wallet-ledger.json'
            entries = [{'status': 'paid', 'kind': 'research_paper_ots_archive',
                        'paid_at': datetime.now(timezone.utc).isoformat(), 'tx_id':'prior', 'winston':cost,
                        'source_path':'research/paper-timestamps/prior/arweave-receipt.json'}] if paid else []
            ledger.write_text('invalid' if malformed else json.dumps({'entries': entries}))
            batch = root / 'batch'
            batch.mkdir()
            targets = {'paper_count':1, 'papers':[{'report':'TA-TR-2026-15','doi':'10.5281/zenodo.22934654'}]}
            (batch / 'targets.json').write_text(json.dumps(targets))
            prior = root / 'research/paper-timestamps/prior'
            prior.mkdir(parents=True)
            (prior / 'targets.json').write_text(json.dumps(targets))
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

    def test_daily_allowance_does_not_apply_to_papers(self):
        rc, out, status = self.check_gate()
        self.assertEqual(rc, 0)
        self.assertEqual(out, 'allowed=true\n')
        self.assertFalse(status['daily_limit_applies'])

    def test_unused_allowance_can_reach_existing_guard(self):
        rc, out, _ = self.check_gate(paid=False)
        self.assertEqual((rc, out), (0, 'allowed=true\n'))

    def test_same_transaction_readback_does_not_need_another_allowance(self):
        rc, out, status = self.check_gate(resume=True)
        self.assertEqual((rc, out), (0, 'allowed=true\n'))
        self.assertTrue(status['recorded_transaction_resume'])

    def test_payload_mismatch_and_invalid_ledger_fail_closed(self):
        for kwargs in ({'resume': True, 'mismatch': True}, {'malformed': True}, {'cost': 'unknown'}):
            with self.subTest(kwargs=kwargs):
                rc, out, _ = self.check_gate(**kwargs)
                self.assertNotEqual(rc, 0)
                self.assertEqual(out, '')

    def test_main_branch_and_cumulative_budget_still_apply(self):
        for kwargs in ({'branch': 'feature'}, {'cost': '100000000000'}):
            with self.subTest(kwargs=kwargs):
                rc, out, _ = self.check_gate(**kwargs)
                self.assertEqual((rc, out), (0, 'allowed=false\n'))

    def test_old_daily_environment_does_not_block_papers(self):
        for limit in ('0', '1', '2'):
            rc, out, _ = self.check_gate(limit=limit)
            self.assertEqual((rc, out), (0, 'allowed=true\n'))

    def test_existing_transaction_can_resume_at_budget_ceiling(self):
        rc, out, _ = self.check_gate(resume=True, cost='100000000000')
        self.assertEqual((rc, out), (0, 'allowed=true\n'))


if __name__ == '__main__':
    unittest.main()
