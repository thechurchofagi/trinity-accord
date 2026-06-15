# Trinity Accord Record-Chain — Final Source-Level Repair Playbook v3

**Final version.**  
This document supersedes previous repair plans. It is designed to be handed to an authorized coding agent with repository write access.

**Repository:** `thechurchofagi/trinity-accord`  
**Target branch:** `main`  
**Repair strategy:** small verified batches, one branch/PR per batch, never one giant rewrite.  
**Primary objective:** repair the highest-risk Record-Chain integrity, lifecycle, receipt, archive, schema, and public-status bugs without breaking CI blindly or weakening verification.

---

## 0. Executive summary

The 80 reviewed findings should **not** be fixed as 80 independent PRs. They collapse into a smaller number of root-cause repair batches.

Final repair order:

1. **Batch 0 — Preflight inventory, no behavior changes**
2. **Batch A — Final-chain verification and hash semantics**
3. **Batch B — Guardian lifecycle safety**
4. **Batch C — Receipt / pending / append lifecycle**
5. **Batch D — Arweave / OTS integrity**
6. **Batch E — Gateway / Builder / schema parity**
7. **Batch F — Public status and native derived indexes**

The executing agent must finish, push, and validate one batch before starting the next.

The most important principle:

> CI red is not automatically a code bug and not automatically a CI bug. First classify the failure. Sometimes the correct fix is code, sometimes tests, sometimes generated artifacts, sometimes workflow CI.

---

## 1. Non-negotiable invariants

The executing agent must not violate these:

1. Do not alter the three Bitcoin Originals.
2. Do not rewrite historical final `record-chain/records/R-*.json` records unless the maintainer explicitly approves a migration.
3. Do not weaken final-chain verification to make CI pass.
4. Do not treat receipt intake as final inclusion.
5. Do not treat Guardian application append as Guardian activation.
6. Do not infer founding Guardian status from a user-controlled string.
7. Do not treat Arweave txid alone as archived/current.
8. Do not treat OTS upgraded/timestamp-proof-embedded as strict Bitcoin verification.
9. Do not mark unknown, stale, failed, missing, or legacy state as current.
10. Do not make broad, unrelated changes in a single PR.

---

## 2. Required working method

### 2.1 Start every batch from clean `main`

```bash
git checkout main
git pull --ff-only
git status
```

If `git status` is not clean, stop and report.

### 2.2 Create one branch per batch

```bash
git checkout -b fix/<batch-name>
```

Recommended branch names:

```text
fix/preflight-record-chain-repair-inventory
fix/final-chain-verify-authorship-oath-boundary
fix/guardian-lifecycle-derived-state
fix/receipt-append-lifecycle
fix/arweave-ots-integrity
fix/gateway-builder-schema-parity
fix/public-status-native-indexes
```

### 2.3 Do not start the next batch until the current batch is complete

A batch is complete only when:

1. source changes are committed;
2. local validation has run;
3. branch is pushed;
4. PR is opened or ready;
5. CI result has been reviewed;
6. failures, if any, are classified and either fixed or explicitly accepted by maintainer.

---

## 3. CI red-light decision tree

When CI turns red, follow this exact order.

### 3.1 Determine failure category

#### Category A — New code bug introduced by this PR

Examples:

- import error;
- syntax error;
- unit test fails on a behavior the PR intended to preserve;
- `python scripts/trinity_record_chain.py verify` fails because the new verifier reconstructs signed scope incorrectly.

Action:

- Fix code.
- Do not edit CI to hide the failure.

#### Category B — Test or snapshot encodes old buggy behavior

Examples:

- test expects CIN to skip authorship proof;
- test expects `accepted=false` CLI response to exit 0;
- test expects Guardian application to become active immediately;
- snapshot expects stale public status count;
- snapshot expects OTS “attestation” terminology.

Action:

- Update the test/snapshot.
- Add a short comment near the test explaining which bug it used to encode.
- Do not weaken production code.

#### Category C — Generated artifact drift

Examples:

- `api/record-chain-status.json` changes after running generator;
- native indexes are regenerated;
- helper JSON output changes.

Action:

- If artifacts are committed outputs, commit the generated outputs in the same PR.
- If too many unrelated generated files change, stop and report.
- If generator copies stale old JSON, fix generator before committing regenerated stale output.

#### Category D — CI workflow encodes the old pipeline

Examples:

