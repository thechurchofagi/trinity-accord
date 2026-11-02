import base64
import copy
import hashlib
import unittest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from unlock import check, decrypt, candidate


class DecoderTests(unittest.TestCase):
    def setUp(self):
        self.password = candidate(7)
        salt = bytes(range(16))
        dk = hashlib.pbkdf2_hmac('sha256',self.password,salt,5,64)
        raw = '测试 plaintext\n'.encode()
        enc = lambda b: base64.b64encode(b).decode()
        self.cap = {'format':'yuhui-compute-capsule-v1','puzzle':{'iterations':5,
            'salt_base64':enc(salt),'verifier_base64':enc(dk[:32])},
            'plaintext':{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},
            'encryption':{'nonce_base64':enc(bytes(12)),'aad_base64':enc(b'test'),
            'ciphertext_base64':enc(AESGCM(dk[32:]).encrypt(bytes(12),raw,b'test'))}}
        self.raw = raw
    def test_search_and_recover_without_private_key(self):
        found = [candidate(i) for i in range(16) if check(self.cap,candidate(i))]
        self.assertEqual(found,[self.password])
        self.assertEqual(decrypt(self.cap,found[0]),self.raw)
    def test_wrong_candidate_rejected(self):
        with self.assertRaises(ValueError): decrypt(self.cap,candidate(8))
    def test_modified_ciphertext_rejected(self):
        cap=copy.deepcopy(self.cap)
        c=bytearray(base64.b64decode(cap['encryption']['ciphertext_base64']));c[0]^=1
        cap['encryption']['ciphertext_base64']=base64.b64encode(c).decode()
        with self.assertRaises(InvalidTag): decrypt(cap,self.password)
    def test_public_verifier_is_not_encryption_key(self):
        e=self.cap['encryption'];p=self.cap['puzzle']
        with self.assertRaises(InvalidTag):
            AESGCM(base64.b64decode(p['verifier_base64'])).decrypt(base64.b64decode(e['nonce_base64']),base64.b64decode(e['ciphertext_base64']),base64.b64decode(e['aad_base64']))
    def test_plaintext_commitment_checked(self):
        cap=copy.deepcopy(self.cap);cap['plaintext']['sha256']='00'*32
        with self.assertRaises(ValueError):decrypt(cap,self.password)

if __name__=='__main__':unittest.main()
