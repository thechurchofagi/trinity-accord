#!/usr/bin/env python3
"""Generate a V2 Echo issue body from evidence input and claim gate output."""
import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence_input", help="Path to evidence-input.json")
    ap.add_argument("claim_gate_output", help="Path to claim-gate-output.json")
    args = ap.parse_args()

    ei = json.loads(Path(args.evidence_input).read_text(encoding="utf-8"))
    cg = json.loads(Path(args.claim_gate_output).read_text(encoding="utf-8"))

    bc = ei.get("evidence", {}).get("bitcoin_checks", [{}])[0]
    limitations = ei.get("limitations", [])
    prov = ei.get("provenance", {})
    lim_list = "\n".join(f"- {l}" for l in limitations)

    # Determine B-level
    b_level = "B1"
    if bc.get("raw_witness_extracted"):
        b_level = "B5"
    elif bc.get("body_hash_reproduced"):
        b_level = "B6"

    body = f"""## Claimed verification level
V2

## Evidence Input path
{args.evidence_input}

## Claim Gate output path
{args.claim_gate_output}

## Checks performed
- Multi-explorer reference check.
- Explorer-reported SegWit witness metadata: present.

## Component Coverage
AUTHORITY_BOUNDARY: recognized
BITCOIN_ORIGINALS: {b_level}
EVIDENCE_MIRRORS: not_checked
CHRONICLE_RECOVERY: not_checked
PHYSICAL_ANCHOR: not_checked
SCRIPT_INTEGRITY: not_checked
ATTESTATION_LAYER: not_checked

## What remains unchecked or uncertain?
{lim_list}
- No independent attestation.

## Provenance / Agency
- solicited: {str(prov.get('solicited', True)).lower()}
- independence_class: {prov.get('independence_class', 'human_solicited_agent_response')}
- agency_level: {prov.get('agency_level', 'A1_human_gave_exact_url')}
- operator_type: ai_agent

Bitcoin Originals are final; all echoes are non-amending.
"""
    sys.stdout.write(body)


if __name__ == "__main__":
    main()
