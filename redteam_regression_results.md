# Trinity Accord Redteam Remediation Test Report

## 1. Overall Status: PASS_ALL

## 2. Commit: `9b4f97b3d9ed19a0ca815238a0dcf024a208685f`

## 3. Timestamp: 2026-05-09T14:00:30.181418+00:00

## 4. Section Results

- P0_triage_normalized_scan: PASS
- P0_claim_text_safety: PASS
- P0_inscription_semantic_boundary: PASS
- P0_bilingual_boundaries: PASS
- P1_unknown_field_guard: PASS
- P1_cross_field_consistency: PASS
- P1_jsonschema_fail_closed: PASS
- P1_legacy_records: PASS
- P2_provenance_required: PASS
- P2_content_abuse_boundaries: PASS
- P2_ai_facing_density: PASS
- P3_workflow_input_hardening: PASS
- P3_workflow_permissions: PASS
- P3_deprecated_worker_surface: PASS
- P3_status_json_deployment: PASS


## 7. Commands Run

```bash
python3 scripts/final_redteam_regression.py
```
