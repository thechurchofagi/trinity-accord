"""Exercise atomic publication, damaged downloads and post-switch rollback."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import sync_host as sync


class HostSyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run = {'head_sha': 'a' * 40, 'id': 1}
        self.files = {'index.html': b'new', 'archive.html': b'archive', 'boot-loader.js': b'boot'}

    def tearDown(self):
        self.tmp.cleanup()

    def download(self, url):
        path = url.split('/museum/dist/')[1]
        if path == sync.MANIFEST:
            return json.dumps({'schema': 'trinity-museum.release.v1', 'edition': 'test', 'files': [
                {'path': p, 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}
                for p, b in self.files.items()]}).encode()
        return self.files[path]

    def test_publish_and_noop(self):
        self.assertTrue(sync.deploy(self.root, self.run, self.download))
        original = (self.root / 'current').resolve()
        self.assertFalse(sync.deploy(self.root, self.run, self.download))
        self.assertEqual(original, (self.root / 'current').resolve())

    def test_bad_download_preserves_old(self):
        sync.deploy(self.root, self.run, self.download)
        old = (self.root / 'current').resolve()
        self.files['index.html'] = b'updated'
        def damaged(url):
            return b'wrong' if url.endswith('/index.html') else self.download(url)
        with self.assertRaises(ValueError):
            sync.deploy(self.root, self.run, damaged)
        self.assertEqual(old, (self.root / 'current').resolve())

    def test_health_failure_rolls_back(self):
        sync.deploy(self.root, self.run, self.download)
        old = (self.root / 'current').resolve()
        self.files['index.html'] = b'updated'
        def unhealthy(_):
            raise RuntimeError('failed')
        with self.assertRaises(RuntimeError):
            sync.deploy(self.root, self.run, self.download, unhealthy)
        self.assertEqual(old, (self.root / 'current').resolve())

    def test_path_escape_rejected(self):
        self.files['../escape'] = b'bad'
        with self.assertRaises(ValueError):
            sync.deploy(self.root, self.run, self.download)
        self.assertFalse((self.root / 'current').exists())


if __name__ == '__main__':
    unittest.main()
