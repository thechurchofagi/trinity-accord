"""Check published identity and the actual workflow's pre-payment recovery gate."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
BATCH = Path('research/paper-timestamps/2026-09-19-paper09')
spec = importlib.util.spec_from_file_location('paper_ots', ROOT / 'scripts/research_paper_ots.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class NinthPaperPreservationTests(unittest.TestCase):
    def test_targets_match_the_published_paper_and_guide(self):
        config = pipeline.read(ROOT / BATCH / 'targets.json')
        papers, count = pipeline.validate_config(ROOT / BATCH, config)
        self.assertEqual(count, 2)
        self.assertEqual([p['report'] for p in papers], ['TA-TR-2026-09'])
        self.assertEqual(papers[0]['doi'], '10.5281/zenodo.22844928')
        for item in papers[0]['pdfs']:
            data = (ROOT / 'research/learning-from-an-ai-claimant/published' / item['name']).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), (item['bytes'], item['sha256']))
        changed = copy.deepcopy(config)
        changed['papers'][0]['pdfs'][0]['sha256'] = '00' * 32
        with self.assertRaises(ValueError):
            pipeline.validate_config(ROOT / BATCH, changed)

    def test_actual_intent_gate_blocks_ambiguous_retry_and_allows_recorded_resume(self):
        workflow = (ROOT / '.github/workflows/research-paper-09-ots-arweave.yml').read_text()
        step = workflow.split('      - name: Persist a payload-bound intent before a new paid attempt\n', 1)[1]
        source = textwrap.dedent(step.split("          python3 - <<'PY'\n", 1)[1].split('\n          PY', 1)[0])
        env = dict(os.environ, GITHUB_RUN_ID='test-run', GITHUB_RUN_ATTEMPT='1')
        with tempfile.TemporaryDirectory() as temp:
            batch = Path(temp) / BATCH
            batch.mkdir(parents=True)
            (batch / 'arweave-bundle.json').write_text('{"test":"no network or payment"}\n')
            def attempt():
                return subprocess.run([sys.executable, '-c', source], cwd=temp, env=env, capture_output=True, text=True)
            self.assertEqual(attempt().returncode, 0)
            original = (batch / 'paid-intent.json').read_bytes()
            repeated = attempt()
            self.assertNotEqual(repeated.returncode, 0)
            self.assertIn('Uncertain prior paid attempt', repeated.stderr)
            self.assertEqual((batch / 'paid-intent.json').read_bytes(), original)
            (batch / 'arweave-receipt.json').write_text(json.dumps({'tx_id': 'recorded-test-transaction'}))
            self.assertEqual(attempt().returncode, 0)
            (batch / 'arweave-bundle.json').write_text('{"changed":true}\n')
            self.assertIn('Paid intent payload changed', attempt().stderr)


if __name__ == '__main__':
    unittest.main()
