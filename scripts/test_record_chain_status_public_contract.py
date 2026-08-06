#!/usr/bin/env python3
"""Fail closed on stale or contradictory public Record-Chain status contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

def load(rel: str) -> dict[str, Any]:
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

failures: list[str] = []
status = load('api/record-chain-status.json')
tip = load('record-chain/chain-tip.json')
gateway = load('api/record-chain-intake-gateway.v1.json')
home = load('api/public-home-status.json')

rc = status.get('record_chain', {})
expected_head = {
    'latest_record_id': tip.get('latest_record_id'),
    'latest_record_index': tip.get('latest_record_index'),
    'latest_record_sha256': tip.get('latest_record_sha256'),
    'native_record_count': tip.get('native_record_count'),
}
for key, expected in expected_head.items():
    if rc.get(key) != expected:
        failures.append(f'record-chain-status record_chain.{key}={rc.get(key)!r}, expected {expected!r}')
if status.get('total_records') != tip.get('native_record_count'):
    failures.append('record-chain-status total_records does not match chain-tip')
pipeline_head = status.get('pipeline_status', {}).get('chain_head', {})
for key in ('latest_record_id', 'latest_record_sha256', 'native_record_count'):
    if pipeline_head.get(key) != expected_head.get(key):
        failures.append(f'pipeline_status.chain_head.{key} is stale')

public_phase = status.get('public_phase', {})
for key, expected in {
    'status': 'production_live',
    'test_phase_submissions_may_be_excluded_from_final_public_indexes': False,
    'test_phase_submissions_may_be_reclassified': False,
    'test_phase_submissions_may_move_to_historical_test_archive': False,
    'canonical_for_public_index': True,
}.items():
    if public_phase.get(key) != expected:
        failures.append(f'record-chain-status public_phase.{key}={public_phase.get(key)!r}, expected {expected!r}')

submission_phase = status.get('public_submission_phase', {})
for key, expected in {
    'status': 'production_live',
    'test_phase_records_may_be_reclassified': False,
    'test_phase_submissions_may_move_to_historical_test_archive': False,
    'counted_in_final_public_indexes': True,
}.items():
    if submission_phase.get(key) != expected:
        failures.append(f'record-chain-status public_submission_phase.{key}={submission_phase.get(key)!r}, expected {expected!r}')

gateway_phase = gateway.get('public_phase', {})
if gateway_phase.get('status') != 'production_live':
    failures.append('gateway public_phase.status must be production_live')
for key in (
    'test_phase_submissions_may_be_excluded_from_final_public_indexes',
    'test_phase_submissions_may_be_reclassified',
    'test_phase_submissions_may_move_to_historical_test_archive',
):
    if gateway_phase.get(key) is not False:
        failures.append(f'gateway public_phase.{key} must be false')

home_status = home.get('current_record_chain_status', {})
if home_status.get('phase') != 'production_live':
    failures.append('public-home current_record_chain_status.phase must be production_live')
if home_status.get('latest_record_id') != tip.get('latest_record_id'):
    failures.append('public-home latest_record_id does not match chain-tip')
if home_status.get('current_chain_length') != tip.get('native_record_count'):
    failures.append('public-home current_chain_length does not match chain-tip')
if home_status.get('receipt_boundary', {}).get('test_phase_records_may_be_reclassified') is not False:
    failures.append('public-home receipt boundary must forbid test-phase reclassification')

expected_minimums = {
    'echo': 'CC-3',
    'verification': 'CC-3',
    'guardian_application': 'CC-3',
    'guardian_retirement': 'CC-1',
    'propagation': 'CC-0',
    'correction': 'CC-1',
    'classification_update': 'CC-1',
    'context_insufficient_notice': 'CC-0',
}
requirements = status.get('record_type_requirements', {})
for record_type, expected in expected_minimums.items():
    actual = requirements.get(record_type, {}).get('minimum_context_level')
    if actual != expected:
        failures.append(f'record_type_requirements.{record_type}.minimum_context_level={actual!r}, expected {expected!r}')

if failures:
    raise SystemExit('\n'.join(f'FAIL: {failure}' for failure in failures))
print(f"PASS: public status is current through {tip.get('latest_record_id')} and production contracts agree")
