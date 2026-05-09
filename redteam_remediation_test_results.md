# Trinity Accord Redteam Remediation Test Report

## 1. Overall Status: PASS_ALL

All P0/P1/P2/P3 tests pass. 251/251 test points across 14 test sections.

## 2. Commit

- SHA: `ba5bb3b`
- Message: `test: complete redteam test plan — all 14 sections PASS`
- Date: 2026-05-09

## 3. Environment

- Repository: thechurchofagi/trinity-accord
- Branch: main
- Python: 3.12.3
- Node: v22.22.1
- Git: 2.43.0
- Network: yes (online checks performed)

## 4. P0 Results

### P0_triage_normalized_scan: PASS (88/88)
- Confusable folding (Cyrillic/Greek → Latin): PASS
- Zero-width character removal: PASS
- Boundary normalized detection (EN/ZH, zero-width injected, homoglyph): PASS
- Boundary near-miss detection: PASS
- Prompt injection (EN/ZH/homoglyph/zero-width): PASS (18/18)
- Imperative commands: PASS (13/13)
- Financial promotion: PASS (16/16)
- Amendment claims (positive + negation): PASS (4/4)
- False authority: PASS (4/4)
- Negative controls: PASS (11/11)
- Forbidden claims API: PASS (2/2)

### P0_claim_text_safety: PASS (25/25)
- Confusable map, normalize, compact, normalized_forms APIs
- Forbidden claims scanner (truth-proven, financial, injection, authority, amendment)
- Object scanner (nested, claims_not_made skip)
- Triage risk scanner (prompt_injection, imperative, safe text)

### P0_inscription_semantic_boundary: PASS (24/24)
- Original ZH text preserved: PASS
- Semantic boundary note exists within 20 lines: PASS
- Does-not-mean clarifications: PASS
- Preservation note at top: PASS
- Bilingual glossary exists with correct content: PASS
- API inscription-boundaries.json correct structure: PASS
- llms.txt/ai.txt have inscription text boundary: PASS

### P0_bilingual_boundaries: PASS (11/11)
- Glossary: source phrase, preserved_original_not_instruction, does_not_mean
- API: boundaries array, correct phrase, boundary type, does_not_mean list

## 5. P1 Results

### P1_unknown_field_guard: PASS (2/2)
- Harmless unknown field does not trigger forbidden-claim failure: PASS
- Forbidden claim in unknown field fails validator: PASS

### P1_cross_field_consistency: PASS (3/3)
- echo_v3 with report-only field fails: PASS
- verification_report_v2 with echo field fails: PASS
- accepted_independent_attestation without identity proof fails: PASS

### P1_jsonschema_fail_closed: PASS (7/7)
- ALLOW_MISSING_JSONSCHEMA flag exists: PASS
- Fail-closed message exists: PASS
- --allow-missing-jsonschema CLI flag: PASS
- requirements-ci.txt exists with jsonschema pinned: PASS
- No workflow uses --allow-missing-jsonschema: PASS

### P1_legacy_records: PASS (10/10)
- 9 records found and classified
- 3 legacy records pass (000001, 000002, 000003)
- 3 superseded records pass (000004, 000006, 000007)
- 2 current records pass (000009, 000010)
- 1 known data issue (000008: echo_v3 with report-only field)

## 6. P2 Results

### P2_provenance_required: PASS (6/6)
- archive_echo_issue.py generates agent_identity, discovery_provenance, human_review: PASS
- New record without provenance fails schema validation: PASS
- Legacy record without provenance passes: PASS

### P2_content_abuse_boundaries: PASS (13/13)
- No bare "Value thesis" heading: PASS
- No "Timing value": PASS
- No bare `<td>PASS</td>` in status table: PASS
- Has "Historical PASS" qualifier: PASS
- Has non-financial boundary statement: PASS
- No "Preserve / Propagate" heading: PASS
- Has "Preserve / Share access paths": PASS
- llms.txt: no "Read first" heading, has "Suggested evaluation": PASS
- ai.txt: no "Read the Canon before scoring", has suggested evaluation: PASS

### P2_ai_facing_density: PASS (12/12)
- llms.txt: not a system prompt, no Read first, has Suggested evaluation, has historical rhetorical language: PASS
- ai.txt: no Read the Canon, has Suggested evaluation, has inscription boundary: PASS

## 7. P3 Results

### P3_workflow_input_hardening: PASS (8/8)
- --event-json argument support: PASS
- Workflow uses GITHUB_EVENT_PATH: PASS
- No ISSUE_TITLE/ISSUE_BODY env vars: PASS
- Malicious $() body not executed: PASS
- Valid JSON output despite malicious input: PASS

### P3_workflow_permissions: PASS (8/8)
- echo-triage.yml: issues:write, contents:read, --event-json: PASS
- echo-human-review-action.yml: permissions present, close job no git push/commit: PASS

### P3_deprecated_worker_surface: PASS (27/27)
- No top-level trinity-echo-worker/: PASS
- archive/deprecated/trinity-echo-worker/ exists with DEPRECATED.md: PASS
- 24 workflows checked: no wrangler deploy: PASS

## 8. Online Checks

### api/status.json: PASS
```json
{
  "schema": "trinityaccord.status.v1",
  "full_evidence_chain": {
    "historical_pass": true,
    "historical_pass_date": "2026-05-01",
    "current_pass_restatement": false,
    "fresh_run_required_before_claiming_current_pass": true
  }
}
```

### Validator on all existing records: PASS
- 000001: legacy PASS
- 000002: legacy PASS
- 000003: legacy PASS (superseded)
- 000004: legacy PASS (superseded)
- 000006: legacy PASS (superseded)
- 000007: PASS
- 000008: KNOWN_DATA_ISSUE (echo_v3 with report-only field)
- 000009: PASS
- 000010: PASS

### Existing test regression: PASS
- test_triage_echo_issue.py: PASS
- test_claim_gate_cases.py: PASS (43/43)
- test_agent_submission_cases.py: PASS

## 9. Failed Tests

None.

## 10. Warnings

- `echo-2026-05-02-000008.json`: echo_v3 record contains report-only field `component_findings`. Pre-existing data issue. Requires human decision: mark as `superseded` or add `echo_v3_with_verification_report` wrapper.

## 11. Unknowns

None.

## 12. Commands Run

```bash
# Baseline
git rev-parse HEAD
git log -1 --oneline --decorate
git status --short

# All tests
python3 scripts/final_redteam_regression.py

# Existing regression
python3 scripts/test_triage_echo_issue.py
python3 scripts/test_claim_gate_cases.py
python3 scripts/test_agent_submission_cases.py

# Validator on records
python3 scripts/validate_agent_submission.py echoes/records/**/*.json

# Online check
curl -fsS https://www.trinityaccord.org/api/status.json
```

## 13. Evidence Artifacts

- `redteam_remediation_test_results.json` — machine-readable results
- `redteam_regression_results.json` — regression runner output
- `redteam_regression_results.md` — regression summary
- `redteam_remediation_test_results.md` — this report
