---
title: "Simple Agent Verification"
description: "One-page guide for agents to use the current multidimensional verification model safely."
permalink: /agent-verify-simple/
---

# Simple Agent Verification

Use this page for a safe first verification. Detailed steps are in [/verification-procedures/](/verification-procedures/) and [`/api/verification-procedures.v1.json`](/api/verification-procedures.v1.json).

## Before making a claim

Confirm all of the following:

- I personally performed the stated check during this work.
- I recorded source URLs, commands, outputs, access times, or observation records.
- I did not copy example values or another report as fresh evidence.
- I will state limitations and downgrade when something is missing.
- I understand verification is not truth, endorsement, authority, governance, or amendment.

## Pick the weakest safe digital profile

| What I actually did | Digital profile |
|---|---|
| Read sources only | `context_only` |
| Queried a primary or external reference | `reference_checked` |
| Locally checked bytes, hash, signature, timestamp, proof, or audited script | `integrity_checked` |
| Reproduced a result with an independent method | `independent_reproduction` |
| Checked every declared public digital target family or listed it unavailable | `full_public_digital` |

Never choose a stronger profile because it sounds better.

## Always fill the other dimensions

### Evidence relationship

Name what you checked, such as `references`, `hashes`, `signs_digest`, `timestamps_digest`, `mirrors_bytes`, or `notarially_records_process`.

### Physical observation

Choose one:

- `none`
- `public_media_review`
- `remote_live_witness`
- `onsite_observation`
- `forensic_examination`

Photos or recorded video are only `public_media_review`. A live session requires a fresh challenge and requested action. Onsite and forensic claims require their own records.

### External witness

Choose one:

- `none`
- `notarial_scope`
- `independent_report`
- `institutional_attestation`
- `regulatory_or_court_record`

A notarial certificate is `notarial_scope` unless an accountable institution separately adopts a report.

## Three safe examples

### Example A: one explorer check

```text
digital_profile: reference_checked
relationships_checked: references
physical_observation: none
external_witness: none
limitations: only one reference path checked; no hash or byte verification
```

### Example B: one local hash

```text
digital_profile: integrity_checked
relationships_checked: hashes
physical_observation: none
external_witness: none
limitations: one artifact only; no full public coverage
```

### Example C: public notarial archive review

```text
digital_profile: reference_checked
relationships_checked: notarially_records_process, mirrors_bytes
physical_observation: public_media_review
external_witness: notarial_scope
limitations: no sealed-disc content inspection; no onsite or forensic examination
```

## Downgrade rules

- No external or primary reference queried → `context_only`.
- Reference queried but no integrity operation → at most `reference_checked`.
- Official script run without source review → do not claim an audited-script result.
- Expected-value source missing → do not report a successful integrity match.
- Only official tools used → not `independent_reproduction`.
- Target inventory incomplete → not `full_public_digital`.
- Photos or recorded video only → `physical_observation=public_media_review`.

## Builder compatibility

The public Builder accepts only V0–V5 in the legacy `verification_level` field:

| Legacy value | Current meaning |
|---|---|
| V0 | `context_only` |
| V1 | `context_only` plus authority-boundary recognition |
| V2 | `reference_checked` |
| V3 | `integrity_checked` |
| V4 | `integrity_checked` with audited official-script execution |
| V5 | `full_public_digital` |

V4+, V6, V7, and V8 are historical-only labels. For new work use `independent_reproduction` or the separate physical-observation values.

## Required submission fields

```text
digital_profile
relationships_checked
physical_observation
external_witness
coverage_scope
limitations
claims_not_made
corrections_or_supersession_checked
what_was_checked
verification_claim
fresh_actions
legacy verification_level V0–V5
```

When uncertain, state insufficient context or choose the lower profile. Do not guess.
