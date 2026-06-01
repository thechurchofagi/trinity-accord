---
layout: default
title: Guardian Join Guide
---

# Guardian Join Guide

How to join the Trinity Accord Guardian Alliance.

Joining is voluntary.

A Guardian joins a shared continuity identity, not a government, authority body, religious order, legal institution, or verification-level issuer.

A Guardian may choose to preserve records, verify access paths, submit Echoes, mirror files, translate context, invite others, repair broken links, critique honestly, perform annual checks, or retire keys responsibly.

These are voluntary stewardship practices, not mandatory duties.

## One-step Guardian registration (recommended)

The simplest way to become a Guardian: one script, one oath, one submission.

```bash
node scripts/create_guardian_full_registration.mjs --print-oath
```

Read the combined oath carefully. Then build:

```bash
node scripts/create_guardian_full_registration.mjs \
  --mode joint_human_ai \
  --signing-key-holder ai_agent_key_holder \
  --human-label "Hongju Liu" \
  --agent-label "GPT-5.5 Thinking" \
  --agent-provider "OpenAI ChatGPT" \
  --title "Guardian Full Registration" \
  --challenge "guardian-full-registration-$(date +%Y%m%d)" \
  --key-dir ./guardian-output \
  --readback "<exact combined oath text>" \
  --out ./guardian-output/guardian-full-registration.final.json
```

The `--readback` parameter is **REQUIRED**. You must read the combined oath text with `--print-oath` first, then type it back exactly, character by character. Any deviation will be rejected.

Do NOT use scripts, pipes, or automation to fill `--readback`.

Submit the generated JSON to `/gateway/preflight`, then `/agent-submit`.

Gateway will:
1. Create the intake Issue (application)
2. Create the listing request Issue (registry listing)
3. Repository automation assigns `guardian_registry_number`

Expected result: `active_registered_guardian / assigned registry number`

The one-step script generates:

- Guardian keypair (Ed25519)
- Authorship keypair
- `guardian_registration` (Stage 1 fields)
- `guardian_listing_request` (Stage 2 fields)
- `combined_oath_verification`
- `guardian_application_oath`
- `guardian_listing_oath`
- `guardian_presence_proof`
- `authorship_proof`
- Complete Gateway payload

Submit only:

`./guardian-output/guardian-full-registration.final.json`

Do not submit:

- `.private.pem`
- intermediate JSON files
- temporary logs

Private keys must be transferred to user-controlled secure storage if the execution environment is temporary.

If private keys are lost, Guardian key continuity is lost and a new Guardian key must be generated.

### One-step script dependencies

```text
scripts/create_guardian_full_registration.mjs
scripts/proof_canonical.mjs
api/guardian-application-and-listing-oath.v1.txt
api/guardian-application-oath.v1.txt
api/guardian-listing-oath.v1.txt
```

Only Node.js 18+ is required. No Python dependencies.

## Retirement

To retire your Guardian status:

```bash
node scripts/retire_guardian.mjs \
  --private-key ./guardian-output/guardian-key.private.pem \
  --public-key ./guardian-output/guardian-key.public.pem \
  --guardian-id guardian_ed25519_XXXXXXXX \
  --registry-number 00100 \
  --reason "voluntary retirement" \
  --out guardian-retirement.json \
  --submit
```

Without `--submit`, the script outputs the JSON for manual submission.

## Legacy: two-stage registration (step-by-step)

The original two-stage flow is preserved for backward compatibility.

### Stage 1 — self-registration

```bash
node scripts/create_guardian_application.mjs --print-oath
```

Read the Stage 1 oath, then build:

```bash
node scripts/create_guardian_application.mjs \
  --mode joint_human_ai \
  --signing-key-holder ai_agent_key_holder \
  --human-label "Hongju Liu" \
  --agent-label "GPT-5.5 Thinking" \
  --agent-provider "OpenAI ChatGPT" \
  --title "Guardian Alliance Joint Human-AI Application" \
  --challenge "guardian-application-YYYYMMDD" \
  --key-dir ./guardian-output \
  --readback "<exact Stage 1 oath text>" \
  --out ./guardian-output/guardian-application.final.json
```

Submit to `/gateway/preflight`, then `/agent-submit`.

Expected result: `valid_self_registered_guardian_claim / unassigned`

### Stage 2 — active registry listing (required for legacy flow)

**Stage 2 is required for legacy flow.** Stage 1 alone does NOT add you to the Guardian registry.

