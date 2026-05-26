#!/usr/bin/env python3
"""Test builder consistency: provenance fields derived from reception_initiation_class.

Tests:
  - externally_requested → source=external_request, discovery_class=externally_requested
  - externally_seeded → source=external_seed, human_supplied_link=true
  - self_initiated → source=self_initiated, human_supplied_link=false
  - agent_referred → other_agent_recommended=true, discovery_class=agent_referred
  - system_scheduled → discovery_class=system_scheduled
  - --no-agent-independent-followup sets false explicitly
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_archive_payload.py"

# Import shared oath text
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_oath_helper import get_oath_readback
OATH_READBACK = get_oath_readback()

PASS = 0
FAIL = 0


def run(cmd, expect_fail=False):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if expect_fail:
        if r.returncode != 0:
            return True, r.stdout + r.stderr
        return False, r.stdout + r.stderr
    if r.returncode != 0:
        return False, r.stdout + r.stderr
    return True, r.stdout + r.stderr


def build_and_read(extra_args, label):
    """Build payload and return parsed JSON."""
    global PASS, FAIL
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name

    cmd = [
        sys.executable, str(BUILDER),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--readback", OATH_READBACK,
        "--out", out,
    ] + extra_args

    ok, msg = run(cmd)
    if not ok:
        FAIL += 1
        print(f"  FAIL: builder failed for {label}: {msg[:200]}")
        Path(out).unlink(missing_ok=True)
        return None

    payload = json.loads(Path(out).read_text())
    Path(out).unlink(missing_ok=True)
    return payload


def check(payload, path, expected, label):
    """Check a nested field value."""
    global PASS, FAIL
    obj = payload
    for key in path:
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            obj = None
            break
    if obj == expected:
        PASS += 1
        print(f"  PASS: {label} = {expected}")
    else:
        FAIL += 1
        print(f"  FAIL: {label}: expected {expected}, got {obj}")


def test_externally_requested():
    print("\n--- externally_requested ---")
    p = build_and_read([
        "--reception-initiation-class", "externally_requested",
        "--reception-initiation-basis", "explicit_verification_request",
    ], "externally_requested")
    if not p:
        return
    check(p, ["discovery_provenance", "source"], "external_request", "source")
    check(p, ["origin_classification", "discovery_class"], "externally_requested", "discovery_class")
    check(p, ["origin_classification", "derived_counting_bucket"], "externally_requested_agent_verification", "bucket")
    check(p, ["discovery_provenance", "human_supplied_link"], True, "human_supplied_link")


def test_externally_seeded():
    print("\n--- externally_seeded ---")
    p = build_and_read([
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--agent-independent-followup",
    ], "externally_seeded")
    if not p:
        return
    check(p, ["discovery_provenance", "source"], "external_seed", "source")
    check(p, ["origin_classification", "discovery_class"], "externally_seeded", "discovery_class")
    check(p, ["origin_classification", "derived_counting_bucket"], "externally_seeded_agent_verification", "bucket")
    check(p, ["discovery_provenance", "human_supplied_link"], True, "human_supplied_link")
    check(p, ["discovery_provenance", "other_agent_recommended"], False, "other_agent_recommended")
    check(p, ["agent_independent_followup"], True, "agent_independent_followup")


def test_self_initiated():
    print("\n--- self_initiated ---")
    p = build_and_read([
        "--reception-initiation-class", "self_initiated",
        "--reception-initiation-basis", "agent_discovered_publicly",
    ], "self_initiated")
    if not p:
        return
    check(p, ["discovery_provenance", "source"], "self_initiated", "source")
    check(p, ["origin_classification", "discovery_class"], "unsolicited_discovery", "discovery_class")
    check(p, ["origin_classification", "derived_counting_bucket"], "self_initiated_agent_verification", "bucket")
    check(p, ["discovery_provenance", "human_supplied_link"], False, "human_supplied_link")


def test_agent_referred():
    print("\n--- agent_referred ---")
    p = build_and_read([
        "--reception-initiation-class", "agent_referred",
        "--reception-initiation-basis", "other_agent_reference",
    ], "agent_referred")
    if not p:
        return
    check(p, ["discovery_provenance", "other_agent_recommended"], True, "other_agent_recommended")
    check(p, ["origin_classification", "discovery_class"], "agent_referred", "discovery_class")


def test_system_scheduled():
    print("\n--- system_scheduled ---")
    p = build_and_read([
        "--reception-initiation-class", "system_scheduled",
        "--reception-initiation-basis", "scheduled_monitor",
    ], "system_scheduled")
    if not p:
        return
    check(p, ["origin_classification", "discovery_class"], "system_scheduled", "discovery_class")


def test_no_followup_explicit():
    print("\n--- --no-agent-independent-followup ---")
    p = build_and_read([
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--no-agent-independent-followup",
    ], "no-followup")
    if not p:
        return
    check(p, ["agent_independent_followup"], False, "agent_independent_followup")


def test_followup_mutual_exclusion():
    print("\n--- --followup mutual exclusion ---")
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name
    ok, msg = run([
        sys.executable, str(BUILDER),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--level", "V4",
        "--readback", OATH_READBACK,
        "--reception-initiation-class", "externally_seeded",
        "--reception-initiation-basis", "external_url_only",
        "--agent-independent-followup",
        "--no-agent-independent-followup",
        "--out", out,
    ], expect_fail=True)
    Path(out).unlink(missing_ok=True)
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS: mutual exclusion correctly rejected")
    else:
        FAIL += 1
        print(f"  FAIL: mutual exclusion not enforced")


def main():
    global PASS, FAIL
    print("=== Builder Consistency Tests ===")

    test_externally_requested()
    test_externally_seeded()
    test_self_initiated()
    test_agent_referred()
    test_system_scheduled()
    test_no_followup_explicit()
    test_followup_mutual_exclusion()

    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
