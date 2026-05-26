#!/usr/bin/env python3
"""Gateway Example Payload Shape Test.
Ensures docs use the raw example endpoint and the fixture is schema-valid.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = F = T = 0
def check(c, l):
    global P, F, T; T += 1
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l}")

def main():
    server = (ROOT / "examples/github-app-backend/server.js").read_text("utf-8")
    agent_submit = (ROOT / "agent-submit.md").read_text("utf-8")
    quickstart = (ROOT / "external-agent-quickstart.md").read_text("utf-8")

    print("\n--- Raw endpoint exists ---")
    check('"/gateway/examples/agent-declared-v4/raw"' in server or
          'app.get("/gateway/examples/agent-declared-v4/raw"' in server,
          "raw example endpoint in server.js")

    print("\n--- Docs use raw endpoint ---")
    for name, content in [("agent-submit.md", agent_submit), ("external-agent-quickstart.md", quickstart)]:
        check("/gateway/examples/agent-declared-v4/raw" in content, f"{name} uses /raw endpoint")
        check("gateway/examples/agent-declared-v4 | jq . > payload.json" not in content,
              f"{name} does not save wrapper as payload.json")

    print("\n--- Capabilities expose raw endpoint ---")
    check("agent_declared_v4_raw" in server, "capabilities has agent_declared_v4_raw")

    print("\n--- Fixture is schema-valid ---")
    fixture_path = ROOT / "tests" / "fixtures" / "gateway" / "valid_agent_declared_v4.json"
    check(fixture_path.exists(), "fixture file exists")
    if fixture_path.exists():
        payload = json.loads(fixture_path.read_text("utf-8"))
        check("schema" in payload, "fixture has 'schema' field")
        check("body" in payload, "fixture has 'body' field")
        check(payload.get("agent_identity", {}).get("self_reported") is True,
              "fixture has agent_identity.self_reported=true")
        check("gateway_payload" not in payload, "fixture has no gateway_payload wrapper")

        # No _comment fields (additionalProperties: false)
        fixture_str = json.dumps(payload)
        check("_comment" not in fixture_str, "fixture has no _comment fields")

        # Run validator
        r = subprocess.run(
            ["python3", str(ROOT / "scripts" / "validate_gateway_payload.py"), str(fixture_path)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        check(r.returncode == 0, "fixture passes validate_gateway_payload.py")
        if r.returncode != 0:
            print(f"    Validator output: {r.stdout[-200:]}")

    print("\n--- Raw endpoint returns valid payload ---")
    # Check that server.js loads the fixture for the raw endpoint
    check('loadFixture("valid_agent_declared_v4.json")' in server,
          "raw endpoint loads valid_agent_declared_v4.json fixture")

if __name__ == "__main__":
    main()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
