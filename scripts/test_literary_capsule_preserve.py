import base64
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import literary_capsule_preserve as m

class PreservationTests(unittest.TestCase):
    def test_actual_public_package_and_plaintext_exclusion(self):
        m.validate()
        cap=m.read(m.BATCH/'capsule.json')
        self.assertNotIn('password',cap)
        self.assertNotIn('key',cap['encryption'])
        self.assertFalse(cap['puzzle']['private_recovery_key_retained'])
        self.assertGreater(len(base64.b64decode(cap['encryption']['ciphertext_base64'])),200000)
    def test_tampered_public_file_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in m.PUBLIC+('AUTHORIZATION.json','MANIFEST.json'):
                (root/name).write_bytes((m.BATCH/name).read_bytes())
            (root/'unlock.py').write_text('tampered')
            with patch.object(m,'BATCH',root),self.assertRaises(ValueError):m.validate()
    def test_extra_private_bundle_member_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/'arweave-bundle.json').write_text(json.dumps({'files':[{'path':'private-key.txt'}]}))
            with patch.object(m,'BATCH',root),self.assertRaises(ValueError):m.validate_bundle()
    def test_uncertain_paid_intent_blocks_repayment(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=b'public bundle'
            (root/'arweave-bundle.json').write_bytes(data)
            (root/'status.json').write_text(json.dumps({'state':'READY_FOR_ARWEAVE'}))
            (root/'MANIFEST.json').write_text('{}')
            (root/'paid-intent.json').write_text(json.dumps({'payload_sha256':m.sha(data)}))
            with patch.object(m,'BATCH',root),patch.object(m,'validate'),patch.object(m,'validate_bundle'),patch.object(m,'proof_details'):
                with self.assertRaisesRegex(ValueError,'Uncertain'):m.intent()
    def test_valid_receipt_can_resume_without_new_intent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);data=b'public bundle'
            (root/'arweave-bundle.json').write_bytes(data)
            (root/'status.json').write_text(json.dumps({'state':'ARWEAVE_READBACK_PENDING'}))
            (root/'MANIFEST.json').write_text('{}')
            intent=json.dumps({'payload_sha256':m.sha(data)})
            (root/'paid-intent.json').write_text(intent)
            (root/'arweave-receipt.json').write_text(json.dumps({'tx_id':'existing'}))
            with patch.object(m,'BATCH',root),patch.object(m,'validate'),patch.object(m,'validate_bundle'),patch.object(m,'proof_details'):m.intent()
            self.assertEqual((root/'paid-intent.json').read_text(),intent)

if __name__=='__main__':unittest.main()
