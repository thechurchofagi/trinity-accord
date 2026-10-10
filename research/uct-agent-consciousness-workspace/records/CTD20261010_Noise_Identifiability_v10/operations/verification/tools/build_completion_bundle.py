#!/usr/bin/env python3
"""Build a verification bundle from completed real receipts; no remote writes."""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', required=True, type=Path)
    parser.add_argument('--preservation', required=True, type=Path)
    parser.add_argument('--chain-receipt', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output must be a new bundle')
    chain = read(args.chain_receipt)
    require(chain['state'] == 'DOI_OTS_ARWEAVE_PUBLIC_READBACK_COMPLETE', 'Actual completed chain required')
    require(chain['doi'] == '10.5281/zenodo.23279189', 'Unexpected DOI')
    require(chain['root_arweave_readback']['hash_match'] is True, 'Independent root AR readback required')
    public_assets = chain['public_assets']
    public_names = {p.name for p in (args.stage / 'public').iterdir() if p.is_file()}
    expected_public_names = {
        'README-LICENSE.txt', 'REVIEW-AND-SOURCES.md', 'SHA256SUMS.txt',
        'citation.bib', 'citation.csl.json', 'citation.ris',
        'noise-identifiability-bodily-judgments-v1.0.0.md',
        'noise-identifiability-bodily-judgments-v1.0.0.pdf',
        'reproducibility-v1.0.0.zip',
    }
    require(len(public_assets) == 9 and public_names == {a['name'] for a in public_assets} == expected_public_names, 'Expected exact nine distinct public assets')
    for item in public_assets:
        data = (args.stage / 'public' / item['name']).read_bytes()
        require(len(data) == item['bytes'] and sha(data) == item['sha256'], 'Public asset mismatch: ' + item['name'])
    status = read(args.preservation / 'status.json')
    require(status['state'] == 'ARWEAVE_READBACK_PASS', 'Final workflow readback required')
    receipt = read(args.preservation / 'arweave-receipt.json')
    bundle_bytes = (args.preservation / 'arweave-bundle.json').read_bytes()
    bundle = json.loads(bundle_bytes)
    bundle_sha = sha(bundle_bytes)
    require(receipt['result'] == 'uploaded' and receipt['hash_match'] is True, 'Successful uploader receipt required')
    require(receipt['payload_sha256'] == receipt['readback_sha256'] == bundle_sha == status['bundle_sha256'], 'AR payload mismatch')
    require(status['arweave_tx_id'] == receipt['tx_id'] == chain['root_arweave_readback']['tx_id'], 'AR transaction mismatch')
    require(chain['root_arweave_readback']['readback_sha256'] == bundle_sha, 'Root readback does not match archived payload')
    require(bundle['targets'] == read(args.preservation / 'targets.json'), 'Frozen target mismatch')
    verified = bundle['verification']
    require(verified['state'] == 'READY_FOR_ARWEAVE' and len(verified['files']) == 1, 'Expected one verified PDF')
    target = verified['files'][0]
    require(target['state'] == 'BITCOIN_VERIFIED_REMOTE_HEADERS' and bool(target['bitcoin_heights']), 'Bitcoin verification missing')
    pdf_name = 'noise-identifiability-bodily-judgments-v1.0.0.pdf'
    expected_pdf = '479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94'
    require((target['report'], target['doi'], target['name']) == ('TA-TR-2026-26', chain['doi'], pdf_name), 'Verified target identity mismatch')
    require(target['sha256'] == expected_pdf, 'Wrong timestamp target')
    public_pdf = (args.stage / 'public' / pdf_name).read_bytes()
    public_proof = (args.preservation / 'proofs/TA-TR-2026-26' / (pdf_name + '.ots')).read_bytes()
    require(len(public_pdf) == target['bytes'] == 269961 and sha(public_pdf) == expected_pdf, 'Use exact public PDF bytes')
    require(sha(public_proof) == target['proof_sha256'], 'Frozen OTS proof mismatch')
    decoded_members = {}
    for member in bundle['files']:
        require(member['path'] not in decoded_members, 'Duplicate AR bundle member path')
        data = base64.b64decode(member['base64'], validate=True)
        require(sha(data) == member['sha256'], 'Corrupt AR bundle member')
        decoded_members[member['path']] = data
    require(decoded_members.get('papers/TA-TR-2026-26/' + pdf_name) == public_pdf, 'Archived PDF differs from public PDF')
    require(decoded_members.get('proofs/TA-TR-2026-26/' + pdf_name + '.ots') == public_proof, 'Archived OTS differs from verified proof')
    report = args.report.read_text(encoding='utf-8')
    require('【待最终填写' not in report, 'Report still has pending placeholders')
    entries = {}
    for path in sorted(args.stage.rglob('*')):
        if path.is_file():
            require(not path.is_symlink(), 'Symbolic links are not accepted')
            entries[path.relative_to(args.stage).as_posix()] = path.read_bytes()
    for path in sorted(args.preservation.rglob('*')):
        if path.is_file():
            require(not path.is_symlink(), 'Symbolic links are not accepted')
            name = 'preservation/' + path.relative_to(args.preservation).as_posix()
            require(name not in entries, 'Duplicate bundle path')
            entries[name] = path.read_bytes()
    require(not {'FINAL_CHAIN_RECEIPT.json', 'PUBLICATION_COMPLETION_ZH.md', 'DELIVERY_MANIFEST.json'} & entries.keys(), 'Reserved root paths exist')
    entries['FINAL_CHAIN_RECEIPT.json'] = args.chain_receipt.read_bytes()
    entries['PUBLICATION_COMPLETION_ZH.md'] = args.report.read_bytes()
    manifest = {
        'schema': 'ctd-publication-preservation-delivery-manifest/1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'doi': chain['doi'],
        'scope': 'Exact nine public publication assets, completed preservation evidence, and explanatory operational records; the ZIP itself is not the Arweave payload.',
        'files': [{'path': n, 'bytes': len(d), 'sha256': sha(d)} for n, d in sorted(entries.items())],
    }
    entries['DELIVERY_MANIFEST.json'] = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.out, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(entries.items()):
            archive.writestr(name, data)
    with zipfile.ZipFile(args.out) as archive:
        require(archive.testzip() is None, 'ZIP CRC check failed')
        require(len(archive.namelist()) == len(entries), 'ZIP member count mismatch')
        for name, expected in entries.items():
            require(archive.read(name) == expected, 'Packed bytes differ: ' + name)
    result = {'state': 'COMPLETED_CHAIN_DELIVERY_BUNDLE_BYTE_CHECK_PASS', 'path': str(args.out.resolve()), 'bytes': args.out.stat().st_size, 'sha256': sha(args.out.read_bytes()), 'members': len(entries), 'public_pdf_sha256': expected_pdf, 'arweave_payload_sha256': bundle_sha}
    args.out.with_suffix('.receipt.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
