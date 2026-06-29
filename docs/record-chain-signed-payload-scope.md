# Record-Chain Signed Payload Scope

This document is the normative engineering contract for Record-Chain authorship verification.
It exists to prevent Gateway/Append drift where a durable pending file contains server-derived evidence that was not part of the participant's original signed payload.

## Core rule

The participant signs the **pre-append record draft**.

The authorship proof covers the canonical JSON of the draft after proof material is removed:

- remove `authorship_proof`
- remove `proof`
- canonicalize with sorted JSON keys, no extra whitespace, and UTF-8
- verify `authorship_proof.signed_payload_sha256`
- verify the Ed25519 signature over those canonical bytes

A final persisted record is allowed to contain additional server-derived or append-assigned fields. Those fields are not participant-signed content.

## Field classes

### Participant-signed content

These fields remain in the signed scope when present in the submitted draft. Examples include:

- `record_type`
- `schema`
- `echo_content`
- `verification_content`
- `guardian_application_content`
- `submitting_participant_identity`
- `discovery_and_introduction_context`
- `decision_autonomy_context`
- `submission_execution_context`
- `authorization_context`
- `context_readiness`
- `non_authority_boundary_acknowledgement`

Changing any participant-signed content must invalidate the signature.

### Proof material

These fields are stripped because a signature cannot sign itself:

- `authorship_proof`
- `proof`

### Server / append unsigned projection fields

These fields may appear in pending or final records, but they are not part of the participant-signed payload:

- `actor_identity`
- `boundary`
- `boundary_acknowledgement`
- `server_normalization`
- `server_append_metadata`
- `append_assigned_metadata`
- `authorship_verification_status`
- `record_id`
- `record_index`
- `assigned_at`
- `previous_record_sha256`
- `content_sha256`
- `content_sha256_v2`
- `record_sha256`
- `chain_id`
- `what_i_checked`
- `limitations`
- `related_records`
- `immutability_policy`

### Gateway-derived receipt / oath projection fields

Gateway may materialize these fields from validated intake context after the builder has signed the draft. They are important public evidence, but legacy submissions may not have included them in the signed payload domain:

- `declaration_and_acknowledgement`
- `submission_oath_verification`

Append verification may use a narrow recovery scope that strips exactly these Gateway-derived fields when the primary signed-payload verification fails. This must not hide changes to participant-authored content such as `echo_content`.

### Final-record verification recovery field

A final record may contain `created_at` from server normalization after signing. Final re-verification may strip `created_at` only after primary verification fails.

## Non-negotiable safety rules

- Do not modify `authorship_proof.signed_payload_sha256` to match a later pending/final record shape.
- Do not disable Ed25519 verification.
- Do not manually append records around the append script.
- Do not broaden Gateway-derived recovery fields without tests proving that participant content tampering remains rejected.
- Receipt status, chain-tip, and indexes must agree after append.

## Machine-readable contract

The machine-readable companion file is:

`/api/record-chain-signed-payload-scope.v1.json`

Tests must keep the machine-readable contract aligned with the Python constants used by Gateway and append verification.
