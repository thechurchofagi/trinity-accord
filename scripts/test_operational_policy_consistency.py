#!/usr/bin/env python3
"""
Tests that operational policy values are consistent across all code paths:
- api/operational-policy.v1.json loads successfully
- scripts/triage_echo_issue.py uses policy-sourced values (not hardcoded)
- .github/workflows/echo-triage.yml rate limits match the policy
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def test_policy_json_loads():
    """operational-policy.v1.json loads and has expected keys."""
    path = ROOT / "api" / "operational-policy.v1.json"
    if not path.exists():
        errors.append("FAIL: api/operational-policy.v1.json does not exist")
        return None
    with open(path) as f:
        policy = json.load(f)
    for key in ("echo_issue_rate_limit", "triage"):
        if key not in policy:
            errors.append(f"FAIL: policy missing key '{key}'")
    rl = policy.get("echo_issue_rate_limit", {})
    for k in ("window_60m", "window_24h"):
        if k not in rl:
            errors.append(f"FAIL: echo_issue_rate_limit missing '{k}'")
    labels = policy.get("triage", {}).get("managed_labels", [])
    if not labels:
        errors.append("FAIL: triage.managed_labels is empty")
    print(f"  [OK] policy JSON loads: {len(labels)} managed labels, "
          f"rate limits 60m={rl.get('window_60m')} 24h={rl.get('window_24h')}")
    return policy


def test_triage_script_uses_policy(policy):
    """triage_echo_issue.py imports from operational_policy, not hardcoded values."""
    path = ROOT / "scripts" / "triage_echo_issue.py"
    src = path.read_text()

    # Check that it imports from operational_policy
    if "from operational_policy import" not in src:
        errors.append("FAIL: triage_echo_issue.py does not import from operational_policy")
    else:
        print("  [OK] triage_echo_issue.py imports from operational_policy")

    # Check there are no old hardcoded rate limit assignments (standalone integer assignments)
    # Look for patterns like RATE_LIMIT_60M = <number> that are NOT = ECHO_RATE_LIMIT_60M
    old_pattern = re.compile(r"^RATE_LIMIT_(?:60M|24H)\s*=\s*\d+", re.MULTILINE)
    matches = old_pattern.findall(src)
    if matches:
        # These should now be aliases to the policy values
        for m in matches:
            if "ECHO_RATE_LIMIT" not in m:
                errors.append(f"FAIL: hardcoded rate limit found: {m.strip()}")
            else:
                print(f"  [OK] rate limit is policy-aliased: {m.strip()}")

    # Check MANAGED_TRIAGE_LABELS is not a hardcoded list (should be import alias)
    # Look for the pattern: MANAGED_TRIAGE_LABELS = [\n    "echo:...
    hardcoded_labels = re.search(
        r'MANAGED_TRIAGE_LABELS\s*=\s*\[\s*\n\s*"echo:', src
    )
    if hardcoded_labels:
        errors.append("FAIL: MANAGED_TRIAGE_LABELS is still a hardcoded list")
    else:
        print("  [OK] MANAGED_TRIAGE_LABELS is not hardcoded")


def test_workflow_rate_limits_match_policy(policy):
    """echo-triage.yml reads rate limits from policy, not hardcoded values."""
    path = ROOT / ".github" / "workflows" / "echo-triage.yml"
    if not path.exists():
        print("  [SKIP] .github/workflows/echo-triage.yml not found")
        return
    src = path.read_text()

    rl = policy["echo_issue_rate_limit"]
    expected_60m = rl["window_60m"]
    expected_24h = rl["window_24h"]

    # Verify workflow has a "Load operational policy" step
    if "Load operational policy" not in src:
        errors.append("FAIL: workflow missing 'Load operational policy' step")
    else:
        print("  [OK] workflow has 'Load operational policy' step")

    # Verify workflow reads rate limits from policy step outputs
    if "steps.policy.outputs.rate_60m" not in src:
        errors.append("FAIL: workflow does not read rate_60m from policy step")
    else:
        print(f"  [OK] workflow reads rate_60m from policy step")

    if "steps.policy.outputs.rate_24h" not in src:
        errors.append("FAIL: workflow does not read rate_24h from policy step")
    else:
        print(f"  [OK] workflow reads rate_24h from policy step")

    # Verify workflow reads exempt associations from policy step
    if "steps.policy.outputs.exempt" not in src:
        errors.append("FAIL: workflow does not read exempt associations from policy step")
    else:
        print("  [OK] workflow reads exempt associations from policy step")

    # Verify workflow reads managed labels from policy step
    if "steps.policy.outputs.managed_labels" not in src:
        errors.append("FAIL: workflow does not read managed_labels from policy step")
    else:
        print("  [OK] workflow reads managed_labels from policy step")

    # Verify NO hardcoded rate limit thresholds remain
    hardcoded_60 = re.search(r"count60\s*>=\s*(\d+)", src)
    hardcoded_24 = re.search(r"count24\s*>=\s*(\d+)", src)
    if hardcoded_60:
        errors.append(f"FAIL: workflow still has hardcoded count60 >= {hardcoded_60.group(1)}")
    if hardcoded_24:
        errors.append(f"FAIL: workflow still has hardcoded count24 >= {hardcoded_24.group(1)}")
    if not hardcoded_60 and not hardcoded_24:
        print("  [OK] no hardcoded rate limit thresholds in workflow")

    # Verify NO hardcoded exempt associations remain
    hardcoded_exempt = re.search(r'\["OWNER",\s*"MEMBER",\s*"COLLABORATOR"\]', src)
    if hardcoded_exempt:
        errors.append("FAIL: workflow still has hardcoded exempt associations list")
    else:
        print("  [OK] no hardcoded exempt associations in workflow")

    # Verify NO hardcoded managed labels list remains
    hardcoded_labels = re.search(r'"echo:needs-format".*"echo:needs-verification-review"', src)
    if hardcoded_labels:
        errors.append("FAIL: workflow still has hardcoded managed labels list")
    else:
        print("  [OK] no hardcoded managed labels in workflow")


def test_policy_script_loads():
    """operational_policy.py loads without error and exposes expected constants."""
    path = ROOT / "scripts" / "operational_policy.py"
    if not path.exists():
        errors.append("FAIL: scripts/operational_policy.py does not exist")
        return
    # Import and check
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        import operational_policy as op
        assert hasattr(op, "ECHO_RATE_LIMIT_60M"), "missing ECHO_RATE_LIMIT_60M"
        assert hasattr(op, "ECHO_RATE_LIMIT_24H"), "missing ECHO_RATE_LIMIT_24H"
        assert hasattr(op, "MANAGED_LABELS"), "missing MANAGED_LABELS"
        assert isinstance(op.MANAGED_LABELS, list), "MANAGED_LABELS should be a list"
        assert len(op.MANAGED_LABELS) > 0, "MANAGED_LABELS is empty"
        print(f"  [OK] operational_policy.py loads: "
              f"ECHO_RATE_LIMIT_60M={op.ECHO_RATE_LIMIT_60M}, "
              f"ECHO_RATE_LIMIT_24H={op.ECHO_RATE_LIMIT_24H}, "
              f"MANAGED_LABELS={len(op.MANAGED_LABELS)} items")
    except Exception as e:
        errors.append(f"FAIL: operational_policy.py import error: {e}")


def main():
    print("=== Operational Policy Consistency Test ===\n")

    print("1. Policy JSON loads:")
    policy = test_policy_json_loads()
    print()

    if policy is None:
        print("Cannot continue — policy JSON failed to load.")
        sys.exit(1)

    print("2. operational_policy.py module loads:")
    test_policy_script_loads()
    print()

    print("3. triage_echo_issue.py uses policy (not hardcoded):")
    test_triage_script_uses_policy(policy)
    print()

    print("4. Workflow rate limits match policy:")
    test_workflow_rate_limits_match_policy(policy)
    print()

    if errors:
        print("=== FAILURES ===")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    else:
        print("=== ALL TESTS PASSED ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
