#!/usr/bin/env python3
"""Timestamp fixed published PDFs; archive only after remote-header verification.

Reuses the repository's pinned OTS client, dual-provider Bitcoin RPC proxy,
Arweave uploader, runtime spend guard, and wallet ledger. No publication edits.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.cache/research-paper-ots'
DEFAULT_BATCH = ROOT / 'research/paper-timestamps/2026-09-18'
BATCH = DEFAULT_BATCH  # Compatibility alias for focused unit-test fixtures.


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + '\n')


def run(cmd, timeout=180):
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, 'Command timed out; preserve prior receipts and retry later.\n'


def proof_details(path, expected_sha):
    from opentimestamps.core.serialize import BytesDeserializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    from opentimestamps.core.op import OpSHA256
    proof = DetachedTimestampFile.deserialize(BytesDeserializationContext(path.read_bytes()))
    if not isinstance(proof.file_hash_op, OpSHA256) or proof.timestamp.msg.hex() != expected_sha:
        raise ValueError(f'OTS target digest mismatch: {path}')
    attestations = list(proof.timestamp.all_attestations())
    heights = sorted({a.height for _, a in attestations if isinstance(a, BitcoinBlockHeaderAttestation)})
    pending = sum(isinstance(a, PendingAttestation) for _, a in attestations)
    if not heights and not pending:
        raise ValueError(f'OTS proof has no Bitcoin or calendar attestation: {path}')
    return heights, pending


def pdf_bytes(paper, item):
    path = CACHE / paper['report'] / item['name']
    if not path.exists():
        url = f"https://zenodo.org/records/{paper['record_id']}/files/{urllib.parse.quote(item['name'])}?download=1"
        with urllib.request.urlopen(url, timeout=90) as response:
            data = response.read(16 * 1024 * 1024 + 1)
        if len(data) > 16 * 1024 * 1024 or digest(data) != item['sha256'] or not data.startswith(b'%PDF-'):
            raise ValueError(f'Published PDF hash/content mismatch: {paper["report"]}/{item["name"]}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if digest(path.read_bytes()) != item['sha256']:
        raise ValueError(f'Cached PDF hash mismatch: {path}')
    return path


def validate_config(batch, config):
    papers = config.get('papers')
    if not isinstance(papers, list) or not papers or config.get('paper_count') != len(papers):
        raise ValueError('Target paper count is invalid')
    reports = [paper.get('report') for paper in papers]
    if len(set(reports)) != len(reports):
        raise ValueError('Target reports must be unique')
    pdf_count = 0
    for paper in papers:
        receipt_path = ROOT / paper['receipt_path']
        receipt = read(receipt_path)
        strict_receipt = all('bytes' in item for item in paper.get('pdfs', []))
        public = {item['name']: item for item in receipt.get('files', [])}
        if strict_receipt:
            expected_identity = (paper['report'], paper['record_id'], paper['doi'], str(paper['version']), paper['title'])
            actual_identity = (receipt.get('report_number'), receipt.get('record_id'), receipt.get('doi'),
                               str(receipt.get('version')), receipt.get('title'))
            state = receipt.get('state')
            public_bytes_verified = (
                state == 'PUBLISHED_AND_PUBLIC_READBACK_PASS'
                or (
                    state == 'PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING'
                    and receipt.get('submitted') is True
                    and receipt.get('public_file_readback_pass') is True
                )
            )
            if not public_bytes_verified or actual_identity != expected_identity:
                raise ValueError(f'Published receipt identity mismatch: {paper["report"]}')
        for item in paper.get('pdfs', []):
            remote = public.get(item['name'])
            if (not item['name'].endswith('.pdf') or (strict_receipt and
                    (remote is None or remote.get('sha256') != item['sha256']
                     or remote.get('bytes') != item['bytes']))):
                raise ValueError(f'PDF target differs from public readback receipt: {paper["report"]}/{item["name"]}')
            pdf_count += 1
    if pdf_count <= 0:
        raise ValueError('Target batch has no PDFs')
    return papers, pdf_count


def lifecycle(batch=None, stamp_only=False):
    batch = Path(batch or BATCH)
    config = read(batch / 'targets.json')
    papers, expected_pdf_count = validate_config(batch, config)
    status_path = batch / 'status.json'
    if status_path.exists() and read(status_path).get('state') == 'ARWEAVE_READBACK_PASS':
        print(f'Batch {batch.name} already archived; no new stamps or paid uploads.')
        return
    # A paid transaction already binds the frozen verified bundle. Resume its
    # readback without changing proofs or constructing a second paid payload.
    receipt_path = batch / 'arweave-receipt.json'
    if receipt_path.exists() and (read(receipt_path).get('tx_id') or read(receipt_path).get('txid')):
        receipt = read(receipt_path)
        bundle_path = batch / 'arweave-bundle.json'
        bundle = read(bundle_path)
        if (receipt.get('payload_sha256') or receipt.get('data_sha256')) != digest(bundle_path.read_bytes()):
            raise ValueError('Paid transaction does not match frozen OTS bundle')
        frozen = bundle.get('verification', {})
        files = frozen.get('files', [])
        expected = {(p['report'], p['doi'], item['name'], item['sha256']) for p in papers for item in p['pdfs']}
        actual = {(f.get('report'), f.get('doi'), f.get('name'), f.get('sha256')) for f in files}
        if (bundle.get('targets') != config or frozen.get('state') != 'READY_FOR_ARWEAVE'
                or len(files) != expected_pdf_count or actual != expected
                or any(f.get('state') != 'BITCOIN_VERIFIED_REMOTE_HEADERS' for f in files)):
            raise ValueError('Paid bundle lacks exact previously verified PDF targets')
        for item in bundle['files']:
            if digest(base64.b64decode(item['base64'], validate=True)) != item['sha256']:
                raise ValueError('Paid bundle member hash mismatch')
        write(status_path, frozen)
        if os.environ.get('GITHUB_OUTPUT'):
            with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
                stream.write('ready=true\n')
        print('Resume readback of the existing paid transaction; frozen verified proofs retained.')
        return
    ots = shutil.which('ots') or str(Path.home() / '.local/bin/ots')
    results = []
    for paper in papers:
        for item in paper['pdfs']:
            entry = {'report': paper['report'], 'doi': paper['doi'], **item}
            proof = batch / 'proofs' / paper['report'] / (item['name'] + '.ots')
            entry['proof'] = str(proof.relative_to(ROOT))
            try:
                proof.parent.mkdir(parents=True, exist_ok=True)
                if not proof.exists():
                    # The published bytes are required only for the first stamp.
                    # Existing detached proofs are bound directly to the frozen
                    # target SHA-256, so proof upgrade/verification must not be
                    # blocked by temporary Zenodo file-download outages.
                    pdf = pdf_bytes(paper, item)
                    candidate = Path(str(pdf) + '.ots')
                    if not candidate.exists():
                        rc, log = run([ots, 'stamp', '--timeout', '30', str(pdf)], 120)
                        (proof.parent / (item['name'] + '.stamp.txt')).write_text(log)
                    if not candidate.exists():
                        raise RuntimeError('Calendar submission did not produce a receipt')
                    proof_details(candidate, item['sha256'])
                    shutil.copyfile(candidate, proof)
                    shutil.copyfile(candidate, Path(str(proof) + '.submitted'))
                heights, pending = proof_details(proof, item['sha256'])
                if not stamp_only and not heights:
                    rc, log = run([ots, 'upgrade', str(proof)], 180)
                    (proof.parent / (item['name'] + '.upgrade.txt')).write_text(log)
                    heights, pending = proof_details(proof, item['sha256'])
                entry.update(bitcoin_heights=heights, pending_calendar_attestations=pending,
                             proof_sha256=digest(proof.read_bytes()), state='PENDING_BITCOIN')
                if heights:
                    entry['state'] = 'BITCOIN_ATTESTATION_EMBEDDED'
                    node = os.environ.get('OTS_BITCOIN_NODE_URL')
                    if node and not stamp_only:
                        rc, log = run([ots, '--bitcoin-node', node, 'verify', '-d', item['sha256'], str(proof)])
                        (proof.parent / (item['name'] + '.verify.txt')).write_text(log)
                        if rc == 0 and 'success' in log.lower() and 'bitcoin' in log.lower():
                            entry['state'] = 'BITCOIN_VERIFIED_REMOTE_HEADERS'
                        else:
                            entry['verification_error'] = 'Bitcoin verification failed; upload blocked'
            except Exception as exc:
                entry.update(state='ERROR', error=str(exc))
            results.append(entry)
            print(entry['report'], entry['name'], entry['state'], flush=True)
    ready = len(results) == expected_pdf_count and all(r['state'] == 'BITCOIN_VERIFIED_REMOTE_HEADERS' for r in results)
    status = {'schema': 'trinityaccord.paper-ots-status.v1', 'batch': config.get('batch'),
              'paper_count': len(papers),
              'pdf_count': len(results), 'state': 'READY_FOR_ARWEAVE' if ready else 'WAITING',
              'verification_model': 'OTS cryptography plus agreeing Blockstream/mempool headers; not local full-node consensus',
              'files': results}
    write(status_path, status)
    if ready and not (batch / 'arweave-bundle.json').exists():
        files = []
        for paper in papers:
            for item in paper['pdfs']:
                pdf = pdf_bytes(paper, item)
                files.append({'path': f"papers/{paper['report']}/{item['name']}",
                              'sha256': item['sha256'], 'base64': base64.b64encode(pdf.read_bytes()).decode()})
        for p in sorted((batch / 'proofs').rglob('*')):
            if p.is_file() and not p.name.endswith('.bak'):
                data = p.read_bytes()
                files.append({'path': str(p.relative_to(batch)), 'sha256': digest(data),
                              'base64': base64.b64encode(data).decode()})
        write(batch / 'arweave-bundle.json', {
            'schema': 'trinityaccord.research-paper-ots-bundle.v1', 'targets': config,
            'verification': status, 'files': files,
            'boundary': 'Non-amending preservation. Timestamp proves existence by the attested block, not authorship, peer review, truth, or the earlier publication date.'})
    output = os.environ.get('GITHUB_OUTPUT')
    if output:
        with open(output, 'a') as stream:
            stream.write(f'ready={str(ready).lower()}\n')
    if any(r['state'] == 'ERROR' or r.get('verification_error') for r in results):
        raise SystemExit(1)


def upload(batch=None):
    batch = Path(batch or BATCH)
    status = read(batch / 'status.json')
    if status['state'] == 'ARWEAVE_READBACK_PASS':
        return
    if status['state'] != 'READY_FOR_ARWEAVE':
        raise SystemExit('Mature verified OTS proofs required before Arweave upload')
    config = read(batch / 'targets.json')
    papers, expected_pdf_count = validate_config(batch, config)
    if status.get('paper_count') != len(papers) or status.get('pdf_count') != expected_pdf_count:
        raise SystemExit('Status counts differ from target batch')
    bundle_path = batch / 'arweave-bundle.json'
    bundle = read(bundle_path)
    if bundle['targets'] != config or bundle['verification']['files'] != status['files']:
        raise SystemExit('Frozen bundle identity differs from verified targets/proofs')
    for item in bundle['files']:
        if digest(base64.b64decode(item['base64'], validate=True)) != item['sha256']:
            raise SystemExit('Bundle file integrity mismatch')
    receipt = batch / 'arweave-receipt.json'
    env = os.environ.copy()
    env['ARWEAVE_ARCHIVE_TYPE'] = 'research-paper-ots-archive'
    # Existing uploader and its runtime guard own signing, spend limits and readback.
    try:
        p = subprocess.run(['node', 'scripts/arweave_upload_payload.mjs', '--payload',
                            str(bundle_path), '--out', str(receipt)], cwd=ROOT, env=env, timeout=600)
        code = p.returncode
    except subprocess.TimeoutExpired:
        code = 124
    if receipt.exists():
        result = read(receipt)
        if result.get('tx_id'):
            subprocess.run([sys.executable, 'scripts/record_arweave_upload_result.py',
                            '--upload-result-json', str(receipt), '--kind', 'research_paper_ots_archive',
                            '--source-path', str(receipt.relative_to(ROOT)),
                            '--note', f'{len(papers)} published papers; {expected_pdf_count} verified PDF OTS proofs; batch {config.get("batch")}'],
                           cwd=ROOT, check=True)
            subprocess.run([sys.executable, 'scripts/generate_arweave_wallet_status.py'], cwd=ROOT, check=True)
        if (result.get('result') == 'uploaded' and result.get('hash_match') is True
                and result.get('readback_sha256') == digest(bundle_path.read_bytes())
                and result.get('payload_sha256') == digest(bundle_path.read_bytes())):
            status.update(state='ARWEAVE_READBACK_PASS', arweave_tx_id=result['tx_id'],
                          arweave_url='https://arweave.net/' + result['tx_id'],
                          bundle_sha256=digest(bundle_path.read_bytes()))
            write(batch / 'status.json', status)
            return
    raise SystemExit(code or 1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['lifecycle', 'stamp', 'upload'])
    parser.add_argument('--batch', type=Path, default=DEFAULT_BATCH)
    args = parser.parse_args()
    batch = args.batch.resolve()
    if ROOT not in batch.parents or batch.parent != ROOT / 'research/paper-timestamps':
        raise SystemExit('Batch must be a direct directory under research/paper-timestamps')
    if args.action == 'upload':
        upload(batch)
    else:
        lifecycle(batch, stamp_only=args.action == 'stamp')
