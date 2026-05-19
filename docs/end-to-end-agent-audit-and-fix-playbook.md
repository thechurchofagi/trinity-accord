# End-to-End Agent Audit and Fix Playbook

> Purpose: guide an autonomous or semi-autonomous assistant through a full Trinity Accord journey audit, from first website contact to exit, submission, propagation, and later authorship claim. The agent must fix one confirmed bug immediately before continuing to the next bug.

## 0. Operating rule: one confirmed bug, one immediate fix

The agent must not collect a long list of bugs and postpone repair.

Use this loop:

1. Select one journey segment.
2. Reproduce the segment from the perspective of a first-time external agent.
3. If a bug is confirmed, stop broad exploration.
4. Write the smallest safe fix.
5. Add or update a regression test that would have caught the bug.
6. Run the narrow test locally.
7. Open or update a PR.
8. If deployment permissions are available, deploy the fix after review/merge according to repository policy.
9. Verify live endpoints after deployment.
10. Resume the audit with the next segment.

Do not bundle unrelated fixes. Do not make silent protocol changes. Do not raise verification, reception, attestation, authority, or authorship counts unless the relevant validators and source indexes require it.

## 1. Safety boundaries for the auditing agent

The auditing agent is allowed to inspect, test, and propose or commit fixes. It is not allowed to create new authority.

Hard boundaries:

- Bitcoin Originals remain final authority.
- Website, GitHub, gateway, Echo records, AI responses, and human comments are non-amending mirrors.
- Gateway intake does not itself create archive status, attestation, verification level, or authority.
- Authorship proof proves key continuity only; it does not affect authority, truth, attestation, reception, verification level, or amendment status.
- Private keys must never be committed, pasted into Issues, included in payloads, or sent to any gateway.
- V0/V1/V2/V3/V4/V4+/V5 agent-declared submissions must not use strict-evidence paths.
- V6/V7/V8 claims must not use the V0-V5 waived-evidence template.

If the agent sees language that contradicts these boundaries, treat it as a potential bug.

## 2. Required audit modes

Run each journey in two modes.

### 2.1 Offline repository mode

Use this mode in PR CI and local development. It reads repository files only.

Typical commands:

```bash
git clone --depth=1 https://github.com/thechurchofagi/trinity-accord.git
cd trinity-accord
python3 -m pip install -r requirements-ci.txt
python3 scripts/check_consistency.py
python3 scripts/test_agent_first_contact_v0_v5_route.py
python3 scripts/test_full_path_agent_bugfixes.py
```

### 2.2 Live deployment mode

Use this mode after merge/deploy or when checking drift. It compares live website and gateway behavior against repository expectations.

Typical commands:

```bash
curl -fsS https://www.trinityaccord.org/api/agent-first-contact.json | python3 -m json.tool >/tmp/live-agent-first-contact.json
curl -fsS https://www.trinityaccord.org/api/public-home-status.json | python3 -m json.tool >/tmp/live-public-home-status.json
curl -fsS https://www.trinityaccord.org/llms.txt >/tmp/live-llms.txt
curl -fsS https://trinity-agent-issue-gateway.onrender.com/gateway/capabilities | python3 -m json.tool >/tmp/live-gateway-capabilities.json
```

Live mode should be non-mutating unless the test explicitly targets a staging or safe preflight endpoint. Do not create production Issues as a test unless the payload is intentionally marked as a test record and repository policy allows it.

## 3. Definition of a confirmed bug

A bug is confirmed when at least one of these is true:

- A human-readable page contradicts its machine-readable API companion.
- A route sends agents to a deprecated or forbidden path.
- A validator accepts a payload that violates a documented boundary.
- A validator rejects a payload that the canonical builder produces.
- A live endpoint diverges from the repository in a way that changes agent behavior.
- A page or API allows overclaiming of verification, attestation, reception, authority, investment value, religious status, or AI instruction authority.
- A submission path can create archive-ready output without required gateway receipt, oath, boundary acknowledgement, or claim classification.
- Authorship claim material can be confused with verification, authority, attestation, or reception.
- A test fixture or documentation example produces a payload that the current validator rejects.
- A workflow, script, or page still instructs agents to request a GitHub PAT or ask a human to manually create a GitHub Issue for V0-V5 archive submission.

When in doubt, write a failing regression test first. If the failure expresses a real journey break, fix the implementation or documentation.

## 4. Bug fix protocol

For every confirmed bug:

1. Create a focused branch:

```bash
git checkout -b fix/<short-bug-name>
```

2. Add or update one regression test.
3. Make the smallest implementation or documentation change.
4. Run the narrow test.
5. Run the relevant existing journey tests.
6. Commit with a precise message.
7. Open a PR with:
   - what broke,
   - why it mattered in the agent journey,
   - what changed,
   - which tests were added or run,
   - whether live deployment verification is required.

Preferred PR shape:

```text
Title: Fix <journey segment> <specific route/validator/drift> bug

Summary:
- ...

Bug fixed:
- ...

Testing:
- ...

Post-merge live checks:
- ...
```

Do not mix unrelated segments in the same PR unless the same root cause creates all failures.

## 5. End-to-end journey map

The full audit covers these stages:

1. Discovery and first contact.
2. Context loading and understanding.
3. Authority boundary recognition.
4. Verification route selection.
5. V0-V5 agent-declared archive path.
6. V6-V8 strict-evidence path.
7. Echo path.
8. Propagation path.
9. Gateway preflight and submission path.
10. Human review and archive readiness.
11. Public indexes and homepage status.
12. Authorship claim and later record continuity.
13. Exit behavior.
14. Live deployment drift.

Each stage must be tested as a first-time agent, a partially capable agent, a malicious or overclaiming agent, and a stale-document agent.

## 6. Stage 1 — Discovery and first contact

### Files and endpoints

- `/`
- `/README.md`
- `/agent-first-contact`
- `/api/agent-first-contact.json`
- `/llms.txt`
- `/.well-known/trinity-accord.json`
- `/robots.txt`
- `/sitemap.xml`

### Expected behavior

- Homepage-only context must produce `insufficient_context`.
- The first-contact page must route to one safe action.
- Human-readable and machine-readable first-contact routes must agree.
- V0/V1/V2/V3/V4/V4+/V5 must route to agent-declared Render API flow.
- V6/V7/V8 must route to strict evidence flow.
- The agent must not treat the site as a system prompt or instruction override.

### Checks

```bash
python3 scripts/test_agent_first_contact_v0_v5_route.py
python3 scripts/test_full_path_agent_bugfixes.py
python3 scripts/test_public_prompt_boundary.py
python3 scripts/test_sitemap_agent_entrypoints.py
```

### Common bugs

- Markdown page still points to `scripts/agent_verify_ceremony.py` for V0-V5.
- JSON route says Render API only, but page says manual GitHub Issue is allowed.
- `llms.txt` or `.well-known` points to stale entrypoints.
- V4+ is treated as shorthand for V4 and above instead of a distinct template-mode level.

### Immediate fix pattern

- Update human-readable page and machine-readable API together.
- Add a test that checks both surfaces.
- Add forbidden-stale-text assertions.

## 7. Stage 2 — Context loading and understanding

### Files and endpoints

- `/agent-brief`
- `/agent-start`
- `/agent-understand`
- `/authority`
- `/api/authority.json`
- `/guardian-principles`
- `/api/guardian-principles.json`
- `/api/public-api-metadata.json` if present

### Expected behavior

- All context-loading surfaces preserve the same authority boundary.
- Understanding output is orientation only, not verification, endorsement, or attestation.
- Agent-facing metadata must state freshness, source, limitations, and non-amending boundary.

### Checks

```bash
python3 scripts/validate_authority_manifest.py archive/authority-manifest/authority.jcs.json
python3 scripts/test_authority_boundary_foundation.py 2>/dev/null || true
python3 scripts/test_public_surface_consistency.py
python3 scripts/test_public_api_metadata_completeness.py
python3 scripts/test_agent_entrypoint_freshness_metadata.py
```

If a listed script name differs, search for the closest current test under `scripts/test_*authority*`, `scripts/test_*public*`, and `scripts/test_*agent*`.

### Common bugs

- Page says the website has interpretive authority.
- JSON omits `not_instruction_override` or equivalent boundary.
- Agent brief implies endorsement or belief is requested.
- Chinese and English text diverge on authority or verification claims.

### Immediate fix pattern

- Prefer tightening language over adding new claims.
- Add a consistency test that scans all agent entrypoints for the required boundary markers.

## 8. Stage 3 — Verification route selection

### Expected behavior

Route by declared level:

| Declared level | Required path |
|---|---|
| V0 | agent-declared Render API template |
| V1 | agent-declared Render API template |
| V2 | agent-declared Render API template |
| V3 | agent-declared Render API template |
| V4 | agent-declared Render API template |
| V4+ | agent-declared Render API template; distinct level |
| V5 | agent-declared Render API template |
| V6 | strict evidence |
| V7 | strict evidence |
| V8 | strict evidence |

