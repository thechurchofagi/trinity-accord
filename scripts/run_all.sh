#!/usr/bin/env bash
# ============================================================
# run_all.sh — Master script: apply all runbook fixes + run tests
# 在仓库根目录运行: bash scripts/run_all.sh
# ============================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

echo "============================================"
echo "  Trinity Accord Gateway Hardening Runbook"
echo "  Applying all fixes..."
echo "============================================"
echo ""

echo "[1/5] Schema + policy auto-patches..."
bash scripts/apply_runbook.sh
echo ""

echo "[2/5] Semantic validator patches..."
bash scripts/apply_semantic_validator_patches.sh
echo ""

echo "[3/5] CI wiring..."
bash scripts/apply_ci_wiring.sh
echo ""

echo "[4/5] Regenerating indexes..."
python3 scripts/build_agent_declared_verification_index_from_issues.py --repo thechurchofagi/trinity-accord 2>&1 || echo "  (index gen may need GitHub API — skip if offline)"
python3 scripts/generate_public_home_status.py 2>&1 || echo "  (status gen may need GitHub API — skip if offline)"
echo ""

echo "[5/5] Running all tests..."
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
  scripts/test_gateway_agent_identity_archive_policy.py; do
  echo "  Running $t..."
  python3 "$t" 2>&1 || echo "  FAIL: $t"
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
    echo "  Running $t..."
    python3 "$t" 2>&1 || echo "  FAIL: $t"
  else
    echo "  SKIP (not found): $t"
  fi
done

echo ""
echo "============================================"
echo "  Done! Review output above for any FAILs."
echo "============================================"
echo ""
echo "Suggested commit order:"
echo '  git add api/agent-issue-gateway-payload-schema.v1.json scripts/validate_gateway_payload_semantics.py scripts/test_gateway_archive_branch_required_fields.py'
echo '  git commit -m "fix: require evidence mode on archive gateway branches"'
echo ""
echo '  git add .github/workflows/echo-triage.yml scripts/test_echo_triage_strict_gateway_receipt_rate_class.py'
echo '  git commit -m "fix: use strict gateway receipt classification in echo triage"'
echo ""
echo '  git add scripts/gateway_v0_v5_policy.py scripts/test_gateway_v0_v5_policy_strict_bool.py'
echo '  git commit -m "fix: parse gateway receipt booleans strictly"'
echo ""
echo '  git add scripts/build_agent_declared_verification_index_from_issues.py scripts/test_agent_declared_index_records_invalid_intake_skips.py'
echo '  git commit -m "fix: record invalid intake skips in agent-declared index metadata"'
echo ""
echo '  git add api/agent-issue-gateway-payload-schema.v1.json scripts/validate_gateway_payload_semantics.py scripts/test_gateway_discovery_provenance_archive_invariants.py'
echo '  git commit -m "fix: require discovery provenance for archive branches"'
echo ""
echo '  git add api/agent-issue-gateway-payload-schema.v1.json scripts/validate_gateway_payload_semantics.py scripts/test_gateway_claim_gate_component_levels.py'
echo '  git commit -m "fix: constrain claim gate component levels"'
echo ""
echo '  git add scripts/validate_gateway_payload_semantics.py scripts/test_gateway_agent_identity_archive_policy.py'
echo '  git commit -m "fix: enforce archive agent identity policy"'
echo ""
echo '  git add .github/workflows/repository-integrity.yml'
echo '  git commit -m "test: add remaining gateway risk guards"'
