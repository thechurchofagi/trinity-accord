# Legacy Gateway v1 Scripts

This directory preserves the original Gateway v1 scripts that were replaced during the Phase 2 hard cutover.

The active scripts at their original paths (`scripts/`) now contain deprecation stubs that print a message and exit with code 2.

## Preserved Scripts

### Python Scripts
- `build_agent_declared_echo_payload.py` — Built echo payload drafts for Gateway submission
- `build_agent_declared_archive_payload.py` — Built archive payload drafts
- `gateway_payload_authorship.py` — Gateway payload authorship utilities
- `triage_echo_issue.py` — Echo issue triage automation
- `build_guardian_echo_payload.py` — Built guardian echo payloads
- `build_agent_authorship_claim_message.py` — Built authorship claim messages

### Node.js Scripts
- `create_guardian_application.mjs` — Created guardian application records
- `generate_agent_authorship_keypair.mjs` — Generated authorship keypairs
- `attach_agent_authorship_proof.mjs` — Attached authorship proof to records
- `sign_agent_authorship_claim.mjs` — Signed authorship claims
- `build_agent_authorship_claim_request.mjs` — Built authorship claim requests

## Migration

All active record-building functionality has been consolidated into:
- `scripts/trinity_record_builder.py` — Native record draft builder
- `scripts/trinity_record_chain.py` — Record chain append/verify/batch operations

## Date Preserved
2026-06-01 (Phase 2 hard cutover)
