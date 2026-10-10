#!/usr/bin/env python3
"""Query previously submitted OTS calendars on isolated local copies only.

No stamp, workflow dispatch, repository mutation, wallet access, or payment.
An embedded Bitcoin attestation is reported for the official workflow to verify;
it is never reported here as a completed Bitcoin verification.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import subprocess
import time

from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
from opentimestamps.core.op import OpSHA256
from opentimestamps.core.serialize import BytesDeserializationContext
from opentimestamps.core.timestamp import DetachedTimestampFile

ROOT = Path('/workspace/scratch/5b73aae6b1e4/ctd_publication_operations')
SOURCE = ROOT / 'preservation_attempt_1/proofs/TA-TR-2026-26/noise-identifiability-bodily-judgments-v1.0.0.pdf.ots'
CLIENT = ROOT / 'ots_local/venv/bin/ots'
SOURCE_SHA = 'a407ef8f904c9bb67d49d3017d8acecebfe8a7e2c082a31dfe3a35f57cc762c7'
PDF_SHA = '479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94'


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(path):
    data = path.read_bytes()
    proof = DetachedTimestampFile.deserialize(BytesDeserializationContext(data))
    if not isinstance(proof.file_hash_op, OpSHA256) or proof.timestamp.msg.hex() != PDF_SHA:
        raise RuntimeError('Detached proof no longer binds the exact published PDF digest')
    att = list(proof.timestamp.all_attestations())
    return {
        'bytes': len(data), 'proof_sha256': sha(data), 'pdf_sha256': proof.timestamp.msg.hex(),
        'bitcoin_heights': sorted({a.height for _, a in att if isinstance(a, BitcoinBlockHeaderAttestation)}),
        'pending_calendar_attestations': sum(isinstance(a, PendingAttestation) for _, a in att),
    }


def require_original():
    data = SOURCE.read_bytes()
    if len(data) != 770 or sha(data) != SOURCE_SHA:
        raise RuntimeError('Original proof has changed; stopping without overwriting it')


def text_output(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')


def main():
    require_original()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    destination = ROOT / 'ots_local' / ('agent_watch_20m_' + stamp)
    destination.mkdir(exist_ok=False)
    started = time.monotonic()
    deadline = started + 1200.0
    receipt = {
        'schema': 'ctd.pending-ots-calendar-watch.v1',
        'started_at_utc': now(), 'source_path': str(SOURCE), 'source_sha256': SOURCE_SHA,
        'pdf_sha256': PDF_SHA, 'client_path': str(CLIENT),
        'client_version': importlib.metadata.version('opentimestamps-client'),
        'cadence_seconds': 120, 'maximum_watch_seconds': 1200,
        'maximum_attempts': 10, 'per_query_timeout_seconds': 45,
        'state': 'WATCHING_PREVIOUSLY_SUBMITTED_CALENDARS', 'attempts': [],
        'boundary': 'Local upgrade only. Bitcoin attestation presence is not official Bitcoin verification or paid archival completion.',
        'new_stamp': False, 'workflow_dispatch': False, 'wallet_access': False, 'payment': False,
    }
    receipt_path = destination / 'WATCH_RECEIPT.json'

    def save():
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')

    save()
    print(json.dumps({'event': 'START', 'receipt_path': str(receipt_path), 'utc': now()}), flush=True)
    for index in range(10):
        next_start = started + index * 120.0
        delay = min(next_start - time.monotonic(), deadline - time.monotonic())
        while delay > 0:
            time.sleep(min(delay, 50.0))
            delay = min(next_start - time.monotonic(), deadline - time.monotonic())
        if time.monotonic() >= deadline:
            break
        require_original()
        trial = destination / f'attempt_{index + 1:02d}'
        trial.mkdir()
        copy = trial / SOURCE.name
        shutil.copyfile(SOURCE, copy)
        before = inspect(copy)
        row = {'attempt': index + 1, 'started_at_utc': now(), 'copy_path': str(copy), 'before': before}
        limit = min(45.0, max(0.1, deadline - time.monotonic()))
        try:
            run = subprocess.run([str(CLIENT), 'upgrade', str(copy)], cwd=trial,
                                 capture_output=True, text=True, timeout=limit)
            row['exit_code'] = run.returncode
            log = run.stdout + run.stderr
        except subprocess.TimeoutExpired as exc:
            row['exit_code'] = 124
            row['error'] = 'Calendar query timed out; no stamp or retry was issued within this attempt.'
            log = text_output(exc.stdout) + text_output(exc.stderr)
        (trial / 'upgrade.log').write_text(log)
        row['completed_at_utc'] = now()
        row['after'] = inspect(copy)
        require_original()
        row['original_proof_unchanged'] = True
        receipt['attempts'].append(row)
        if row['after']['bitcoin_heights']:
            receipt['state'] = 'BITCOIN_ATTESTATION_OBSERVED_NOT_YET_OFFICIALLY_VERIFIED'
        save()
        print(json.dumps({'event': 'ATTEMPT', 'receipt_path': str(receipt_path), **row}), flush=True)
        if row['after']['bitcoin_heights']:
            break
    if receipt['state'] == 'WATCHING_PREVIOUSLY_SUBMITTED_CALENDARS':
        receipt['state'] = 'WATCH_LIMIT_REACHED_NO_BITCOIN_ATTESTATION'
    receipt['completed_at_utc'] = now()
    receipt['elapsed_seconds'] = time.monotonic() - started
    receipt['original_proof_unchanged'] = True
    require_original()
    save()
    print(json.dumps({'event': 'STOP', 'state': receipt['state'], 'receipt_path': str(receipt_path),
                      'attempt_count': len(receipt['attempts']), 'utc': now()}), flush=True)


if __name__ == '__main__':
    main()
