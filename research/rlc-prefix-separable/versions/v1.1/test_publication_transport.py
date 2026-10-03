"""Confirm empty DELETE responses without retrying or accepting unverified state."""
import json,unittest
from publication_run import ConfirmedDeleteClient

class Fake:
    def __init__(self,still_present=False):self.calls=[];self.still_present=still_present
    def request(self,path,method='GET',data=None,**kw):
        self.calls.append((method,path))
        if method=='DELETE':raise json.JSONDecodeError('empty successful response','',0)
        return [{'id':'file-abc'}] if self.still_present else []

class TransportTests(unittest.TestCase):
    def test_empty_response_accepts_only_confirmed_removal_and_never_redeletes(self):
        f=Fake();c=ConfirmedDeleteClient(f,23118189)
        self.assertIsNone(c.request('/deposit/depositions/23118189/files/file-abc','DELETE'))
        self.assertEqual([method for method,path in f.calls],['DELETE','GET'])
    def test_file_still_present_is_failure(self):
        f=Fake(True);c=ConfirmedDeleteClient(f,23118189)
        with self.assertRaisesRegex(RuntimeError,'not confirmed'):c.request('/deposit/depositions/23118189/files/file-abc','DELETE')
    def test_predecessor_delete_is_rejected_before_any_request(self):
        f=Fake();c=ConfirmedDeleteClient(f,23118189)
        with self.assertRaisesRegex(RuntimeError,'outside'):c.request('/deposit/depositions/23103274/files/file-abc','DELETE')
        self.assertEqual(f.calls,[])

if __name__=='__main__':unittest.main()
