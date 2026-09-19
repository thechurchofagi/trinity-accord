#!/usr/bin/env python3
"""Reserve exactly one v1.2 descendant of the published TA09 v1.1 record."""
import json
import os
import re
import sys
import urllib.parse
from publication_common import (DATE, PREVIOUS_RECORD, REPORT, ROOT, TITLE, VERSION,
    check_deposit, client, load, persist_states, read, save, validate_identity, validate_record_id)

PHASE = 'initialization'

def validate_previous(deposit):
    md = deposit.get('metadata', {})
    if (deposit.get('id'), md.get('title'), md.get('version')) != (PREVIOUS_RECORD, TITLE, '1.1'):
        raise RuntimeError('Previous edition identity mismatch')
    if [c.get('name') for c in md.get('creators', [])] != ['Liu, Hongju'] or not deposit.get('submitted'):
        raise RuntimeError('Previous edition is not the published author record')
    concept = str(deposit.get('conceptrecid', ''))
    if not concept.isdigit():
        raise RuntimeError('Previous concept record unavailable')
    return concept

def draft_id(url):
    p = urllib.parse.urlsplit(url)
    m = re.fullmatch(r'/api/deposit/depositions/([0-9]+)', p.path)
    if (p.scheme != 'https' or p.hostname != 'zenodo.org' or p.username or p.password
            or p.port not in (None, 443) or p.query or p.fragment or not m):
        raise RuntimeError('Unexpected latest draft URL')
    return int(m.group(1))

def validate_descendant(deposit, concept):
    rid = validate_record_id(deposit.get('id'))
    md = deposit.get('metadata', {})
    if (str(deposit.get('conceptrecid')), md.get('title')) != (str(concept), TITLE):
        raise RuntimeError('New draft is not a descendant of this paper')
    # Zenodo clears the version field in an unpublished new-version draft.
    if md.get('version') not in (None, '1.1', VERSION) or [c.get('name') for c in md.get('creators', [])] != ['Liu, Hongju']:
        raise RuntimeError('Unrelated version or author in descendant draft: ' + json.dumps({
            'id': rid, 'version': md.get('version'), 'creators': md.get('creators'),
            'submitted': deposit.get('submitted')}, ensure_ascii=False))
    if deposit.get('submitted') and md.get('version') != VERSION:
        raise RuntimeError('Cannot modify a submitted prior version')
    return rid

def reconcile_existing(z, concept):
    """Read the caller's deposits; never repeat an ambiguous creation POST."""
    candidates = []
    query = urllib.parse.urlencode({'q': 'conceptrecid:' + str(concept),
                                   'all_versions': 'true', 'size': 100})
    for page in range(1, 11):
        listing = read(z, '/deposit/depositions?' + query + '&page=' + str(page))
        if not isinstance(listing, list):
            raise RuntimeError('Unexpected deposit reconciliation response')
        for item in listing:
            if str(item.get('conceptrecid')) == str(concept) and item.get('id') != PREVIOUS_RECORD:
                validate_descendant(item, concept)
                candidates.append(item)
        if len(listing) < 100:
            break
    else:
        raise RuntimeError('Incomplete reconciliation pagination')
    if len(candidates) != 1:
        raise RuntimeError('Unresolved creation intent; matching descendants: ' + str(len(candidates)))
    return validate_descendant(candidates[0], concept)

def run():
    global PHASE
    z = client()
    PHASE = 'check_published_predecessor'
    previous = read(z, f'/deposit/depositions/{PREVIOUS_RECORD}')
    concept = validate_previous(previous)
    if (ROOT / 'deposit.json').exists():
        identity = load('deposit.json')
        rid = validate_identity(identity)
        if str(identity.get('conceptrecid')) != concept or identity.get('previous_record_id') != PREVIOUS_RECORD:
            raise RuntimeError('Reservation lineage mismatch')
        deposit = read(z, f'/deposit/depositions/{rid}')
    else:
        link = previous.get('links', {}).get('latest_draft')
        existing = draft_id(link) if link else PREVIOUS_RECORD
        if existing == PREVIOUS_RECORD:
            if (ROOT / 'create-intent.json').exists():
                PHASE = 'read_only_reconciliation'
                existing = reconcile_existing(z, concept)
        if existing == PREVIOUS_RECORD:
            PHASE = 'checkpoint_version_creation_intent'
            save('create-intent.json', {'state':'CREATE_ONE_VERSION_INTENT','previous_record_id':PREVIOUS_RECORD,
                'conceptrecid':concept,'title':TITLE,'report_number':REPORT,'version':VERSION,
                'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
            persist_states({'create-intent.json'})
            PHASE = 'create_one_linked_version'
            response = z.request(f'/deposit/depositions/{PREVIOUS_RECORD}/actions/newversion', 'POST')
            # The legacy documentation describes the predecessor response; current
            # deployments may return the descendant itself. Validate either form.
            if response.get('id') == PREVIOUS_RECORD:
                existing = draft_id(response['links']['latest_draft'])
            else:
                existing = validate_descendant(response, concept)
        validate_record_id(existing)
        deposit = read(z, f'/deposit/depositions/{existing}')
    rid = validate_descendant(deposit, concept)
    PHASE = 'set_new_version_metadata'
    if not deposit.get('submitted'):
        md = {'upload_type':'publication','publication_type':'preprint','title':TITLE,
            'creators':[{'name':'Liu, Hongju','affiliation':'Independent researcher, Shenzhen, China'}],
            'description':'<p>TA-TR-2026-09, revision 1.2 of the published v1.1 preprint. A philosophical study using conceptual analysis and stipulated thought experiments. English full paper and Chinese argument guide, not a full translation. Substantial generative-AI assistance is disclosed. Not peer reviewed. Reservation only; publication and exact public readback remain separate steps.</p>',
            'publication_date':DATE,'version':VERSION,'access_right':'open','license':'cc-by-4.0','language':'eng',
            'keywords':['AI consciousness','scientific understanding','epistemic dependence','expertise','thought experiments']}
        deposit = z.request(f'/deposit/depositions/{rid}', 'PUT', {'metadata':md})
    rid, doi = check_deposit(deposit, {'record_id':rid,'doi':f'10.5281/zenodo.{rid}','conceptrecid':concept})
    receipt = {'record_id':rid,'doi':doi,'conceptrecid':concept,'conceptdoi':f'10.5281/zenodo.{concept}',
        'previous_record_id':PREVIOUS_RECORD,'previous_doi':f'10.5281/zenodo.{PREVIOUS_RECORD}',
        'title':TITLE,'report_number':REPORT,'version':VERSION,'submitted':bool(deposit.get('submitted')),
        'state':'ALREADY_SUBMITTED_REQUIRES_READBACK' if deposit.get('submitted') else 'RESERVED_NOT_PUBLICATION',
        'prior_version_files_modified':False,'workflow_run_id':os.environ.get('GITHUB_RUN_ID')}
    save('deposit.json', receipt)
    save('preparation-attempt.json', {'state':receipt['state'],'record_id':rid,'phase':'completed','workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
    persist_states({'deposit.json','preparation-attempt.json'})
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    try:
        run()
    except Exception as error:
        save('preparation-attempt.json', {'state':'INCOMPLETE_REQUIRES_SAME_VERSION_RECONCILIATION',
            'phase':PHASE,'error_type':type(error).__name__,'error':str(error),'workflow_run_id':os.environ.get('GITHUB_RUN_ID')})
        print(f'{type(error).__name__}: {error}', file=sys.stderr)
        sys.exit(1)
