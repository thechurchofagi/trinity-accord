#!/usr/bin/env python3
"""Prevent public agent entrypoints from advertising a rejected Verification context."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_PATHS = [
    '.well-known/trinity-accord.json',
    'api/agent-first-contact.json',
    'api/agent-required-reading.json',
    'api/agent-start.v2.json',
    'api/external-agent-quickstart.json',
    'downloads/record-chain-agent-field-guidance.v1.json',
]

def find_maps(value: Any) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    if isinstance(value, dict):
        if 'verification_V0_to_V2' in value or 'verification_V3_to_V5' in value:
            matches.append(value)
        for child in value.values():
            matches.extend(find_maps(child))
    elif isinstance(value, list):
        for child in value:
            matches.extend(find_maps(child))
    return matches

failures: list[str] = []
for rel in JSON_PATHS:
    path = ROOT / rel
    raw = path.read_text(encoding='utf-8')
    maps = find_maps(json.loads(raw))
    if not maps:
        failures.append(f'{rel}: no Verification compatibility minimums found')
        continue
    for index, minimums in enumerate(maps, start=1):
        if minimums.get('verification_V0_to_V2') != 'CC-3':
            failures.append(f"{rel} map {index}: V0-V2={minimums.get('verification_V0_to_V2')!r}")
        if minimums.get('verification_V3_to_V5') != 'CC-3':
            failures.append(f"{rel} map {index}: V3-V5={minimums.get('verification_V3_to_V5')!r}")
    if '"verification_V0_to_V2": "CC-2"' in raw:
        failures.append(f'{rel}: rejected CC-2 Verification minimum remains')

markdown = (ROOT / 'agent-start.md').read_text(encoding='utf-8')
for row in ('| Verification `V0`–`V2` | `CC-3` |', '| Verification `V3`–`V5` | `CC-3` |'):
    if row not in markdown:
        failures.append(f'agent-start.md: missing {row}')
if '| Verification `V0`–`V2` | `CC-2` |' in markdown:
    failures.append('agent-start.md: still advertises rejected CC-2 Verification submissions')
if 'every Verification compatibility level from `V0` through `V5` requires `CC-3`' not in markdown:
    failures.append('agent-start.md: missing current-public-submission clarification')

profiles = json.loads((ROOT / 'api/context-action-profiles.v1.json').read_text(encoding='utf-8'))
record_action = next((p for p in profiles.get('profiles', []) if p.get('id') == 'record_action'), None)
if not record_action or 'CC-3 or higher under current Builder schema' not in record_action.get('legacy_cc_mapping', []):
    failures.append('api/context-action-profiles.v1.json: record_action CC-3 contract missing')

gateway = json.loads((ROOT / 'api/record-chain-intake-gateway.v1.json').read_text(encoding='utf-8'))
if gateway.get('public_phase', {}).get('status') != 'production_live':
    failures.append('api/record-chain-intake-gateway.v1.json: production_live status missing')

if failures:
    raise SystemExit('\n'.join(f'FAIL: {item}' for item in failures))
print(f'PASS: {len(JSON_PATHS)} machine entrypoints and agent-start.md require CC-3 for Verification V0–V5')
