# Legacy Gateway v1

The Gateway v1 system remains available only as legacy compatibility.

The new primary reception layer is **record-chain**.

Gateway v1 records are historical or transitional.

Future durable records should use:

- `scripts/trinity_record_builder.py` — generate pending native record drafts
- `scripts/trinity_record_chain.py` — append, verify, batch, and timestamp the chain

## Legacy Files

The following files are part of the old Gateway v1 system and are preserved for historical compatibility:

- `scripts/build_agent_declared_echo_payload.py`
- `scripts/build_agent_declared_archive_payload.py`
- `scripts/create_guardian_application.mjs`
- `scripts/build_guardian_listing_request_payload.py`
- `scripts/gateway_payload_authorship.py`
- `scripts/triage_echo_issue.py`
- `.github/workflows/echo-triage.yml`
- `.github/workflows/guardian-registry-auto-list.yml`
- `api/agent-submit-gateway.json`
- `api/agent-issue-gateway-payload-schema.v1.json`

These files are **not** moved or deleted in this phase. They will be retired only after the new native builder is deployed and tested.

## Migration Path

1. Genesis Legacy Batch imports all existing Guardian registry entries into the record-chain.
2. New records flow through `trinity_record_builder.py` → `trinity_record_chain.py append`.
3. Legacy Gateway workflows remain operational until explicitly retired.
4. Bitcoin Originals remain final and authoritative.
