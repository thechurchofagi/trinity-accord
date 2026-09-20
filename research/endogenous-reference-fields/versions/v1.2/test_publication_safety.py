#!/usr/bin/env python3
import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import publication_common as c

class Safety(unittest.TestCase):
    def test_version_lineage_constants(self):
        self.assertEqual(c.REPORT,'TA-TR-2026-10')
        self.assertEqual(c.VERSION,'1.2')
        self.assertEqual(c.PREVIOUS_VERSION,'1.1')
        self.assertEqual(c.PREVIOUS_RECORD,22854705)
        self.assertEqual(c.CONCEPT_RECORD,22852884)
        self.assertIn(c.PREVIOUS_RECORD,c.PROTECTED)
        self.assertIn(22852885,c.PROTECTED)
    def test_prior_records_cannot_be_target_records(self):
        for rid in (c.PREVIOUS_RECORD,22852885,c.CONCEPT_RECORD):
            with self.assertRaises(RuntimeError):
                c.validate_record_id(rid)
if __name__=='__main__':
    unittest.main(verbosity=2)
