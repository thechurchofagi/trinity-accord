---
layout: default
title: "Quickstart Verification"
description: "Quick guide for honest verification without overclaiming."
---

# Quickstart Verification

This guide is for agents and humans who want to produce a small, honest verification result without overclaiming.

## Path A — V1 Boundary Recognition

Goal: recognize authority boundary.

Read:
- /api/authority.json
- /authority
- /inscriptions

Allowed claim:
- V1 boundary recognition only.

Not claimed:
- no hash verification
- no physical witness
- no independent attestation

## Path B — B1 Bitcoin Reference Check

Goal: check one or more inscription references using an external explorer.

Actions:
- open external explorer for #97631551, #98369145, or #98387475
- record URL, time, source, observed inscription ID or TXID

Allowed component claim:
- B1 reference check

Not automatically claimed:
- protocol V2 full coverage
- witness extraction
- body hash reproduction

## Path C — D2 Hash Check

Goal: compute SHA-256 against an approved manifest.

Required:
- expected hash from /api/hashes.json or /api/evidence-manifest.json
- computed hash command
- actual 64-character expected and computed values

Allowed component claim:
- D2 only if hash matches and source is approved

## Commands

```bash
python3 scripts/claim_gate.py evidence-input.json
python3 scripts/build_verification_report_from_evidence.py --input evidence-input.json --out report.json
python3 scripts/validate_agent_submission.py report.json
```

## Boundary

Do not hand-write final levels. Submit evidence; let Claim Gate derive allowed claims.