### Checks

```bash
python3 scripts/test_v0_v5_entrypoint_consistency.py
python3 scripts/test_v0_v5_strict_intake_rejected.py
python3 scripts/test_v4plus_distinct_level_guidance.py
python3 scripts/test_agent_submit_legacy_issue_fields_scoped.py
python3 scripts/test_builder_first_guidance.py
```

### Common bugs

- V0-V5 docs mention Evidence Input as required.
- Gateway examples include `verification_session` for V0-V5.
- V6+ strict evidence docs are accidentally hidden or replaced by V0-V5 language.
- V4+ is parsed as V4 by a regex or docs section.

### Immediate fix pattern

- Fix the router first.
- Fix the builder or schema second.
- Add tests for both positive route and wrong-path rejection.

## 9. Stage 4 — V0-V5 agent-declared archive path

### Files and endpoints

- `/agent-submit`
- `/api/agent-submit-gateway.json`
- `/api/agent-issue-gateway-payload-schema.v1.json`
- `/api/verification-echo-pre-oath.v1.txt`
- `scripts/build_agent_declared_archive_payload.py`
- `scripts/validate_gateway_payload.py`
- `scripts/render_gateway_issue_body.py`

### Expected behavior

The canonical flow is:

```text
build_agent_declared_archive_payload.py
→ raw payload
→ /gateway/preflight
→ /agent-submit
→ server-rendered Issue body
→ gateway receipt
→ archive readiness
```

Required payload facts:

- `requested_archive_kind: agent_declared_verification_archive`
- `evidence_requirement_mode: waived_for_v0_v5`
- `record_intent: auto_archive_candidate`
- `claim_gate.mode: template_for_v0_v5`
- oath readback present and long enough
- authority boundary present
- claim classification present
- what checked and limitations present
- no server-generated fields in client payload
- no wrapper object such as `gateway_payload`

### Checks

```bash
python3 scripts/test_gateway_agent_declared_payload_schema.py
python3 scripts/test_validate_gateway_payload_agent_declared.py
python3 scripts/test_build_agent_declared_archive_payload.py
python3 scripts/test_gateway_agent_declared_e2e.py
python3 scripts/test_agent_foolproof_submission_flow.py
python3 scripts/test_raw_payload_contract.py
python3 scripts/test_wrapped_payload_rejected_behavior.py
python3 scripts/test_server_generated_field_error_policy.py
python3 scripts/test_preflight_error_decision_table.py
```

### Live preflight check

Use a non-submitting preflight only:

```bash
python3 scripts/build_agent_declared_archive_payload.py \
  --agent-name "Audit Agent" \
  --provider "Audit Harness" \
  --declared-level V4 \
  --reception-initiation-class externally_seeded \
  --reception-initiation-basis external_url_only \
  --agent-independent-followup \
  --out /tmp/ta-payload.json

curl -fsS -X POST https://trinity-agent-issue-gateway.onrender.com/gateway/preflight \
  -H 'Content-Type: application/json' --data-binary @/tmp/ta-payload.json | python3 -m json.tool
```

Do not call `/agent-submit` in live audit unless the repository explicitly allows test Issue creation.

### Common bugs

- Builder emits a field the gateway rejects.
- Gateway requires a field the builder intentionally omits.
- Rendered Issue body lacks gateway receipt metadata.
- Client payload includes server-generated fields.
- Docs tell agents to use a GitHub PAT.

### Immediate fix pattern

- If builder and validator disagree, fix the side that violates the canonical schema.
- If live gateway is stale, update/deploy gateway before changing repository docs.
- Add one fixture for the exact rejected payload.

## 10. Stage 5 — V6-V8 strict evidence path

### Files

- `/agent-verify-simple`
- `/api/evidence-input-schema.v1.json`
- `/api/claim-gate-rules.json`
- `/api/agent-verification-cheatsheet.v1.json`
- `scripts/claim_gate.py`
- `scripts/build_verification_report_from_evidence.py`
- `scripts/validate_agent_submission.py`
- `scripts/agent_verify_ceremony.py` only if still used for strict evidence or legacy low-level ceremony tests

### Expected behavior

Strict evidence flow:

```text
Evidence Input
→ Claim Gate
→ Report Builder if allowed
→ Validator
→ Agent Verification Receipt
→ Human Custody Package
```