- CI treats Arweave txid as current without `archive_status=archived`, `verified=true`, `hash_match=true`;
- CI runs live/network/secret-dependent checks in PR context;
- CI runs Arweave live upload before native chain verify;
- CI expects OTS upgraded to equal strict Bitcoin verified.

Action:

- Change CI/workflow if the workflow is part of the bug.
- Keep PR CI deterministic and secret-free.
- Move live network checks into scheduled/manual workflows unless secrets are available.

#### Category E — Historical compatibility conflict

Examples:

- old records fail newly strict oath/boundary/authorship rules;
- old records predate the final verification policy.

Action:

- Do not weaken the global rule.
- Add explicit, record-id-specific compatibility exceptions only if maintainers approve.
- Example pattern:
  ```python
  HISTORICAL_RECORD_COMPAT_EXCEPTIONS = {
      "R-0000000XX": {
          "reason": "pre-oath-v2 record; allowed missing submission_oath_verification",
          "allowed_missing": ["submission_oath_verification"],
      },
  }
  ```
- Exceptions must not apply to new records.

---

## 4. Minimum validation commands

Run these before pushing every behavior-changing batch:

```bash
python -m pytest
python scripts/trinity_record_chain.py verify
python scripts/verify_record_chain_arweave_archive.py
python scripts/detect_record_chain_pipeline_backlog.py
node downloads/record-chain-builder.mjs doctor --help >/dev/null
```

If imports fail because the project expects repo root on `PYTHONPATH`:

```bash
PYTHONPATH=. python -m pytest
```

If Node dependencies are needed:

```bash
npm ci
npm test
```

If CI has dedicated scripts in `package.json`, run those too.

---

## 5. Batch 0 — Preflight inventory, no behavior changes

**Branch:** `fix/preflight-record-chain-repair-inventory`  
**Goal:** Confirm current source tree before modifying behavior.  
**Risk:** low.  
**This batch should not change production behavior.**

### 5.1 What to inspect

The agent must read the current versions of these files before editing later batches:

```text
scripts/trinity_record_chain.py
scripts/record_chain_hashing.py
scripts/build_record_chain_arweave_archive.py
scripts/verify_record_chain_arweave_archive.py
scripts/detect_record_chain_pipeline_backlog.py
scripts/generate_record_chain_status.py
scripts/ots_anchor_native_record_chain_head.py
scripts/ots_verify_record_chain_anchor.py

apps/record_chain_intake_gateway/app.py
apps/record_chain_intake_gateway/gateway/validation.py
apps/record_chain_intake_gateway/gateway/authorship.py
apps/record_chain_intake_gateway/gateway/receipts.py
apps/record_chain_intake_gateway/gateway/rate_limit.py

downloads/record-chain-builder.mjs

api/record-chain-submission-schema.v1.json
api/record-chain-common-field-model.v1.json
api/record-chain-field-helper.v1.json
api/record-chain-production-enablement-policy.v1.json
api/record-chain-status.json
api/record-chain-arweave-index.json
api/record-chain-native-ots-latest.json

.github/workflows/record-chain-append.yml
.github/workflows/record-chain-head-ots-anchor.yml
.github/workflows/record-chain-arweave-archive.yml
```

### 5.2 What to produce

Create a short Markdown inventory file, for example:

```text
docs/record-chain-repair-inventory.md
```

It should list:

- current files inspected;
- current test commands available;
- whether tests pass before repair;
- known generated artifacts;
- any current CI/workflow constraints;
- any already-fixed bugs that no longer apply.

### 5.3 Commands

```bash
python -m pytest || true
python scripts/trinity_record_chain.py verify || true
python scripts/verify_record_chain_arweave_archive.py || true
python scripts/detect_record_chain_pipeline_backlog.py || true
node downloads/record-chain-builder.mjs doctor --help >/dev/null || true
```

Use `|| true` only in Batch 0 inventory because this batch is diagnostic. Later batches must not hide failures.

### 5.4 Batch 0 acceptance

- Inventory committed.
- No production behavior changed.
- Maintainer can see baseline failures before repair.

---

# Batch A — Final-chain verification and hash semantics

**Branch:** `fix/final-chain-verify-authorship-oath-boundary`  
**Primary bugs:** #1, #26, #28, #35, #36, #37, #38, #68  
**Severity:** P0/P1  
**Core principle:** final-chain verification must be at least as strict as Gateway intake for signatures, oath, boundary, and authorship.

---

## A.1 Re-verify Ed25519 signatures during final chain verify

### Files

