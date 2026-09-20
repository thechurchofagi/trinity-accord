import pathlib,sys,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
import publication_common as c
class T(unittest.TestCase):
    def test_guardrails(self):
        self.assertEqual(c.PREVIOUS_RECORD,22852885); self.assertIn(c.PREVIOUS_RECORD,c.PROTECTED); self.assertEqual(c.VERSION,'1.1')
        with self.assertRaises(RuntimeError): c.validate_record_id(c.PREVIOUS_RECORD)
if __name__=='__main__': unittest.main(verbosity=2)
