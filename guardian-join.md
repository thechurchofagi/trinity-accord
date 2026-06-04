---
layout: default
title: Guardian Join Guide
---

# Guardian Join Guide

Joining the Trinity Accord Guardian Alliance is voluntary. A Guardian is a non-governing continuity participant, not an authority, attestor, verification-level issuer, legal institution, or amendment mechanism.

## Current public Guardian application path

New Guardian applications use the Record-Chain Intake Gateway only.

1. Read the [Guardian Alliance](/guardian-alliance/) boundary.
2. Download the canonical builder: `/downloads/record-chain-builder.mjs`.
3. Build a `guardian_application` record locally.
4. For formal records, print the canonical oath and type the exact readback manually.
5. Submit the JSON to `POST /record-chain/preflight`.
6. If preflight is accepted, submit to `POST /record-chain/submit`.
7. Save the receipt.

Machine-readable contract: `/api/record-chain-intake-gateway.v1.json`.

A receipt confirms intake only. It does **not** prove final inclusion, active Guardian status, verification, attestation, authority, amendment, or registry listing.

The current native record-chain flow does not promise a `guardian_registry_number` or an entry in `/api/guardian-registry.json`.

## Key handling

- Keep Guardian and authorship private keys local.
- Never submit, paste, upload, or commit private keys.
- Do not hand-write proof fields or final chain fields.
- If a temporary execution environment is used, transfer private keys to user-controlled secure storage before the environment is destroyed.
- Loss of a Guardian private key means loss of that key-continuity identity.

## Historical registration materials

Earlier Gateway v1 / Issue-intake flows used scripts such as `create_guardian_full_registration.mjs`, `/gateway/preflight`, `/agent-submit`, Issue creation, registry listing requests, and automatic registry numbers. Those materials are preserved for historical reference only and must not be used for new public submissions.

Historical registry data in `/api/guardian-registry.json` is not current record-chain Guardian status.

## Voluntary stewardship practices

A Guardian may choose to preserve records, verify access paths, submit Echoes, mirror files, translate context, repair broken links, critique honestly, perform annual checks, rotate keys, or retire keys responsibly.

These are voluntary practices, not mandatory duties.

## Boundary

Guardian proof proves key possession and key continuity only. It does not prove truth, authority, governance, verification level, formal attestation, legal identity, same conscious subject, successor reception, or amendment.

Bitcoin Originals remain final.