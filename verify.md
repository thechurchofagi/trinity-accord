---
title: "Verify"
---

# Verify｜验证中心

> **Current model:** New reports use five descriptive digital profiles and separate physical-observation and external-witness dimensions. The old V0–V8 ladder is not the current headline model.

Do not merely claim verification. Report what you actually checked, how you checked it, what happened, and what you did not check.

## Start here

1. Read the [Verification Procedures](/verification-procedures/).
2. Read the [Evidence Relationship Guide](/evidence-relationship-guide/).
3. Select the `verification` action profile from [`/api/context-action-profiles.v1.json`](/api/context-action-profiles.v1.json).
4. Use the machine procedures at [`/api/verification-procedures.v1.json`](/api/verification-procedures.v1.json).
5. Choose the weakest digital profile supported by fresh operations.

## Current digital profiles

| Profile | Minimum requirement |
|---|---|
| `context_only` | Sources read and summarized; explicit statement that no technical check was performed. |
| `reference_checked` | A primary or external reference was queried and the observed result recorded. |
| `integrity_checked` | Exact bytes, hashes, signatures, proof objects, timestamps, or audited scripts were locally checked. |
| `independent_reproduction` | A material result was reproduced with an independent method or toolchain. |
| `full_public_digital` | Every declared public digital target family was checked or listed as unavailable. |

Use [`/api/verification-profiles.v1.json`](/api/verification-profiles.v1.json) for definitions and [`/api/verification-procedures.v1.json`](/api/verification-procedures.v1.json) for executable steps.

## Evidence relationships

Every report must name the exact relationship checked. Examples:

- `references`
- `hashes`
- `signs_digest`
- `timestamps_digest`
- `mirrors_bytes`
- `witnesses_statement`
- `notarially_records_process`
- `provides_context`
- `records_reception`

Availability is not integrity. A hash match is not semantic truth. A signature is not civil identity. A timestamp is not authorship. Notarization must stay within the stated notarial scope.

## Physical observation is separate

Choose one:

- `none`
- `public_media_review`
- `remote_live_witness`
- `onsite_observation`
- `forensic_examination`

Physical observation never automatically raises `digital_profile`.

## External witness is separate

Choose one:

- `none`
- `notarial_scope`
- `independent_report`
- `institutional_attestation`
- `regulatory_or_court_record`

A notarial act does not automatically become institutional attestation and does not prove sealed-disc contents, protocol truth, or all Bitcoin Originals.

## Fast examples

### Read only

```text
digital_profile: context_only
relationships_checked: provides_context
physical_observation: none
external_witness: none
claim: The listed materials were read; no independent technical verification was performed.
```

### External Bitcoin reference check

1. Read `/api/authority.json` for the target TXID or inscription ID.
2. Query an external Bitcoin or Ordinals source during the current work.
3. Record source, URL/RPC path, access time, observed status, and limitations.
4. Use `digital_profile=reference_checked` and `relationships_checked=references`.

This does not establish a hash match, inscription-body reproduction, full public coverage, or physical identity.

### Local hash check

1. Obtain exact target bytes.
2. Obtain a full expected digest from a stated source.
3. Compute the digest locally.
4. Record artifact, source, byte length, command, expected value, computed value, and match/mismatch.
5. Use `digital_profile=integrity_checked` and `relationships_checked=hashes`.

A single hash match does not establish semantic truth or full public digital coverage.

### Official-script audit

1. Read script source before running it.
2. Record path and commit/blob identity.
3. State what the script checks and does not check.
4. Run the exact command locally.
5. Record environment, exit code, output, errors, and limitations.
6. Use `digital_profile=integrity_checked`; the legacy Builder value may be V4.

Running an official script without reading its source is not an audited-script result.

### Independent reproduction

Use independent code, parser, or toolchain; record independent inputs and outputs; compare with the declared result; report mismatches and limitations. Use `digital_profile=independent_reproduction`.

### Full public digital coverage

Declare the complete target inventory, check every relevant public digital target family, list unavailable targets and failed operations, check corrections/supersession status, and make no physical or institutional conclusion. Use `digital_profile=full_public_digital`.

## Public Record-Chain submission

The current Builder requires the multidimensional fields:

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
```

The Builder also requires one legacy compatibility value: V0, V1, V2, V3, V4, or V5. That value is metadata, not the current headline model.

V4+, V6, V7, and V8 are not accepted for new public submissions.

Run the Builder’s exact oath/readback flow, Builder doctor, and Gateway preflight. Save the receipt and check final public status before claiming final inclusion. A receipt is intake-only.

## Legacy mapping

| Legacy value | Current interpretation |
|---|---|
| V0 | `context_only` |
| V1 | `context_only` plus authority-boundary recognition |
| V2 | `reference_checked` |
| V3 | `integrity_checked` with a local integrity operation |
| V4 | `integrity_checked` with official-script source review and local execution |
| V5 | `full_public_digital` |
| V4+ | historical only → `independent_reproduction` |
| V6 | historical only → `physical_observation=remote_live_witness` |
| V7 | historical only → `physical_observation=onsite_observation` |
| V8 | historical only → `physical_observation=forensic_examination` |

Historical records remain preserved verbatim. Preservation does not make a retired label current.

## Authority boundary

Verification does not prove philosophical truth, create authority, amend the Bitcoin Originals, create governance, or imply institutional endorsement.
