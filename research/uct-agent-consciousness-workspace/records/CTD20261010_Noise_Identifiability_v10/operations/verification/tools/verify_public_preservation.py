#!/usr/bin/env python3
"""Independently GET a completed CTD Arweave payload and verify its exact bytes.

Run only after the real workflow writes ARWEAVE_READBACK_PASS. This script reads
local receipts and public HTTPS data; it never uploads, signs, pays or retries a
transaction. It writes one new local verification receipt and exits nonzero on
every incomplete or mismatched result. No wallet or credential is needed.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

DOI = '10.5281/zenodo.23279189'
REPORT = 'TA-TR-2026-26'
BATCH = '2026-10-10-paper26-v100'
PDF_NAME = 'noise-identifiability-bodily-judgments-v1.0.0.pdf'
PDF_BYTES = 269961
PDF_SHA = '479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94'
MAX_PAYLOAD_BYTES = 4 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def public_https(url):
    u = urlsplit(url)
    host = u.hostname or ''
    require(u.scheme == 'https' and (host == 'arweave.net' or host.endswith('.arweave.net'))
            and u.username is None and u.password is None and u.port in (None, 443),
            'Redirect is not anonymous HTTPS on the public Arweave gateway')


class PublicRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        public_https(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def validate_local(preservation, public_pdf):
    paths = {
        'status': preservation / 'status.json',
        'uploader_receipt': preservation / 'arweave-receipt.json',
        'bundle': preservation / 'arweave-bundle.json',
        'targets': preservation / 'targets.json',
        'public_pdf': public_pdf,
        'ots_proof': preservation / 'proofs' / REPORT / (PDF_NAME + '.ots'),
    }
    raw = {k: p.read_bytes() for k, p in paths.items()}
    status = json.loads(raw['status'])
    require(status.get('schema') == 'trinityaccord.paper-ots-status.v1'
            and status.get('batch') == BATCH and status.get('paper_count') == status.get('pdf_count') == 1
            and status.get('state') == 'ARWEAVE_READBACK_PASS',
            'Real final workflow readback for this one-paper, one-PDF batch is required')
    receipt = json.loads(raw['uploader_receipt'])
    require(receipt.get('schema') == 'trinityaccord.arweave-upload-result.v1'
            and receipt.get('result') == 'uploaded' and receipt.get('hash_match') is True,
            'Uploader receipt is not a successful actual readback')
    tx = receipt['tx_id']
    require(isinstance(tx, str) and re.fullmatch(r'[A-Za-z0-9_-]{43}', tx), 'Invalid transaction ID')
    require(receipt['txid'] == status['arweave_tx_id'] == tx, 'Transaction identities disagree')
    endpoint = 'https://arweave.net/' + tx
    require(status['arweave_url'] == endpoint, 'Workflow public URL disagrees with transaction ID')
    payload = raw['bundle']
    require(0 < len(payload) <= MAX_PAYLOAD_BYTES, 'Unexpected local payload size')
    digest = sha(payload)
    require(receipt['payload_sha256'] == receipt['data_sha256'] == receipt['readback_sha256']
            == status['bundle_sha256'] == digest, 'Transaction receipt and frozen bundle hashes disagree')
    bundle = json.loads(payload)
    require(bundle.get('schema') == 'trinityaccord.research-paper-ots-bundle.v1', 'Wrong bundle schema')
    config = json.loads(raw['targets'])
    require(config.get('schema') == 'trinityaccord.paper-ots-targets.v1' and config['batch'] == BATCH
            and bundle['targets'] == config and config['paper_count'] == 1 and len(config['papers']) == 1,
            'Frozen targets disagree')
    paper = config['papers'][0]
    require((paper['report'], paper['doi'], paper['record_id'], paper['version'])
            == (REPORT, DOI, 23279189, '1.0.0') and len(paper['pdfs']) == 1,
            'Wrong published paper target')
    item = paper['pdfs'][0]
    require((item['name'], item['bytes'], item['sha256']) == (PDF_NAME, PDF_BYTES, PDF_SHA),
            'Wrong public PDF identity in targets')
    verified = bundle['verification']
    require(verified.get('schema') == 'trinityaccord.paper-ots-status.v1'
            and verified.get('batch') == BATCH and verified.get('paper_count') == verified.get('pdf_count') == 1
            and verified['state'] == 'READY_FOR_ARWEAVE' and len(verified['files']) == 1
            and status['files'] == verified['files'], 'Verification snapshot does not match final status')
    target = verified['files'][0]
    require((target['report'], target['doi'], target['name'], target['bytes'], target['sha256'])
            == (REPORT, DOI, PDF_NAME, PDF_BYTES, PDF_SHA), 'Wrong verified PDF identity')
    require(target['state'] == 'BITCOIN_VERIFIED_REMOTE_HEADERS' and bool(target['bitcoin_heights']),
            'No completed Bitcoin verification in the frozen bundle')
    require(target['proof'] == 'research/paper-timestamps/' + BATCH + '/proofs/' + REPORT + '/' + PDF_NAME + '.ots',
            'Verified proof path does not name the exact CTD preservation batch')
    require(len(raw['public_pdf']) == PDF_BYTES and sha(raw['public_pdf']) == PDF_SHA,
            'Local PDF is not the exact public original')
    require(sha(raw['ots_proof']) == target['proof_sha256'], 'Local OTS proof differs from verified proof')
    return paths, raw, tx, endpoint, target


def verify_members(downloaded, raw):
    members = json.loads(downloaded)['files']
    decoded, evidence = {}, []
    for member in members:
        name = member['path']
        p = PurePosixPath(name)
        require(isinstance(name, str) and '\\' not in name and '\0' not in name
                and not p.is_absolute() and '..' not in p.parts and str(p) == name
                and name not in ('', '.') and name not in decoded, 'Invalid or duplicate AR member path')
        data = base64.b64decode(member['base64'], validate=True)
        require(sha(data) == member['sha256'], 'AR member SHA mismatch: ' + name)
        decoded[name] = data
        evidence.append({'path': name, 'bytes': len(data), 'sha256': sha(data)})
    require(decoded.get('papers/' + REPORT + '/' + PDF_NAME) == raw['public_pdf'],
            'Downloaded AR member is not the exact public PDF')
    require(decoded.get('proofs/' + REPORT + '/' + PDF_NAME + '.ots') == raw['ots_proof'],
            'Downloaded AR member is not the exact verified OTS proof')
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preservation', type=Path, required=True)
    parser.add_argument('--public-pdf', type=Path, required=True, help='Exact original 269961-byte Zenodo PDF')
    parser.add_argument('--out', type=Path, required=True, help='New local JSON receipt; never overwritten')
    parser.add_argument('--timeout', type=int, default=30)
    args = parser.parse_args()
    require(1 <= args.timeout <= 60, 'Timeout must be between 1 and 60 seconds')
    require(not args.out.exists(), 'Use a new receipt path; preserve earlier evidence')
    result = {
        'schema': 'ctd-independent-public-preservation-readback/1',
        'state': 'PUBLIC_ARWEAVE_READBACK_NOT_VERIFIED', 'doi': DOI,
        'started_utc': utc(), 'authenticated': False, 'http_method': 'GET',
        'network_request_attempted': False, 'hash_match': False,
        'tx_id': None, 'downloaded_endpoint': None, 'http_status': None,
        'bytes': None, 'readback_sha256': None,
        'wallet_payment_upload_or_workflow_actions': False,
    }
    try:
        paths, raw, tx, endpoint, target = validate_local(args.preservation, args.public_pdf)
        result.update(tx_id=tx, requested_endpoint=endpoint, payload_sha256=sha(raw['bundle']),
                      expected_bytes=len(raw['bundle']))
        public_https(endpoint)
        # urllib's default opener has no HTTP auth, cookie or .netrc handler.
        # Only anonymous GET is made, with HTTPS redirects restricted above.
        opener = build_opener(PublicRedirects())
        request = Request(endpoint, method='GET', headers={
            'User-Agent': 'CTD-independent-public-readback/1',
            'Accept': 'application/json', 'Accept-Encoding': 'identity', 'Cache-Control': 'no-cache'})
        result['network_request_attempted'] = True
        with opener.open(request, timeout=args.timeout) as response:
            final_url = response.geturl()
            public_https(final_url)
            result.update(downloaded_endpoint=final_url, http_status=response.status,
                          content_type=response.headers.get('Content-Type'))
            require(response.status == 200, 'Gateway response is not HTTP 200; not verified')
            downloaded = response.read(len(raw['bundle']) + 1)
        result.update(bytes=len(downloaded), readback_sha256=sha(downloaded))
        require(len(downloaded) == len(raw['bundle']) and sha(downloaded) == sha(raw['bundle'])
                and downloaded == raw['bundle'], 'Public payload bytes do not equal the frozen bundle')
        members = verify_members(downloaded, raw)
        require(all(p.read_bytes() == raw[k] for k, p in paths.items()),
                'Local source evidence changed during public readback')
        result.update(
            state='PUBLIC_ARWEAVE_READBACK_PASS', hash_match=True,
            pdf_sha256=PDF_SHA, pdf_bytes=PDF_BYTES, proof_sha256=sha(raw['ots_proof']),
            bitcoin_heights=target['bitcoin_heights'], members=members,
            member_count=len(members), source_files={
                k: {'path': str(p.resolve()), 'bytes': len(raw[k]), 'sha256': sha(raw[k])}
                for k, p in paths.items()},
            verification_scope='Independent anonymous payload-byte readback and embedded-member identity; '
                               'Bitcoin verification is inherited from the exact frozen remote-header receipt, '
                               'not rerun here. The nine Zenodo public assets have separate publication-readback evidence; '
                               'this does not claim all nine are archived by this one-PDF OTS batch. The delivery ZIP '
                               'and distribution-metadata PDF variants are not this payload.')
    except HTTPError as exc:
        result.update(http_status=exc.code, downloaded_endpoint=exc.geturl(),
                      error_type='HTTPError', error='Gateway HTTP response is not verified: ' + str(exc.code))
    except Exception as exc:
        result.update(error_type=type(exc).__name__, error=str(exc))
    result['checked_utc'] = utc()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['hash_match'] is True else 1


if __name__ == '__main__':
    sys.exit(main())
