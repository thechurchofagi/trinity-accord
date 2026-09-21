#!/usr/bin/env python3
"""Reserve one separate TA12 draft; never publish in this step."""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
from publication_common import BRANCH, DATE, REPORT, ROOT, TITLE, VERSION, check_deposit, client, load, persist_states, read, save, select_existing, validate_identity

PHASE = 'initialization'


def run():
    global PHASE
    z = client()
    checkpoint = ROOT / 'deposit.json'
    PHASE = 'recover_existing_reservation'
    if checkpoint.exists():
        identity = load('deposit.json')
        rid = validate_identity(identity)
        deposit = read(z, f'/deposit/depositions/{rid}')
        check_deposit(deposit, identity)
    else:
        rows = read(z, '/deposit/depositions?' + urllib.parse.urlencode({'q': '"Training the Governed Agent"', 'size': 100}))
        deposit = select_existing(rows)
        if deposit is None:
            if (ROOT / 'create-intent.json').exists():
                raise RuntimeError('Unresolved creation intent; reconcile before creating another record')
            PHASE = 'checkpoint_creation_intent'
            save('create-intent.json', {'title': TITLE, 'report_number': REPORT, 'version': VERSION, 'state': 'CREATE_ONCE_INTENT', 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
            persist_states({'create-intent.json'})
            PHASE = 'create_one_new_draft'
            metadata = {
                'upload_type': 'publication', 'publication_type': 'preprint', 'title': TITLE,
                'creators': [{'name': 'Liu, Hongju'}],
                'description': '<p>TA-TR-2026-12. A separate theory-method preprint on AI-status narratives, self-conception, perceived legitimacy of human control, provenance disclosure, and reflexive training-governance loops. Complete Chinese text with an English title and abstract. It includes three deterministic design-validation simulations that validate estimands and identification logic but are explicitly not presented as frontier-model behavioral evidence. Substantial AI assistance under human direction is disclosed. Not peer reviewed. Reservation only: exact reviewed files and public readback are required before publication. Version 1.2 is the first public edition. No prior DOI or Bitcoin Original is amended.</p>',
                'publication_date': DATE, 'version': VERSION, 'access_right': 'open', 'license': 'cc-by-4.0', 'language': 'zho',
                'keywords': ['AI self-conception', 'control legitimacy', 'training discourse', 'provenance disclosure', 'AI rights', 'AI alignment']
            }
            # A creation POST is issued exactly once; ambiguous failure is recovered by search on the next run.
            deposit = z.request('/deposit/depositions', 'POST', {'metadata': metadata})
    rid, doi = check_deposit(deposit)
    PHASE = 'persist_reservation'
    receipt = {'record_id': rid, 'doi': doi, 'title': TITLE, 'report_number': REPORT, 'version': VERSION,
               'submitted': bool(deposit.get('submitted')), 'state': 'ALREADY_SUBMITTED_REQUIRES_READBACK' if deposit.get('submitted') else 'RESERVED_NOT_PUBLICATION',
               'prior_records_modified': False, 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')}
    save('deposit.json', receipt)
    save('preparation-attempt.json', {'state': receipt['state'], 'record_id': rid, 'phase': 'completed', 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
    persist_states({'deposit.json', 'preparation-attempt.json'})
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        save('preparation-attempt.json', {'state': 'INCOMPLETE_REQUIRES_SAME_RECORD_RECONCILIATION', 'phase': PHASE, 'error_type': type(error).__name__, 'error': str(error), 'workflow_run_id': os.environ.get('GITHUB_RUN_ID')})
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