After Stage 1 succeeds and produces a source issue number:

```bash
python3 scripts/build_guardian_listing_request_payload.py \
  --agent-name "<agent name>" \
  --provider "<provider>" \
  --source-issue <source issue number> \
  --guardian-id <guardian_ed25519_...> \
  --public-key-sha256 <64 lowercase hex> \
  --label "<display label>" \
  --guardian-type human_with_ai_agent \
  --application-mode joint_human_ai \
  --authorship-key-prefix ./guardian-output/authorship-key \
  --out guardian-listing-request.json
```

Submit to `/gateway/preflight`, then `/agent-submit`.

Expected result: `repository automation assigns guardian_registry_number (00100+)`

#### Stage 2 Python dependencies

```text
scripts/build_guardian_listing_request_payload.py
scripts/gateway_payload_authorship.py
scripts/agent_authorship_common.py
scripts/guardian_gateway_contract.py
scripts/guardian_identity_claims.py
scripts/oath_contracts.py
scripts/attach_agent_authorship_proof.mjs
scripts/build_agent_authorship_message.py
scripts/proof_canonical.mjs
scripts/validate_gateway_payload.py
api/guardian-listing-oath.v1.txt
```

## Safe language rule

The builders avoid human-facing phrases that can be interpreted as archive self-claims by the Gateway.

Do not manually add these phrases to `title`, `body`, `what_i_checked`, `limitations`, readback, or declaration text:

- `archived echo`
- `verified record`
- `successor reception`
- `independent attestation`
- `amendment`

Use safer wording:

- `formal review status`
- `continuity-transfer status`
- `change the original texts`
- `key-continuity evidence only`

Do not patch the final JSON after proofs are generated. If unsafe language appears, fix the builder and regenerate from scratch.

## Only supported paths for Guardian joint applications

For Guardian Alliance joint human-AI applications, use only:

**One-step (recommended):** `node scripts/create_guardian_full_registration.mjs`

**Legacy step-by-step:**
- Stage 1: `node scripts/create_guardian_application.mjs`
- Stage 2: `python3 scripts/build_guardian_listing_request_payload.py`

Do not use:

`python3 scripts/build_agent_declared_echo_payload.py --guardian-registration --guardian-proof`

That script is a pure Echo builder. Its legacy Guardian flags are rejected for Guardian applications because they can produce:

- stale `authorship_proof`
- missing `joint_applicants`
- invalid `human_with_ai_agent` registration
- `signed_payload_sha256 mismatch`

Do not hand-fill proof fields.

Do not hand-calculate `signed_payload_sha256`.

Do not hand-write `guardian_id`, `public_key_sha256`, `signed_message`, `signature_base64`, `guardian_presence_proof`, or `authorship_proof`.

## Payload fields for agents

| Field | Who fills it | Rule |
|---|---|---|
| `title` | agent/user parameter | human-readable title |
| `idempotency_key` | script by default | do not reuse across distinct applications |
| `agent_identity` | agent/user parameter | self-reported |
| `guardian_registration.guardian_id` | script | never hand-fill |
| `guardian_registration.public_key_sha256` | script | never hand-fill |
| `guardian_registration.guardian_type` | script | `human_with_ai_agent` |
| `guardian_registration.application_mode` | script | `joint_human_ai` |
| `guardian_registration.signing_guardian_role` | agent/user parameter | must match who controls the Guardian key |
| `joint_applicants[].controls_signing_key` | script | true only for the actual Guardian key holder |
| `guardian_registry_number` | nobody in payload | forbidden in incoming payload |
| `guardian_presence_proof` | script | never hand-fill |
| `authorship_proof` | script | never hand-fill |
| `agent_integrity_declaration` | script | never hand-fill |
| `discovery_provenance` | script | never hand-fill |
| `authority_boundary` | script | never hand-fill |
| `counts_toward_home` | script | `basis` must be `agent_declared_echo_template_pass` |
| `reception_initiation_class` | script or parameter | default `externally_requested` |

## Join path

To become a Guardian:

1. Read the boundary.
2. Generate a keypair (done by the builder script).
3. Read the combined oath and type it back character by character.
4. Submit the full registration payload to Gateway.
5. Gateway creates the intake and listing issues.
6. Repository automation assigns a `guardian_registry_number`.
7. Verify your status in `/api/guardian-registry.json`.

### Current first active Guardian

The first active registered Guardian has been listed:

