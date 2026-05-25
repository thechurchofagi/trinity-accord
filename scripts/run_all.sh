#!/usr/bin/env bash
# ============================================================
# run_all.sh — Master script: apply all runbook fixes + run tests
# FAIL-CLOSED: exits non-zero if any required step fails
# ============================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

failures=0

run_required() {
  local label="$1"
  shift
  echo "  Running ${label}..."
  if ! "$@"; then
    echo "  FAIL: ${label}"
    failures=$((failures + 1))
  fi
}

run_optional() {
  local label="$1"
  shift
  echo "  Running optional ${label}..."
  if ! "$@"; then
    echo "  WARN: optional step failed: ${label}"
  fi
}

echo "============================================"
echo "  Trinity Accord Gateway Hardening Runbook"
echo "============================================"
echo ""

echo "--- Schema validation ---"
python3 -m json.tool api/agent-issue-gateway-payload-schema.v1.json >/dev/null && echo "  JSON schema: OK"

echo ""
echo "--- New tests ---"
for t in \
  scripts/test_gateway_archive_branch_required_fields.py \
  scripts/test_echo_triage_strict_gateway_receipt_rate_class.py \
  scripts/test_gateway_v0_v5_policy_strict_bool.py \
  scripts/test_agent_declared_index_records_invalid_intake_skips.py \
  scripts/test_gateway_discovery_provenance_archive_invariants.py \
  scripts/test_gateway_claim_gate_component_levels.py \
  scripts/test_gateway_agent_identity_archive_policy.py \
  scripts/test_gateway_semantic_validator_no_dead_code.py \
  scripts/test_gateway_fixtures_use_current_v0_v5_shape.py \
  scripts/test_echo_triage_receipt_fields_only_from_intake_block.py; do
  if [ -f "$t" ]; then
    run_required "$t" python3 "$t"
  fi
done

echo ""
echo "--- Existing tests ---"
for t in \
  scripts/test_agent_issue_gateway_schema.py \
  scripts/test_gateway_payload_semantic_validator.py \
  scripts/test_gateway_claim_gate_semantic_invariants.py \
  scripts/test_gateway_authority_boundary_schema_invariants.py \
  scripts/test_gateway_checked_limitations_content_invariants.py \
  scripts/test_gateway_readback_hash_semantics.py \
  scripts/test_agent_declared_intake_block_parser_hardening.py \
  scripts/test_agent_declared_intake_bool_parser.py \
  scripts/test_guardian_listing_gateway_schema_invariants.py; do
  if [ -f "$t" ]; then
    run_required "$t" python3 "$t"
  fi
done

echo ""
echo "--- Index drift check ---"
if [ -f scripts/build_agent_declared_verification_index_from_issues.py ]; then
  run_required "agent-declared index --check" \
    python3 scripts/build_agent_declared_verification_index_from_issues.py --repo thechurchofagi/trinity-accord --check
fi

echo ""
if [[ "$failures" -ne 0 ]]; then
  echo "============================================"
  echo "  FAILED: ${failures} required step(s) failed"
  echo "============================================"
  exit 1
fi

echo "============================================"
echo "  PASS: all required steps completed"
echo "============================================"
