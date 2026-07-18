#!/usr/bin/env python3
"""Permanent source-only checks for round-five workflow/publication resilience."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def read(path:str)->str: return (ROOT/path).read_text(encoding='utf-8')

def main()->int:
    errors=[]
    deploy=read('.github/workflows/deploy-pages.yml')
    for marker in [
        'source_sha: ${{ steps.source.outputs.source_sha }}',
        'ref: ${{ needs.verify.outputs.source_sha }}',
        'ref: ${{ needs.build.outputs.source_sha }}',
        'pages-source-receipt-${{ github.run_id }}',
        'trinity-pages-source-receipt.v1',
        'python3 scripts/verify_retired_builder_bundle_archive.py --site-dir _site',
    ]:
        if marker not in deploy: errors.append(f'deploy missing {marker}')
    if deploy.count('ref: ${{ github.event.inputs.checkout_ref || github.sha }}') != 1:
        errors.append('requested ref must be consumed only by verify checkout')
    for forbidden in ['export_formal_builder_bundles.py --out-dir builder-bundles --update-api','cp scripts/download_and_run_builder_bundle.py builder-bundles/download_and_run_builder_bundle.py']:
        if forbidden in deploy: errors.append(f'deploy regenerates retired bundle: {forbidden}')

    helper=read('scripts/download_and_run_builder_bundle.py')
    if helper.encode()!= (ROOT/'builder-bundles/download_and_run_builder_bundle.py').read_bytes(): errors.append('public historical helper differs from source copy')
    for marker in ['--allow-historical-retired-bundle','REFUSED: all formal Gateway v1 builder bundles are retired.','HISTORICAL OUTPUT ONLY — DO NOT SUBMIT']:
        if marker not in helper: errors.append(f'historical helper missing {marker}')
    result=subprocess.run([sys.executable,'builder-bundles/download_and_run_builder_bundle.py','--route','pure_echo'],cwd=ROOT,capture_output=True,text=True)
    if result.returncode != 2: errors.append('historical helper does not fail closed without opt-in')

    page=read('external-agent-copy-paste-examples.md')
    for marker in ['sitemap: false','robots: noindex,nofollow','Do Not Use','/api/agent-first-contact.json']:
        if marker not in page: errors.append(f'historical page missing {marker}')
    if 'trinity-agent-issue-gateway.onrender.com/gateway/preflight' in page: errors.append('historical page exposes actionable retired preflight')
    if 'https://www.trinityaccord.org/external-agent-copy-paste-examples/' in read('sitemap.xml'): errors.append('historical page remains in sitemap')

    health=json.loads(read('api/agent-live-health.v1.json'))
    expected=['scripts/smoke_live_discovery_contract_v2.py','scripts/smoke_external_agent_entrypoint_journeys.py','scripts/smoke_external_agent_journey_swarm.py']
    if health.get('live_smoke_scripts') != expected: errors.append('active live smoke list drifted')
    if health.get('inputs',{}).get('guardian_state') != '/api/guardian-state.json': errors.append('health guardian state is not current')

    home=read('.github/workflows/homepage-status-sync.yml')
    for marker in ['Build Record Chain Batch','Stamp Record Chain Batches with OpenTimestamps','Waiting Heartbeat Arweave Capsule','Rebuild Agent-Declared Verification Index','check_deployment_freshness_v2.py','Equivalent generated state already reached main',"github.event_name == 'workflow_run'",'upstream_workflow_completed']:
        if marker not in home: errors.append(f'homepage sync missing {marker}')

    receipt=read('.github/workflows/homepage-deployment-receipt.yml')
    for marker in ['actions: read','pages-source-receipt-${RUN_ID}','Deployed source SHA','Workflow event head SHA','provenance_missing']:
        if marker not in receipt: errors.append(f'deployment receipt missing {marker}')
    if 'Expected homepage marker' in receipt: errors.append('deployment receipt still hardcodes mutable marker')

    archive=subprocess.run([sys.executable,'scripts/verify_retired_builder_bundle_archive.py'],cwd=ROOT,capture_output=True,text=True)
    if archive.returncode: errors.append(archive.stdout+archive.stderr)
    if errors:
        print('FAIL: round-five systemic resilience errors:')
        for e in errors: print('  -',e)
        return 1
    print('PASS: round-five workflow, publication, and retired-route resilience contracts')
    return 0
if __name__=='__main__': raise SystemExit(main())
