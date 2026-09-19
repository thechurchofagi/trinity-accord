import importlib.util
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('paper_ots', ROOT / 'scripts/research_paper_ots.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PaperProofTests(unittest.TestCase):
    def test_followup_batch_is_wired_to_the_guarded_workflow(self):
        workflow = (ROOT / '.github/workflows/research-paper-07-08-ots-arweave.yml').read_text()
        original_workflow = (ROOT / '.github/workflows/research-paper-ots-arweave.yml').read_text()
        batch = 'research/paper-timestamps/2026-09-19'
        self.assertIn(f'python3 scripts/research_paper_ots.py lifecycle --batch {batch}', workflow)
        self.assertIn(f'python3 scripts/research_paper_ots.py upload --batch {batch}', workflow)
        self.assertIn('ARWEAVE_MINIMUM_REMAINING_AR', workflow)
        self.assertIn('ARWEAVE_ROLLING_30_DAY_SPEND_LIMIT_AR', workflow)
        self.assertNotIn(batch, original_workflow)

    def test_followup_targets_match_public_readback_receipts(self):
        batch = ROOT / 'research/paper-timestamps/2026-09-19'
        config = module.read(batch / 'targets.json')
        papers, pdf_count = module.validate_config(batch, config)
        self.assertEqual([paper['report'] for paper in papers], ['TA-TR-2026-07', 'TA-TR-2026-08'])
        self.assertEqual(pdf_count, 4)

        tampered = copy.deepcopy(config)
        tampered['papers'][1]['pdfs'][0]['sha256'] = '00' * 32
        with self.assertRaises(ValueError):
            module.validate_config(batch, tampered)

    @unittest.skipUnless(importlib.util.find_spec('opentimestamps'), 'OTS is installed in the dedicated paper workflow')
    def test_detached_proof_must_match_published_bytes(self):
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
        from opentimestamps.core.notary import PendingAttestation, BitcoinBlockHeaderAttestation
        from opentimestamps.core.serialize import BytesSerializationContext
        expected = 'ab' * 32
        stamp = Timestamp(bytes.fromhex(expected))
        stamp.attestations.add(PendingAttestation('https://a.pool.opentimestamps.org'))
        proof = DetachedTimestampFile(OpSHA256(), stamp)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'paper.ots'
            ctx = BytesSerializationContext()
            proof.serialize(ctx)
            path.write_bytes(ctx.getbytes())
            self.assertEqual(module.proof_details(path, expected), ([], 1))
            with self.assertRaises(ValueError):
                module.proof_details(path, 'cd' * 32)
            stamp.attestations.add(BitcoinBlockHeaderAttestation(900000))
            ctx = BytesSerializationContext()
            proof.serialize(ctx)
            path.write_bytes(ctx.getbytes())
            self.assertEqual(module.proof_details(path, expected), ([900000], 1))

    def test_pending_proofs_cannot_reach_paid_uploader(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)
            module.write(batch / 'status.json', {'state': 'WAITING'})
            with patch.object(module, 'BATCH', batch), patch.object(module.subprocess, 'run') as runner:
                with self.assertRaises(SystemExit):
                    module.upload()
                runner.assert_not_called()

    def test_completed_batch_does_not_repeat_paid_upload(self):
        with tempfile.TemporaryDirectory() as directory:
            batch = Path(directory)
            module.write(batch / 'status.json', {'state': 'ARWEAVE_READBACK_PASS'})
            with patch.object(module, 'BATCH', batch), patch.object(module.subprocess, 'run') as runner:
                module.upload()
                runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