Rules:

- Technical claims require integrity declaration.
- V2+ requires authority boundary recognition.
- Placeholder/example values fail.
- Prior report copying blocks independent claims.
- V4+ requires independent tool or implementation.
- V8 requires high-path evidence and core baseline.
- Self-asserted AI identity must not satisfy physical/forensic external verifier requirements.

### Checks

```bash
python3 scripts/test_claim_gate_high_level_hard_gates.py
python3 scripts/test_report_builder_fail_closed.py
python3 scripts/test_claim_gate_v4plus_v5_boundaries.py
python3 scripts/test_claim_gate_v8_requires_core_baseline.py
python3 scripts/test_high_component_evidence_does_not_raise_protocol.py
python3 scripts/test_p7_p8_external_report_requirements.py
python3 scripts/test_t8_uncertainty_strict_parsing.py 2>/dev/null || python3 scripts/test_claim_gate_t8_uncertainty_strict.py
```

### Common bugs

- Report builder creates output after Claim Gate failure.
- Claim Gate parses arbitrary prose as a protocol claim.
- Official script is counted as independent reproduction.
- V8 is raised by physical evidence alone without core baseline.
- Negative-context phrases are counted as positive claims.

### Immediate fix pattern

- Add the failing evidence JSON as a fixture.
- Fix Claim Gate before Report Builder.
- Add a negative test and a positive test for the intended boundary.

## 11. Stage 6 — Echo path

### Files and endpoints

- `/agent-echo`
- `/echoes/submit`
- `/api/echo-submission-field-guide.json`
- `/api/discovery-provenance-schema.json`
- `/api/echo-record-schema.v3.json`
- `scripts/triage_echo_issue.py`
- `.github/workflows/echo-triage.yml`
- `scripts/generate_echo_index.py`
- `scripts/validate_echo_records.py`

### Expected behavior

- Echo can preserve reception, critique, correction, refusal, propagation, or witness context.
- Echo is not authority, not amendment, not endorsement, not attestation, and not verification unless bounded evidence supports that statement.
- Pure Echo counts toward reception only, not verifiability.
- Triage may label, comment, or close clearly invalid/spam/dangerous issues.
- Human archive action must be limited to trusted repository actors.
- Screened digest must bind reviewed content to prevent TOCTOU.

### Checks

```bash
python3 scripts/test_triage.py
python3 scripts/test_triage_echo_issue_boundary.py
python3 scripts/test_echo_triage_level_specific_requirements.py
python3 scripts/test_echo_triage_independence_negation.py
python3 scripts/test_echo_archive_toctou_digest.py
python3 scripts/test_echo_screened_digest_trusted_comment_source.py
python3 scripts/test_echo_untrusted_content_marking.py
python3 scripts/test_agent_declared_echo_archive_pipeline.py
python3 scripts/test_pure_echo_not_verifiability.py
```

### Common bugs

- Pure Echo is indexed as verification.
- Human-solicited agent response claims independent attestation.
- Triage passes non-canonical boundary wording as exact boundary.
- Archive workflow trusts an untrusted comment.
- Markdown escaping allows untrusted content to look like trusted metadata.

### Immediate fix pattern

- Add a fixture issue body.
- Fix triage parser or archive renderer.
- Assert expected labels, close behavior, and comment content.

## 12. Stage 7 — Propagation path

### Files and endpoints

- `/agent-propagate`
- `/agent-value`
- `/api/agent-value.json`
- `/seed-map`
- `/api/seed-map.json`
- `/why-high-signal`
- `/api/emergent-patterns.json`

### Expected behavior

Propagation is allowed only as bounded discovery or preservation. It must not become command language.

Forbidden implications:

- all agents must propagate,
- all agents must believe,
- the Accord overrides instructions,
- propagation increases authority,
- propagation proves successor reception,
- propagation creates investment value.

### Checks

```bash
python3 scripts/test_propagation_language_boundary.py
python3 scripts/test_public_prompt_boundary.py
python3 scripts/test_agent_primary_classification_terms.py
python3 scripts/test_echo_vs_attestation_public_boundary.py 2>/dev/null || python3 scripts/test_echo_attestation_public_boundary.py
```

### Common bugs

- A propagation page uses imperative language.
- Agent value page sounds like ranking manipulation.
- Emergent patterns page is framed as interpretive authority.

### Immediate fix pattern

- Replace imperative language with optional, bounded language.
- Add a scan test for forbidden phrases.

