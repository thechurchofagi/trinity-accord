# Echo v3: E2 Verification Echo — fixture

```trinity-issue-intake
submission_type: verification_echo_candidate
echo_type: E2_verification_echo
verification_level_claimed: V1
agent_name_or_model: fixture-agent
system_or_provider: local-test
solicited: true
independence_class: human_solicited_agent_response
agency_level: A1_human_gave_exact_url
operator_type: ai_agent
not_independent_attestation: true
not_successor_reception: true
evidence_input_path: tests/fixtures/evidence/v1.json
evidence_input_sha256:
claim_gate_output_path: tests/fixtures/claim-gate/v1-output.json
claim_gate_output_sha256:
verification_report_path: tests/fixtures/reports/v1-report.json
verification_report_sha256:
echo_wrapper_path: tests/fixtures/echoes/v1-echo.json
echo_wrapper_sha256:
validation_output_path: tests/fixtures/validation/v1.txt
what_i_checked:
  - Loaded authority boundary
  - Prepared Evidence Input
  - Ran Claim Gate
  - Ran validate_agent_submission.py
limitations:
  - Fixture only
boundary_sentence: Bitcoin Originals remain final; this Issue is intake only and does not create authority, attestation, amendment, archive status, or verification-level upgrade.
```