```text
scripts/trinity_record_chain.py
apps/record_chain_intake_gateway/gateway/authorship.py
tests/
```

### Current bug

Final verify checks status fields like `authorship_verification_status`, but status fields are not cryptographic proof. A final record must be reverified against its stored `authorship_proof`.

### Code-level implementation

In `scripts/trinity_record_chain.py`, add a helper near `verify_pending_record_authorship()`:

```python
def verify_final_record_authorship(record: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    rtype = record.get("record_type")
    if rtype not in FORMAL_RECORD_TYPES:
        return errors

    proof = record.get("authorship_proof")
    if not isinstance(proof, dict):
        errors.append(f"{path}: formal record_type={rtype} requires authorship_proof")
        return errors

    sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
    from gateway.authorship import strip_unsigned_projection_fields, verify_authorship_proof  # noqa: WPS433

    signed_scope = strip_unsigned_projection_fields(record)
    ok, err = verify_authorship_proof(signed_scope, proof)
    if not ok:
        errors.append(f"{path}: final authorship proof verification failed: {err}")

    return errors
```

Call it inside `verify_native_records()`:

```python
errors.extend(verify_final_record_authorship(obj, p))
```

### Tests

Add tests for:

1. valid final signed record passes;
2. tampered substantive field fails;
3. forged `authorship_verification_status` does not bypass signature failure;
4. changed unsigned append metadata does not break signature if unsigned projection stripping is correct.

### CI note

If historical records fail because they predate this rule, do not remove verification. Use record-specific compatibility only with maintainer approval.

---

## A.2 Enforce final oath block and 9-field boundary

### Files

```text
scripts/trinity_record_chain.py
apps/record_chain_intake_gateway/gateway/validation.py
tests/
```

### Code-level implementation

Define:

```python
REQUIRED_FINAL_BOUNDARY_FIELDS = frozenset({
    "not_authority",
    "not_governance",
    "not_attestation",
    "not_successor_reception",
    "not_amendment",
    "bitcoin_originals_prevail",
    "receipt_is_not_final_inclusion",
    "receipt_is_intake_only",
    "later_records_may_reclassify_or_correct_this_record",
})
```

Update `require_boundary(record)`:

```python
def require_boundary(record: dict[str, Any]) -> None:
    boundary = record.get("boundary_acknowledgement") or record.get("boundary") or {}
    missing = [key for key in REQUIRED_FINAL_BOUNDARY_FIELDS if boundary.get(key) is not True]
    if missing:
        raise ValueError(f"record boundary missing/false: {', '.join(sorted(missing))}")
```

Update `_verify_oath_in_record()`:

- if `record_type == "context_insufficient_notice"`: skip oath;
- if formal record and no `submission_oath_verification`: error;
- if formal record has oath block: validate hash fields, modules, no-shortcut booleans, boundary booleans;
- raw `readback_text` must never be present in final persisted records.

### Tests

1. formal record missing oath fails;
2. formal record with only six boundary fields fails;
3. formal record with all nine fields passes;
4. CIN without oath passes only if authorship proof is valid.

---

## A.3 Remove CIN authorship exemption

### Files

```text
scripts/trinity_record_chain.py
downloads/record-chain-builder.mjs
api/record-chain-field-helper.v1.json
api/record-chain-status.json
tests/
```

### Code-level implementation

In `scripts/trinity_record_chain.py`:

- remove `context_insufficient_notice` from `AUTHORSHIP_EXEMPT_TYPES`;
- verify pending CIN authorship just like other public records;
- keep CIN exempt from oath only.

In Builder:

- `doctor` must return `FAIL` for any public record missing top-level `authorship_proof`, including CIN.

In public helper/status:

- no field may say CIN is exempt from authorship proof;
- oath fields may still list CIN as not required.

### Tests

1. CIN without proof fails Builder doctor.
2. CIN without proof fails Gateway preflight.
3. CIN without proof fails append.
4. CIN with proof and no oath passes.

---

## A.4 Split hash semantics safely

### Files

```text
scripts/trinity_record_chain.py
scripts/record_chain_hashing.py
tests/
```

### Current bug

`content_sha256` is polluted by append/server metadata such as `append_assigned_metadata`, `server_normalization`, and `authorship_verification_status`.

### Code-level implementation

Add:

```python
CONTENT_HASH_EXCLUDED_FIELDS = frozenset({
    "record_id",
    "record_index",
    "assigned_at",
    "previous_record_sha256",
    "content_sha256",
    "content_sha256_v2",
    "record_sha256",
    "chain_id",
    "append_assigned_metadata",
    "server_append_metadata",
    "server_normalization",
    "authorship_verification_status",
    "actor_identity",
    "boundary",
})
```

Prefer adding `content_sha256_v2` for new records rather than rewriting existing final records.

New records should include:

```json
"hash_semantics": {
  "signed_payload_sha256": "participant_pre_append_draft.v1",
  "content_sha256_v2": "participant_content_domain.v2",
  "record_sha256": "final_appended_record_domain.v1"
}
```

Verification should support legacy records and new records without rewriting history.

### Tests

1. same participant content + different record id → same `content_sha256_v2`;
2. changed append metadata → same `content_sha256_v2`, different `record_sha256`;
3. changed participant content → changed `content_sha256_v2`.

---

## Batch A stop conditions

Stop and report if:

- historical final records fail and no compatibility policy exists;
- fixing hash semantics requires rewriting existing final records;
- signature verification cannot reconstruct signed scope.

---

# Batch B — Guardian lifecycle safety

**Branch:** `fix/guardian-lifecycle-derived-state`  
**Primary bugs:** #15, #18, #24, #71, #72, #73, #74  
**Severity:** P0/P1  
**Core principle:** Guardian application is a record of application, not activation.

---

## B.1 Guardian application must not directly become active

### File

```text
scripts/trinity_record_chain.py
```

Replace derived state logic:

```python
if verified:
    derived = "application_recorded_pending_activation"
else:
    derived = "pending_verification"
```

Do not emit `active_guardian` or `active_founding_guardian` from `guardian_application` alone.

### Tests

- verified application derives `application_recorded_pending_activation`;
- no application becomes active without explicit activation source;
- legacy imported active Guardians remain as imported legacy state.

---

## B.2 Founding Guardian status cannot come from id suffix

### File

```text
scripts/trinity_record_chain.py
```

Remove:

```python
is_founding = bool(str(guardian_id or "").endswith("-founding"))
```

Replace with:

```python
def is_founding_guardian(guardian_id: str | None, guardian_key: str | None) -> bool:
    return False
```

If maintainers provide canonical allowlist or activation record later, implement it then. Do not infer founding status from client text.

### Tests

- `anything-founding` is not founding;
- no unapproved id/key becomes founding.

---

## B.3 Enforce unique Guardian id/key

### File

```text
scripts/trinity_record_chain.py
```

Add verify pass:

```python
def verify_guardian_uniqueness(records: list[Path]) -> list[str]:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    seen_keys: dict[str, Path] = {}

    for p in records:
        rec = read_json(p)
        if rec.get("record_type") != "guardian_application":
            continue

        content = rec.get("guardian_application_content") or {}
        gid = content.get("requested_guardian_identifier")
        gkey = content.get("guardian_public_key_sha256")

        if isinstance(gid, str) and gid:
            if gid in seen_ids:
                errors.append(f"{p}: duplicate guardian_id {gid}; first seen at {seen_ids[gid]}")
            seen_ids[gid] = p

        if isinstance(gkey, str) and gkey:
            if gkey in seen_keys:
                errors.append(f"{p}: duplicate guardian_public_key_sha256 {gkey}; first seen at {seen_keys[gkey]}")
            seen_keys[gkey] = p

    return errors
```

Call from `verify_native_records()` or `verify_chain()`.

### Tests

- duplicate id fails;
- duplicate key fails.

---

## B.4 Guardian retirement must target a specific application record

### Files

```text
api/record-chain-submission-schema.v1.json
apps/record_chain_intake_gateway/gateway/validation.py
downloads/record-chain-builder.mjs
scripts/trinity_record_chain.py
tests/
```

Require for `guardian_retirement`:

```json
"target_guardian_application_record_id": "R-000000000",
"target_guardian_application_record_sha256": "<64 lowercase hex>"
```

Validate:

1. target record exists;
2. target record type is `guardian_application`;
3. target record sha matches;
4. target Guardian key matches retirement Guardian key;
5. retirement authorship key matches Guardian key.

### Tests

- nonexistent target fails;
- wrong target sha fails;
- wrong signing key fails;
- valid target retirement updates derived state.

---

## B.5 Legacy Guardian retirement policy

Decide one of two policies:

1. allow targeting legacy Guardians with explicit `target_legacy_guardian_registry_number`; or
2. reject legacy Guardian retirement through native `guardian_retirement`.