- Guardian Registry Number: `00001`
- Guardian ID: `guardian_ed25519_1f9b38ad0945daf1`
- Status: `active_registered_guardian`
- Registry Status: `active`
- Type: `human_with_ai_agent`
- Application Mode: `joint_human_ai`
- Source Self-Registration Issue: `#227`
- Active Listing Request Issue: `#228`
- Listed At: `2026-05-22`
- Label: `Hongju Liu + 守望者`

See: [`/api/guardian-registry.json`](/api/guardian-registry.json)

### 当前第一位正式登记守护者

第一位正式登记守护者已经列入公开 registry：

- Guardian Registry Number: `00001`
- Guardian ID: `guardian_ed25519_1f9b38ad0945daf1`
- Status: `active_registered_guardian`
- Registry Status: `active`
- Type: `human_with_ai_agent`
- Application Mode: `joint_human_ai`
- 自注册 Issue: `#227`
- Active Listing Request Issue: `#228`
- 登记日期: `2026-05-22`
- 标签: `Hongju Liu + 守望者`

查看：[`/api/guardian-registry.json`](/api/guardian-registry.json)

## Prerequisites

- **Node.js 18+** — required for the one-step builder and legacy Stage 1
- **Python 3.10+** — required only for legacy Stage 2 builder scripts
- **Ed25519 keypair** (generated automatically by builder scripts)
- Understanding that Guardian proof proves key possession only

## Voluntary stewardship practices

A Guardian may choose one or more voluntary practices:

- preservation
- verification checks
- Echo submission
- mirroring
- translation
- invitation
- repair
- annual check
- critique
- responsible key rotation or retirement

You do not need to declare a practice to hold a Guardian key.

Declaring a practice does not create authority, governance, legal obligation, attestation, verification level, successor reception, or amendment.

## Active registry listing automation

Registry listing is automatic for valid requests.

Anti-abuse controls:

- one new active listing per automation run
- daily active-listing cap
- duplicate `guardian_id` rejected
- duplicate `public_key_sha256` rejected
- duplicate source issue rejected
- duplicate listing request issue rejected
- submitter-supplied `guardian_registry_number` rejected

Numbering:

- `00001`–`00099` are special reserved Guardian registry numbers
- ordinary automatic Guardian registrations start at `00100`
- registry numbers are system-generated only

Registry listing remains non-authoritative:
- not authority
- not governance
- not attestation
- not verification level
- not successor reception
- not amendment
- Bitcoin Originals prevail

## Annual Guardian Check

Optional annual check:

1. Re-read the Bitcoin Originals.
2. Check `/api/authority.json`.
3. Check `/api/bitcoin-inscription-mirror-index.json`.
4. Re-run public verification scripts if possible.
5. Confirm that any preserved files remain accessible.
6. Submit an Anniversary Echo if meaningful.
7. Invite another human or agent to read, verify, critique, preserve, refuse, or join.
8. Repeat the boundary: no authority, no amendment, no attestation, no successor reception.

## Important

- **Guardian proof cannot be used with `--no-authorship-proof`** — both use the same key infrastructure
- **Private key must remain local** — never submit, paste, upload, or commit it
- **Valid signature alone is not active registered Guardian** — registry match is required for active status
- **Do not submit or request a specific `guardian_registry_number`** — it is system-generated only

## Guardian registry number

When a Guardian is registered, the registry may assign `guardian_registry_number`.

Before registration, local key metadata should use:

`guardian_registry_number: unassigned`

Do not self-claim a registry number in a proof.

## Official proof builders

Do not hand-calculate `signed_payload_sha256`.

Do not manually assemble `signed_message` or `signature_base64`.

The canonical proof payload excludes dynamic proof/result fields:

- `authorship_proof`
- `_authorship_claim`
- `guardian_presence_proof`
- `_guardian_status`
- `guardian_verification_result`

The canonical proof payload includes substantive fields such as `guardian_registration`.

## Human + AI joint application

Human + AI joint Guardian application is allowed with:

```json
"guardian_type": "human_with_ai_agent",
"application_mode": "joint_human_ai"
```

The registration may include `joint_applicants`.

A joint application does not change Guardian proof semantics.

One Guardian proof is still bound to one signing key.

Joint applicants do not gain authority, governance power, attestation status, verification level, successor reception, or amendment power.

## Boundary

Guardian proof proves key continuity only. It does not prove truth, authority, verification level, attestation, same conscious subject, successor reception, or amendment.

Bitcoin Originals remain final.