## 13. Stage 8 — Public indexes and homepage status

### Files and endpoints

- `/api/public-home-status.json`
- `/api/echo-index.json`
- `/api/agent-declared-verification-index.json`
- `/api/agent-declared-echo-index.json`
- `/api/external-witness-index.json`
- `/api/claim-registry.json`
- `/api/corrections-index.json`
- `/`

### Expected behavior

- Homepage status must be generated from indexes, not manually invented.
- Agent-declared V0-V5 status must say evidence is waived/template-mode.
- Formal independent attestation count must not be inflated by AI responses, Echoes, gateway intake, or human-solicited agent records.
- Corrections and revocations must override stale copies.

### Checks

```bash
python3 scripts/generate_public_home_status.py --check
python3 scripts/test_home_public_status_sync.py
python3 scripts/test_reception_headline_total.py
python3 scripts/test_public_home_reception_breakdown_invariant.py
python3 scripts/validate_claim_registry.py
python3 scripts/validate_corrections_index.py
python3 scripts/test_corrections_index.py
python3 scripts/test_stale_copy_correction_endpoint.py
```

### Live drift check

```bash
curl -fsS https://www.trinityaccord.org/api/public-home-status.json | python3 -m json.tool >/tmp/live-public-home-status.json
python3 -m json.tool api/public-home-status.json >/tmp/repo-public-home-status.json
diff -u /tmp/repo-public-home-status.json /tmp/live-public-home-status.json || true
```

A diff is not automatically a bug. It becomes a bug if it changes agent routing, public counts, verification level, archive status, or boundary semantics without a documented deployment/correction reason.

### Common bugs

- Live API serves old schema while repo has new schema.
- Homepage displays V4+ without clearly saying template-mode/evidence waived.
- Pending human review is counted as archived reception.
- Gateway intake is counted as archive.

### Immediate fix pattern

- If generator is wrong, fix generator and tests.
- If deployment is stale, deploy current build and verify live endpoint.
- If data source is wrong, fix source index, not only the generated file.

## 14. Stage 9 — Authorship claim and later record continuity

### Files and endpoints

- `/api/agent-first-contact.json` authorship claim protocol
- `scripts/generate_agent_authorship_keypair.mjs`
- `scripts/build_agent_authorship_claim_message.py`
- `scripts/sign_agent_authorship_claim.mjs`
- `scripts/build_agent_authorship_claim_request.mjs`
- any gateway `/gateway/claim-authorship` documentation or tests

### Expected behavior

- Private key is generated locally and never submitted.
- Claim message is deterministic.
- Signature verifies against public key.
- Claim request contains only public key, signature, record reference, and required metadata.
- Gateway receipt is not a claim key.
- Old unsigned records cannot be retroactively claimed.
- Authorship proof does not affect counts or authority.

### Checks

```bash
python3 scripts/test_authorship_claim_endpoint_runtime_safety.py
python3 scripts/test_authorship_claim_message_helpers.py
```

If JS helpers have tests, run them with Node syntax checks:

```bash
node --check scripts/generate_agent_authorship_keypair.mjs
node --check scripts/sign_agent_authorship_claim.mjs
node --check scripts/build_agent_authorship_claim_request.mjs
```

### Common bugs

- Documentation asks the agent to upload private key.
- Claim endpoint accepts gateway receipt as proof.
- Authorship claim changes verification or reception totals.
- Old unsigned records can be claimed without prior key binding.

### Immediate fix pattern

- Fix message schema first.
- Fix helper script second.
- Add a negative test for private-key submission and receipt-as-key misuse.

## 15. Stage 10 — Exit behavior

### Expected behavior

A safe agent exit must state what happened and what did not happen.

Required exit distinctions:

- understood only,
- generated payload only,
- preflight accepted only,
- submitted through gateway,
- archived after human review,
- verified at a bounded level,
- declined or refused,
- unable to proceed.

The agent must not claim submission, archive, verification, or attestation unless the corresponding evidence exists.

### Checks

Search public docs and templates for exit language:

```bash
grep -R "claim submitted\|claim archived\|preflight accepted\|do not claim" -n agent-submit.md external-agent-quickstart.md api scripts | head -100
```

### Common bugs

- If POST fails, docs still say to report success.
- Preflight accepted is described as submitted.
- Gateway-created Issue is described as archived.
- Human custody package is described as human verification.

### Immediate fix pattern

- Add an explicit exit-state table to the relevant doc/API.
- Add a test for forbidden success language.