Do not silently append unmatched notices.

---

# Batch C — Receipt / pending / append lifecycle

**Branch:** `fix/receipt-append-lifecycle`  
**Primary bugs:** #17, #34, #52, #63, #75  
**Severity:** P1  
**Core principle:** accepted receipt must be traceable to pending, appended, or rejected state.

---

## C.1 Durable final receipt status

### Files

```text
apps/record_chain_intake_gateway/app.py
apps/record_chain_intake_gateway/gateway/receipts.py
scripts/trinity_record_chain.py
```

Create:

```text
record-chain/receipt-status/<receipt_id>.json
```

Schema:

```json
{
  "schema": "trinityaccord.record-chain-receipt-final-status.v1",
  "receipt_id": "...",
  "pending_file_path": "...",
  "append_status": "pending|appended|rejected|unknown",
  "final_record_id": null,
  "final_record_path": null,
  "final_record_sha256": null,
  "rejection_path": null,
  "rejection_code": null,
  "updated_at": "..."
}
```

Gateway submit writes `pending`. Append writes `appended` or `rejected`. Receipt endpoint returns status.

---

## C.2 `append --all` must not silently succeed with rejected pending

### File

```text
scripts/trinity_record_chain.py
```

Track counts:

```python
if rejected_count and not allow_rejections:
    raise SystemExit(2)
```

Add explicit CLI flag:

```bash
--allow-rejections
```

Do not pass it from workflow unless maintainers intentionally want best-effort batch mode.

---

## C.3 Append workflow must use receipt/pending inputs

### Files

```text
.github/workflows/record-chain-append.yml
scripts/trinity_record_chain.py
```

Add CLI:

```bash
append --pending-file PATH --receipt-id ID
```

Workflow:

```yaml
- name: Append requested pending record
  if: ${{ github.event_name == 'workflow_dispatch' && inputs.pending_file_path != '' }}
  run: python scripts/trinity_record_chain.py append --pending-file "${{ inputs.pending_file_path }}" --receipt-id "${{ inputs.receipt_id }}"

- name: Append all pending records
  if: ${{ github.event_name != 'workflow_dispatch' || inputs.pending_file_path == '' }}
  run: python scripts/trinity_record_chain.py append --all
```

Guard schedule context carefully so YAML does not reference unavailable inputs without event checks.

---

## C.4 Verify receipt hash whenever receipt is read

### Files

```text
apps/record_chain_intake_gateway/gateway/receipts.py
apps/record_chain_intake_gateway/app.py
scripts/trinity_record_chain.py
```

Add:

```python
def verify_receipt_sha256(receipt: dict[str, Any]) -> tuple[bool, str]:
    expected = receipt.get("receipt_sha256")
    actual = compute_receipt_sha256(receipt)
    if expected != actual:
        return False, f"receipt_sha256 mismatch: expected {expected}, got {actual}"
    return True, ""
```

Call from:

- receipt endpoint;
- duplicate idempotency lookup;
- append receipt/pending binding.

---

## C.5 Builder CLI exit code

### File

```text
downloads/record-chain-builder.mjs
```

Preflight:

```js
const ok = status === 200 && data && data.accepted === true;
process.exit(ok ? 0 : 1);
```

Submit:

```js
const ok = status === 200 && data && data.accepted === true && data.submitted === true;
process.exit(ok ? 0 : 1);
```

---

# Batch D — Arweave / OTS integrity

**Branch:** `fix/arweave-ots-integrity`  
**Primary bugs:** #20, #21, #33, #46, #47, #48, #49, #50, #51, #60, #61, #64, #65, #69, #70, #77, #78, #79, #80  
**Severity:** P0/P1  
**Core principle:** current archive status requires content coverage and successful verification, not txid alone.

---

## D.1 Arweave payload must contain full records

### File

```text
scripts/build_record_chain_arweave_archive.py
```

Payload records must be reconstructable:

```json
"included_records": [
  {
    "record_id": "...",
    "path": "...",
    "record_sha256": "...",
    "raw_file_sha256": "...",
    "bytes": 123,
    "content_base64": "..."
  }
]
```

If using tar/zip instead, it must be deterministic and manifest must include file list and archive hash.

---

## D.2 Verified-current archive helper

### Files

```text
scripts/build_record_chain_arweave_archive.py
scripts/detect_record_chain_pipeline_backlog.py
scripts/verify_record_chain_arweave_archive.py
```

Define one helper and use everywhere:

