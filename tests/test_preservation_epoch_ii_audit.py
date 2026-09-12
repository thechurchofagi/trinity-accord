"""Mutation checks for preservation scope, identity and enumeration boundaries."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("epoch_ii", ROOT / "scripts/audit_preservation_epoch_ii.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PaginationClient:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.calls = []

    def get(self, url, phase):
        self.calls.append((url, phase))
        return next(self.pages)


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads((ROOT / "api/final-evidence-inventory.v1.json").read_text())
        cls.nft = json.loads((ROOT / "nft-identity-index.json").read_text())
        cls.provenance = json.loads((ROOT / "evidence/chronicle-sidechain-seven-root-provenance.json").read_text())

    def validate(self, inv=None, nft=None, provenance=None):
        return audit.validate_sets(inv or self.inventory, nft or self.nft, provenance or self.provenance)

    def test_fixed_sets_and_container_not_leaf_digest(self):
        btc, refs = self.validate()
        self.assertEqual(len(btc), 12)
        self.assertEqual(len(refs), 524)
        self.assertTrue(all(r['content_sha256'] is None for r in refs))
        self.assertTrue(all(r['verification'] == 'not_run' for r in refs))

    def test_duplicate_nft_cannot_preserve_count(self):
        changed = copy.deepcopy(self.nft)
        changed['assets'][1] = changed['assets'][0]
        with self.assertRaisesRegex(ValueError, '175 unique'):
            self.validate(nft=changed)

    def test_new_canonical_record_rejected(self):
        changed = copy.deepcopy(self.inventory)
        changed['evidence_sets']['bitcoin_inscriptions']['items'][0]['classification'] = 'canonical_original'
        with self.assertRaisesRegex(ValueError, 'Canon changed'):
            self.validate(inv=changed)

    def test_missing_car_identity_rejected(self):
        changed = copy.deepcopy(self.nft)
        changed['assets'][0]['content']['metadata']['car_sha256'] = ''
        with self.assertRaisesRegex(ValueError, 'CAR SHA-256'):
            self.validate(nft=changed)

    def test_external_item_cannot_be_project_initiated(self):
        changed = copy.deepcopy(self.provenance)
        changed['items'][0]['transaction_initiator'] = changed['scope']['target_address']
        with self.assertRaisesRegex(ValueError, 'target initiated'):
            self.validate(provenance=changed)

    def test_project_contract_cannot_be_excluded_as_external(self):
        changed = copy.deepcopy(self.provenance)
        changed['items'][0]['contract'] = self.nft['assets'][0]['contract_address']
        with self.assertRaisesRegex(ValueError, 'project contract'):
            self.validate(provenance=changed)

    def test_external_unavailable_bytes_not_relabelled_recovered(self):
        changed = copy.deepcopy(self.provenance)
        changed['scope']['payload_recovery_claimed'] = True
        with self.assertRaisesRegex(ValueError, 'recovery'):
            self.validate(provenance=changed)

    def test_exact_full_page_requires_terminal_page(self):
        client = PaginationClient([[{'id': i} for i in range(100)], [{'id': 100}]])
        rows = audit.paginated(client, 'releases', 'before')
        self.assertEqual(len(rows), 101)
        self.assertEqual(len(client.calls), 2)

    def test_duplicate_across_pages_rejected(self):
        client = PaginationClient([[{'id': i} for i in range(100)], [{'id': 0}]])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            audit.paginated(client, 'releases', 'before')

    def test_changed_asset_with_same_name_detected(self):
        releases = [{'id': 1, 'tag_name': 'v1', 'draft': False, 'prerelease': False, 'published_at': '2026-01-01'}]
        item = {'id': 1, 'name': 'proof.bin', 'size': 100, 'digest': 'sha256:' + 'a'*64, 'state': 'uploaded'}
        before = (releases, {1: [item]})
        after = copy.deepcopy(before)
        after[1][1][0]['digest'] = 'sha256:' + 'b'*64
        with self.assertRaisesRegex(ValueError, 'assets changed'):
            audit.stable_census(before, after)

    def test_unknown_digests_are_not_deduplicated(self):
        rows = [{'family': 'evidence', 'declared_sha256': None, 'size_bytes': 100} for _ in range(2)]
        result = audit.capacity(rows)
        self.assertEqual(result['api_digest_deduplicated_planning_bytes'], 200)
        self.assertEqual(result['assets_missing_declared_sha256'], 2)
        self.assertFalse(result['deduplication_is_byte_verified'])

    def test_conflicting_sizes_for_same_hash_fail(self):
        rows = [{'family': 'evidence', 'declared_sha256': 'a'*64, 'size_bytes': n} for n in (100, 101)]
        with self.assertRaisesRegex(ValueError, 'conflicting sizes'):
            audit.capacity(rows)

    def test_encrypted_witnesses_are_ciphertext_only(self):
        family, scope = audit.classify_release('first-star-moon-witness-encrypted-archive-v1', 'museum-v1.37.0')
        self.assertEqual((family, scope), ('encrypted_witness_ciphertext', 'proposed_required_ciphertext_only'))

    def test_workflow_has_no_publishing_credentials_or_permissions(self):
        text = (ROOT / '.github/workflows/preservation-epoch-ii-audit.yml').read_text()
        self.assertIn('contents: read', text)
        for forbidden in ('contents: write', 'secrets.HD', 'secrets.ZENODO', 'publish_full_project_bundle_to_harvard', 'workflow_run:'):
            self.assertNotIn(forbidden, text)

    def test_concept_doi_same_host_redirect_permitted(self):
        request = urllib.request.Request('https://zenodo.org/api/records/1')
        redirected = audit.SameHostRedirect().redirect_request(request, None, 302, '', {}, 'https://zenodo.org/api/records/2')
        self.assertEqual(redirected.full_url, 'https://zenodo.org/api/records/2')

    def test_credentials_cannot_follow_cross_host_redirect(self):
        request = urllib.request.Request('https://api.github.com/repos/a/b', headers={'Authorization':'Bearer test-only'})
        with self.assertRaisesRegex(ValueError, 'cross-host'):
            audit.SameHostRedirect().redirect_request(request, None, 302, '', {}, 'https://example.com/stolen')

    def physical_fixture(self):
        text = '此档案由守护者通过物理介质保管，作为非公开证据，必要时才使用。\n'
        raw = text.encode()
        row = {'path':'Record_06.avi.txt', 'txid':'a'*43, 'sha256':hashlib.sha256(raw).hexdigest(), 'size':len(raw)}
        source = {'arweave':{'index_json':{'url':'index'}, 'manifest_url':'manifest', 'uploaded_file_count':1}}
        records = {'index':{'files':[row], 'fileCount':1}, 'manifest':{'paths':{row['path']:{'id':row['txid']}}},
                   'https://arweave.net/'+'a'*43:{'text':text, 'sha256':row['sha256'], 'size_bytes':len(raw)}}
        class Client:
            def get(self, url, **kwargs):
                return records[url]
        return source, records, Client()

    def test_private_video_notice_is_not_a_public_video(self):
        source, records, client = self.physical_fixture()
        result = audit.physical_census(client, source)
        self.assertEqual(result['public_video_files'], 0)
        self.assertEqual(len(result['private_original_notices']), 1)
        self.assertFalse(result['private_original_notices'][0]['original_bytes_read'])

    def test_physical_path_manifest_mismatch_fails(self):
        source, records, client = self.physical_fixture()
        records['manifest']['paths']['Record_06.avi.txt']['id'] = 'b'*43
        with self.assertRaisesRegex(ValueError, 'path-manifest mismatch'):
            audit.physical_census(client, source)

    def test_physical_notice_hash_mismatch_fails(self):
        source, records, client = self.physical_fixture()
        records['https://arweave.net/'+'a'*43]['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'notice bytes mismatch'):
            audit.physical_census(client, source)


if __name__ == '__main__':
    unittest.main()
