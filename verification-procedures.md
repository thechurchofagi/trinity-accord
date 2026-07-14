---
title: "Verification Procedures"
permalink: /verification-procedures/
---

# Verification Procedures｜验证操作规程

The machine-readable source of truth is [`/api/verification-procedures.v1.json`](/api/verification-procedures.v1.json).

> Verification is non-authoritative and non-amending. The three Bitcoin Originals remain the sole final canonical authority.

## Current report model

A new report records separate dimensions:

- `digital_profile`
- `relationships_checked`
- `physical_observation`
- `external_witness`
- `coverage_scope`
- `limitations`
- `claims_not_made`
- `corrections_or_supersession_checked`

The five digital profiles are:

| Profile | Minimum meaning |
|---|---|
| `context_only` | Sources read; no technical check. |
| `reference_checked` | A primary or external reference was queried. |
| `integrity_checked` | Bytes, hashes, signatures, proofs, timestamps, or audited scripts were locally checked. |
| `independent_reproduction` | A material result was reproduced with an independent method. |
| `full_public_digital` | Every declared public digital target family was checked or listed as unavailable. |

Physical observation and external witness are independent dimensions. They never automatically increase the digital profile.

## Required workflow

1. Write one bounded proposed claim and list claims not made.
2. List every target.
3. Name the exact evidence relationship checked.
4. Load exact source inputs and expected-value sources.
5. Perform fresh operations and record commands, tools, versions, access times, outputs, errors, and exit codes.
6. Record pass, mismatch, unavailable, inconclusive, or error for every target.
7. Choose the weakest supported digital profile.
8. Report physical observation separately.
9. Report external witness separately.
10. State limitations and downgrade when any requirement is missing.
11. Use Builder doctor and Gateway preflight for public submission. A receipt is intake-only.

## Profile procedures

### `context_only`

List sources, summarize them, state the authority boundary where relevant, and explicitly say no independent technical verification was performed.

Legacy Builder mapping: V0 or V1.

### `reference_checked`

Identify the target, query a primary or external source, record the exact access path and time, record the observed result, and state what was not checked. Use a second independent source before claiming strong reference coverage.

Legacy Builder mapping: V2.

### `integrity_checked`

Obtain exact bytes or proof material, identify the expected value and source, perform the operation locally, record the exact command/tool/version/output, compare observed and expected values, and state the operation’s limits.

For official scripts, read source before execution and record what the script checks and does not check.

Legacy Builder mapping: V3 for direct integrity operations; V4 for audited official-script execution.

### `independent_reproduction`

Use independently written code, an independent parser, or a separately selected toolchain. Record independent inputs, method, output, comparison, mismatches, and limitations. One independently reproduced component does not establish whole-protocol reproduction.

Historical V4+ maps here. V4+ is not accepted as a new public legacy V value.

### `full_public_digital`

Declare the complete public digital target inventory, check every relevant target family, list all unavailable targets and failures, check corrections/supersession status, and make no physical or institutional conclusion.

Legacy Builder mapping: V5.

## Physical observation

- `none`: no physical material reviewed.
- `public_media_review`: exact public photos/videos reviewed; no live, custody, onsite, or forensic claim.
- `remote_live_witness`: live session, fresh challenge, requested action/angle, time and witness role recorded; historical mapping V6.
- `onsite_observation`: direct observation, location/date/observer role, custody or association record, fresh capture where permitted; historical mapping V7.
- `forensic_examination`: documented instruments/methods, reproducible measurements, comparison criteria, attributable examiner where applicable, uncertainty and custody limits; historical mapping V8.

## External witness

- `none`
- `notarial_scope`: report only the process, document, identity, or date actually covered by the notarial act.
- `independent_report`: separately authored report with method and limitations.
- `institutional_attestation`: an accountable institution formally adopts the exact report.
- `regulatory_or_court_record`: report the exact jurisdictional and operative scope.

A notarial certificate is not automatically an institutional attestation and does not prove sealed-disc contents, protocol truth, or all Bitcoin Originals.

## Legacy compatibility

| Legacy value | Current meaning |
|---|---|
| V0 | `context_only` |
| V1 | `context_only` plus authority-boundary recognition |
| V2 | `reference_checked` |
| V3 | `integrity_checked` |
| V4 | `integrity_checked` with audited official-script execution |
| V5 | `full_public_digital` |
| V4+ | historical only → `independent_reproduction` |
| V6 | historical only → `remote_live_witness` |
| V7 | historical only → `onsite_observation` |
| V8 | historical only → `forensic_examination` |

New public submissions accept only V0–V5 in the legacy compatibility field. The multidimensional fields carry the current meaning.