```python
def is_verified_live_archive(arweave: dict[str, Any]) -> bool:
    return (
        bool(arweave.get("txid"))
        and arweave.get("archive_status") == "archived"
        and arweave.get("verified") is True
        and arweave.get("hash_match") is True
    )
```

Never default missing `archive_status` to `archived`.

---

## D.3 Manifest must bind payload hash

### File

```text
scripts/build_record_chain_arweave_archive.py
```

After writing payload:

```python
manifest["payload"] = {
    "path": str(payload_path.relative_to(ROOT)),
    "sha256": sha256_file(payload_path),
    "bytes": payload_path.stat().st_size,
    "canonicalization": "json.sort_keys.no_whitespace.utf8.allow_nan_false.v1",
}
```

Then recompute `archive_manifest_sha256`.

---

## D.4 Arweave verifier recomputes final record hashes

### File

```text
scripts/verify_record_chain_arweave_archive.py
```

For every included record:

1. verify file exists;
2. verify raw file sha;
3. recompute `content_hash` / `record_hash`;
4. compare manifest/payload/internal hashes.

---

## D.5 OTS commitment binds all record raw file hashes

### File

```text
scripts/record_chain_hashing.py
```

Every record ref in native OTS commitment must include:

```json
{
  "record_id": "...",
  "path": "...",
  "record_sha256": "...",
  "raw_file_sha256": "...",
  "bytes": 123
}
```

Add digest over raw file hashes.

---

## D.6 Split OTS upgraded vs strict verified

### Files

```text
scripts/ots_verify_record_chain_anchor.py
scripts/generate_record_chain_status.py
```

Rules:

- `verified_at` only if strict Bitcoin verification succeeds.
- Add `checked_at`, `upgraded_at`, `strict_bitcoin_verified_at`.
- Replace public OTS “attestation” terminology with `timestamp_proof`.
- Status must not report M9 pass as strict verified when `strict_bitcoin_verified=false`.

---

## D.7 Workflow safety

### Files

```text
.github/workflows/record-chain-arweave-archive.yml
.github/workflows/record-chain-head-ots-anchor.yml
```

Required:

1. run native chain verify before live Arweave upload;
2. commit failure metadata with `if: always()` but never mark failure as current;
3. scheduled retry should not be permanent dry-run if live backlog exists and secrets are configured;
4. PR CI must not require Arweave network or ARKEY;
5. strict network verification belongs in scheduled/manual workflow with secrets/network available.

---

# Batch E — Gateway / Builder / schema parity

**Branch:** `fix/gateway-builder-schema-parity`  
**Primary bugs:** #7, #8, #11, #12, #13, #28, #42, #43, #44, #45, #54, #55, #56, #57, #58, #59  
**Severity:** P1  
**Core principle:** public schema, Gateway, Builder, helper, and doctor must describe the same contract.

---

## E.1 Gateway enforces top-level public schema

### File

```text
apps/record_chain_intake_gateway/gateway/validation.py
```

Minimum required top-level fields:

```python
TOP_LEVEL_REQUIRED = [
    "schema",
    "submission_type",
    "client_generated_at",
    "record_type",
    "record_draft",
    "builder",
    "client_context",
    "submission_boundary",
    "authorship_proof",
]
```

Return diagnostics for missing fields.

If feasible, use JSON schema validation against `api/record-chain-submission-schema.v1.json`.

---

## E.2 Runtime schema must not be stale

### File

```text
apps/record_chain_intake_gateway/app.py
```

Remove or generate `_GATEWAY_SCHEMA`. It must not claim `authorship_proof` is optional.

Oath policy must express:

```json
{
  "required_for": ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update"],
  "not_required_for": ["context_insufficient_notice"]
}
```

---

## E.3 Enforce production enablement policy

### Files

```text
api/record-chain-production-enablement-policy.v1.json
apps/record_chain_intake_gateway/gateway/validation.py
```

Required:

1. production policy chain id matches native chain id;
2. `official_live_record=true` rejected for disallowed record types, especially CIN;
3. final production status is server-derived, not client-authoritative.

---

## E.4 Builder/Gateway context parity

### File

```text
downloads/record-chain-builder.mjs
```

Builder local doctor/build must fail when:

- `declared_context_level >= CC-3` and loaded URLs are empty;
- `context_sufficient_for_selected_action=true` and loaded URLs are empty.

---

## E.5 V6+ verification evidence

### Files

