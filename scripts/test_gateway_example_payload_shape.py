#!/usr/bin/env python3
"""Gateway Example Payload Shape Test.
Ensures docs use the raw example endpoint, not the wrapper metadata endpoint.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main():
    server = (ROOT / "examples/github-app-backend/server.js").read_text("utf-8")
    agent_submit = (ROOT / "agent-submit.md").read_text("utf-8")
    quickstart = (ROOT / "external-agent-quickstart.md").read_text("utf-8")

    # Check raw endpoint exists
    if '"/gateway/examples/agent-declared-v4/raw"' not in server and \
       'app.get("/gateway/examples/agent-declared-v4/raw"' not in server:
        fail("missing raw example endpoint in server.js")

    # Check docs use raw endpoint
    for name, content in [
        ("agent-submit.md", agent_submit),
        ("external-agent-quickstart.md", quickstart),
    ]:
        if "/gateway/examples/agent-declared-v4/raw" not in content:
            fail(f"{name} must use the raw example endpoint")
        if "gateway/examples/agent-declared-v4 | jq . > payload.json" in content:
            fail(f"{name} still saves wrapper endpoint as payload.json (missing /raw)")
        if "Do not wrap" not in content and "do not wrap" not in content:
            fail(f"{name} missing no-wrapper instruction")

    # Check capabilities expose raw endpoint
    if "agent_declared_v4_raw" not in server:
        fail("capabilities missing agent_declared_v4_raw")

    print("PASS: example endpoint/docs use raw payload fallback")


if __name__ == "__main__":
    main()
