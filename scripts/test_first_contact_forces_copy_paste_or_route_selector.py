#!/usr/bin/env python3
"""Current first-contact surfaces must select the Record-Chain route and reject retired Gateway v1 guidance."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CURRENT=["/api/agent-first-contact.json","/downloads/record-chain-builder.mjs","/api/record-chain-builder-bundles.v1.json","/api/record-chain-intake-gateway.v1.json","/record-chain/preflight","/record-chain/submit"]
FORBIDDEN=["/gateway/preflight","/agent-submit","/api/route-selector.v1.json","/api/gateway-runtime-contract.v1.json"]
def main()->int:
    errors=[]
    for rel in ("llms.txt","ai.txt"):
        text=(ROOT/rel).read_text(encoding="utf-8")
        for marker in CURRENT:
            if marker not in text: errors.append(f"{rel}: missing current marker {marker}")
        for marker in FORBIDDEN:
            if marker in text: errors.append(f"{rel}: exposes retired route {marker}")
    first=json.loads((ROOT/'api/agent-first-contact.json').read_text())
    method=first.get('current_public_submission_method',{})
    expected={
      'builder':'/downloads/record-chain-builder.mjs',
      'builder_manifest':'/api/record-chain-builder-bundles.v1.json',
      'contract':'/api/record-chain-intake-gateway.v1.json',
      'preflight':'https://trinity-record-chain-gateway.onrender.com/record-chain/preflight',
      'submit':'https://trinity-record-chain-gateway.onrender.com/record-chain/submit',
    }
    for key,value in expected.items():
        if method.get(key)!=value: errors.append(f"first-contact {key} drifted")
    if method.get('render_is_only_public_submission_method') is not True: errors.append('first-contact must bind public submission to Render Gateway')
    intents={i.get('intent') for i in first.get('choose_one',[]) if isinstance(i,dict)}
    if 'submit_record' not in intents: errors.append('first-contact missing submit_record')
    retired=json.dumps(first,sort_keys=True)
    for marker in ('verify_v0_v5_agent_declared','verification_echo_e2','verify_v6_plus_strict_evidence'):
        if marker in retired: errors.append(f"first-contact contains retired intent {marker}")
    if errors:
        print('FAIL: current first-contact contract errors:')
        for e in errors: print('  -',e)
        return 1
    print('PASS: first-contact forces the current Record-Chain Builder/Gateway route')
    return 0
if __name__=='__main__': raise SystemExit(main())