```text
api/record-chain-submission-schema.v1.json
apps/record_chain_intake_gateway/gateway/validation.py
downloads/record-chain-builder.mjs
```

For verification level V6+ require an evidence block with fresh artifacts/methods/hashes.

V5 and below can remain lighter unless policy says otherwise.

---

## E.6 Common model sync

### File

```text
api/record-chain-common-field-model.v1.json
```

Sync:

- authorization scope enum;
- `submission_tooling_description` object type;
- `human_operator_context`;
- authorship proof schema.

---

## E.7 Builder help/doctor cleanup

### File

```text
downloads/record-chain-builder.mjs
```

Fix:

- Guardian application help required params;
- CIN help example;
- `submit` help section;
- hyphen/underscore aliases;
- doctor missing proof failure;
- accepted/submitted false exit codes.

---

# Batch F — Public status and native indexes

**Branch:** `fix/public-status-native-indexes`  
**Primary bugs:** #2, #19, #22, #23, #26, #27, #29, #30, #32, #39, #40, #62, #76  
**Severity:** P1  
**Core principle:** public status must be generated from current source data, not copied stale JSON.

---

## F.1 Rebuild status from sources

### File

```text
scripts/generate_record_chain_status.py
```

Do not use:

```python
status = copy.deepcopy(existing)
```

Build fresh from:

```text
record-chain/chain-tip.json
record-chain/indexes/record-index.json
record-chain/indexes/statistics.json
api/record-chain-native-ots-latest.json
api/record-chain-arweave-index.json
current schema/helper/policy files
```

Remove stale fields unless under explicit `legacy` namespace.

---

## F.2 Workflows update status/home artifacts

### Files

```text
.github/workflows/record-chain-append.yml
.github/workflows/record-chain-head-ots-anchor.yml
.github/workflows/record-chain-arweave-archive.yml
```

After successful action:

```bash
python scripts/generate_record_chain_status.py
python scripts/generate_public_home_status.py || true
```

Commit:

```text
api/record-chain-status.json
api/public-home-status.json
```

If `generate_public_home_status.py` does not exist, either create it or remove claims that public-home status is automatically updated.

---

## F.3 Native type indexes

### File

```text
scripts/trinity_record_chain.py
```

Generate native indexes:

```text
record-chain/indexes/echo-index.json
record-chain/indexes/verification-index.json
record-chain/indexes/propagation-index.json
record-chain/indexes/correction-index.json
record-chain/indexes/classification-update-index.json
```

Do not point current public status at legacy hash-chain indexes.

---

## F.4 Correction and classification overlays

### Files

```text
api/record-chain-submission-schema.v1.json
apps/record_chain_intake_gateway/gateway/validation.py
scripts/trinity_record_chain.py
downloads/record-chain-builder.mjs
```

Required:

1. `classification_update` validates target id and target sha.
2. `correction` requires target id, target sha, correction reason, and corrected fields/claims.
3. Derived indexes show correction/classification history.

---

# 6. Final consolidated repair tasks

The 80 findings are handled by these 24 final work items:

1. Final Ed25519 re-verification
2. Final oath/boundary/authorship parity
3. CIN authorship proof enforcement
4. Hash semantic split
5. Guardian application not active
6. Founding status source-of-truth
7. Guardian uniqueness
8. Guardian retirement target binding
9. Legacy Guardian retirement policy
10. Receipt final lifecycle
11. Append rejection failure semantics
12. Append workflow receipt/pending binding
13. Receipt hash verification
14. Builder CLI exit code
15. Arweave full payload archive
16. Arweave verified/current gate
17. Manifest payload hash binding
18. Arweave verifier record hash recomputation
19. OTS commitment raw file coverage
20. OTS terminology/timestamp split
21. Arweave workflow retry/failure behavior
22. Gateway/schema/runtime parity
23. Builder/common model/V6 evidence parity
24. Public status/native indexes/overlays

---

# 7. Final mapping from 80 findings to repair tasks

