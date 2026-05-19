#!/usr/bin/env python3
"""Test: V0-V5 builder outputs single route identity fields."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = 0
FAIL = 0


def check(condition, msg):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {msg}")
    else:
        FAIL += 1
        print(f"  ❌ {msg}")


# Test builder help text mentions single route
print("\n=== Builder help text ===")
result = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "build_agent_declared_archive_payload.py"), "--help"],
    capture_output=True, text=True
)
help_text = result.stdout + result.stderr
check("only valid path for V0" in help_text, "help says only valid path for V0-V5")
check("Do not run the strict evidence pipeline" in help_text, "help says do not run strict evidence pipeline")
check("PASS_WITH_DOWNGRADE" in help_text, "help mentions PASS_WITH_DOWNGRADE to avoid")

# Build a test payload
print("\n=== Builder output ===")
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
    out_path = tmp.name

result = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "build_agent_declared_archive_payload.py"),
     "--agent-name", "TestBot",
     "--provider", "TestProvider",
     "--declared-level", "V4",
     "--reception-initiation-class", "externally_seeded",
     "--reception-initiation-basis", "external_url_only",
     "--agent-independent-followup",
     "--first-entry-url", "https://www.trinityaccord.org/",
     "--first-entry-type", "homepage",
     "--out", out_path],
    capture_output=True, text=True, cwd=str(ROOT)
)

if result.returncode == 0:
    payload = json.loads(Path(out_path).read_text())

    check(payload.get("route_id") == "sub_v6_agent_declared_template_archive",
          "route_id == sub_v6_agent_declared_template_archive")
    check(payload.get("single_mandatory_route") is True,
          "single_mandatory_route == true")
    check(payload.get("declared_level_source") == "agent_oath_template_declaration",
          "declared_level_source == agent_oath_template_declaration")
    check(payload.get("evidence_chain_required") is False,
          "evidence_chain_required == false")
    check(payload.get("strict_evidence_required") is False,
          "strict_evidence_required == false")
    check(payload.get("strict_evidence_used_for_level") is False,
          "strict_evidence_used_for_level == false")
    check(payload.get("strict_evidence_path_forbidden") is True,
          "strict_evidence_path_forbidden == true")

    policy = payload.get("sub_v6_template_mode_policy")
    check(policy is not None, "sub_v6_template_mode_policy exists")
    if policy:
        check(policy.get("route_id") == "sub_v6_agent_declared_template_archive",
              "policy.route_id correct")
        check(policy.get("evidence_chain_required") is False,
              "policy.evidence_chain_required == false")
        check(policy.get("strict_evidence_downgrade_language_forbidden") is True,
              "policy.strict_evidence_downgrade_language_forbidden == true")
else:
    print(f"  ⚠️ Builder failed: {result.stderr[:500]}")
    FAIL += 1

# Clean up
Path(out_path).unlink(missing_ok=True)

print(f"\n{'='*50}")
print(f"Results: {PASS} passed, {FAIL} failed")
sys.exit(1 if FAIL else 0)