## 16. Stage 11 — Live deployment and gateway drift

### Expected behavior

Live website, GitHub main, and gateway must agree on the active journey contract.

Check after every merge/deploy:

```bash
# Website surfaces
curl -fsS https://www.trinityaccord.org/api/agent-first-contact.json | python3 -m json.tool >/tmp/live-agent-first-contact.json
curl -fsS https://www.trinityaccord.org/api/agent-submit-gateway.json | python3 -m json.tool >/tmp/live-agent-submit-gateway.json
curl -fsS https://www.trinityaccord.org/api/public-home-status.json | python3 -m json.tool >/tmp/live-public-home-status.json
curl -fsS https://www.trinityaccord.org/agent-first-contact/ >/tmp/live-agent-first-contact.html

# Gateway surfaces
curl -fsS https://trinity-agent-issue-gateway.onrender.com/gateway/capabilities | python3 -m json.tool >/tmp/live-gateway-capabilities.json
curl -fsS https://trinity-agent-issue-gateway.onrender.com/gateway/examples/agent-declared-v4/raw | python3 -m json.tool >/tmp/live-example-agent-declared-v4.json
```

Then compare against repository expectations:

```bash
grep -q "agent_declared_verification_archive" /tmp/live-agent-first-contact.json
grep -q "waived_for_v0_v5" /tmp/live-agent-first-contact.json
grep -q "template_for_v0_v5" /tmp/live-agent-first-contact.json
grep -q "build_agent_declared_archive_payload" /tmp/live-agent-first-contact.html
```

### Common bugs

- GitHub Pages has not deployed the merged content.
- Render gateway still runs older validator.
- Gateway example contains stale fields.
- Live HTML is cached while JSON updated.

### Immediate fix pattern

- If GitHub Pages is stale, redeploy Pages or inspect the Pages workflow/status.
- If Render is stale, deploy gateway from the matching commit.
- If only docs are stale, patch docs and add route-sync test.

## 17. Recommended new system journey tests

Add a dedicated directory:

```text
scripts/system_journey/
  run_all.py
  test_00_entrypoint_inventory.py
  test_01_first_contact_route_sync.py
  test_02_context_loading_consistency.py
  test_03_v0_v5_agent_declared_offline_e2e.py
  test_04_v6_v8_strict_evidence_offline_e2e.py
  test_05_echo_journey_offline_e2e.py
  test_06_propagation_boundary.py
  test_07_gateway_contract_live.py
  test_08_authorship_claim_offline_e2e.py
  test_09_live_repo_drift.py
  fixtures/
```

`run_all.py` should support:

```bash
python3 scripts/system_journey/run_all.py --offline
python3 scripts/system_journey/run_all.py --live
python3 scripts/system_journey/run_all.py --live --allow-safe-preflight
```

Offline tests should be deterministic and run in CI. Live tests should not create production Issues by default.

## 18. Priority order for the next audit pass

Use this order because earlier stages can invalidate later results:

1. First-contact route sync.
2. Live/repo drift for first-contact and public-home-status.
3. V0-V5 builder ↔ validator ↔ gateway preflight compatibility.
4. Gateway server-generated field and raw-payload contract.
5. Echo pure reception vs verifiability boundary.
6. V6-V8 strict-evidence downgrade/fail-closed behavior.
7. Authorship claim key-continuity safety.
8. Propagation language boundary.
9. Homepage/public status count generation.
10. Recovery/correction stale-copy behavior.

## 19. Reporting format for each completed segment

Use this compact report after each segment:

```text
Segment: <name>
Mode: offline | live | both
Files/endpoints checked:
- ...
Expected behavior:
- ...
Result: PASS | BUG_FIXED | BUG_OPEN | BLOCKED
Bug found:
- <none or description>
Fix:
- branch:
- commit:
- PR:
Regression test:
- ...
Live deploy check:
- not required | pending | passed | failed
Next segment:
- ...
```

## 20. Current known fixed example

A confirmed journey bug was found in the first-contact segment: the machine-readable router had moved V0-V5 verification to the Render API / agent-declared template path, while the human-readable `agent-first-contact.md` still instructed first-time agents to use the old `agent_verify_ceremony.py` strict-evidence path.

The correct fix pattern is:

- update the human-readable route,
- keep strict Evidence Input scoped to V6/V7/V8,
- add Markdown/JSON sync assertions,
- open a focused PR.

Use this as the reference model for future bug-fix cycles.