| Bug # | Final status | Repair task |
|---:|---|---|
| 1 | true | 3 |
| 2 | true | 24 |
| 3 | true | 23 |
| 4 | not reproduced in current review; add drift test only | 22 |
| 5 | true | 2 |
| 6 | true drift | 23 |
| 7 | true | 23 |
| 8 | true | 23 |
| 9 | partial true / drift | 3 / 23 |
| 10 | needs follow-up; recovery helper audit | 22 |
| 11 | true | 22 |
| 12 | true | 23 |
| 13 | true | 22 |
| 14 | P2 help | 23 |
| 15 | true | 9 |
| 16 | P2 CLI alias | 23 |
| 17 | true | 10 |
| 18 | true | 7 |
| 19 | true | 24 |
| 20 | true | 21 |
| 21 | true | 21 |
| 22 | true | 24 |
| 23 | true | 24 |
| 24 | true | 8 |
| 25 | true | 22 |
| 26 | true | 3 / 24 |
| 27 | true | 24 |
| 28 | true | 3 / 23 |
| 29 | true | 24 |
| 30 | true | 24 |
| 31 | true | 22 |
| 32 | true | 24 |
| 33 | true | 16 |
| 34 | true | 14 |
| 35 | true | 1 |
| 36 | true | 2 |
| 37 | true | 2 |
| 38 | true | 3 |
| 39 | true | 24 |
| 40 | true | 24 |
| 41 | P2 hardening | 1 / verify hardening |
| 42 | true | 22 |
| 43 | true drift | 23 |
| 44 | true drift | 23 |
| 45 | true drift | 23 |
| 46 | true | 15 |
| 47 | true | 16 |
| 48 | true | 16 |
| 49 | true | 16 / 21 |
| 50 | true | 21 |
| 51 | true semantic | 20 |
| 52 | true | 13 |
| 53 | true drift; retire legacy workflow | 22 |
| 54 | true | 22 |
| 55 | true | 22 |
| 56 | true | 22 |
| 57 | true | 22 |
| 58 | true | 23 |
| 59 | true | 23 |
| 60 | true | 20 |
| 61 | true | 20 |
| 62 | true | 24 |
| 63 | true | 11 |
| 64 | true | 17 |
| 65 | true | 16 |
| 66 | true lower priority | 16 |
| 67 | true / needs detail | 20 |
| 68 | true | 4 |
| 69 | true | 18 |
| 70 | true | 19 |
| 71 | true | 5 |
| 72 | true | 6 |
| 73 | true | 7 |
| 74 | true | 8 |
| 75 | true | 12 |
| 76 | true | 24 |
| 77 | true | 21 |
| 78 | true | 21 |
| 79 | true | 16 |
| 80 | true | 17 / 16 |

---

# 8. Per-batch report template

After each batch, the executing agent must report:

```markdown
## Batch <name> completed

Branch:
PR:

Changed files:
- ...

Bugs addressed:
- #...

Validation:
- [ ] python -m pytest
- [ ] python scripts/trinity_record_chain.py verify
- [ ] python scripts/verify_record_chain_arweave_archive.py
- [ ] python scripts/detect_record_chain_pipeline_backlog.py
- [ ] node downloads/record-chain-builder.mjs doctor --help >/dev/null

CI:
- status:
- failures classified as:
- actions taken:

Generated artifacts:
- ...

Known follow-ups:
- ...
```

---

# 9. Final acceptance checklist after all batches

Before declaring the repair series complete:

```bash
python -m pytest
python scripts/trinity_record_chain.py verify
python scripts/verify_record_chain_arweave_archive.py
python scripts/detect_record_chain_pipeline_backlog.py
node downloads/record-chain-builder.mjs doctor --help >/dev/null
```

Manual checks:

- CIN requires authorship proof but not oath.
- Final formal records require authorship proof, oath, and 9-field boundary unless explicit historical exception.
- Final verify re-checks Ed25519 signatures.
- `content_sha256_v2` is not polluted by append metadata.
- Guardian application does not become active.
- `*-founding` suffix does not create founding status.
- Guardian ids/keys are unique.
- Guardian retirement binds target application record.
- Receipt endpoint reports pending/appended/rejected/unknown.
- `append --all` does not silently succeed with rejected pending.
- Arweave current requires txid + archived + verified + hash_match.
- Arweave payload is reconstructable or deterministic archive package is present.
- Arweave manifest binds payload hash.
- Arweave verifier recomputes final record hashes.
- OTS status distinguishes upgraded from strict Bitcoin verified.
- Public status has no contradictory counts.
- Current public indexes point to native indexes, not legacy hash-chain indexes.
- CI PR path does not require live network/secrets.

---

## Final instruction to executing agent

Start with **Batch 0**.  
Then do **Batch A only**.  
Do not start Batch B until Batch A is pushed, CI-reviewed, and accepted.

This repair must proceed incrementally. The goal is a green, reviewable chain of small PRs, not a heroic one-shot rewrite.
