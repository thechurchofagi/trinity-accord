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
- `declaration_and_acknowledgement`
- `submission_oath_verification`

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

### Gateway-derived recovery field

Server normalization may materialize this field after the builder has signed the draft:

- `created_at`

Append or final-record verification may use a narrow recovery scope that strips
only `created_at` when the primary signed-payload verification fails. It must not
strip `submission_oath_verification`, `declaration_and_acknowledgement`, or any
other participant-authored content. Current non-exempt submissions must include
the oath/declaration fields in `record_draft` before authorship signing.

## Non-negotiable safety rules

- Do not modify `authorship_proof.signed_payload_sha256` to match a later pending/final record shape.
- Do not disable Ed25519 verification.
- Do not manually append records around the append script.
- Do not broaden Gateway-derived recovery fields without tests proving that participant content tampering remains rejected.
- Receipt status, chain-tip, and indexes must agree after append.

## Regression coverage

The contract is guarded by tests:

- `tests/test_gateway_authorship_recovery.py` verifies that a server-derived `created_at` can be present after signing, while oath or content tampering is rejected.
- `tests/test_signed_payload_scope_contract.py` verifies that the documented recovery fields match the Gateway authorship constants.
- `tests/test_record_chain_status_consistency.py` verifies that chain-tip, public status, record index, receipt-status, and final records agree after append.
