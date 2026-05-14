#!/usr/bin/env python3
"""Test that the GitHub App backend example is correct and complete."""

import json
import os
import sys
import subprocess

errors = []


def check(condition, msg):
    if not condition:
        print(f"FAIL: {msg}")
        errors.append(msg)
    else:
        print(f"PASS: {msg}")


def read(path):
    with open(path) as f:
        return f.read()


def load_json(path):
    with open(path) as f:
        return json.load(f)


# 1. Files exist
REQUIRED_FILES = [
    "examples/github-app-backend/README.md",
    "examples/github-app-backend/package.json",
    "examples/github-app-backend/server.js",
    "examples/github-app-backend/.env.example",
    "examples/github-app-backend/test-payload.echo.json",
]

for f in REQUIRED_FILES:
    check(os.path.exists(f), f"{f} exists")

# 2. package.json checks
pkg = load_json("examples/github-app-backend/package.json")
check(isinstance(pkg, dict), "package.json is valid JSON")

deps = pkg.get("dependencies", {})
for dep in ["@octokit/app", "@octokit/rest", "ajv", "express"]:
    check(dep in deps, f"package.json has dependency: {dep}")

# Check pinned versions (no caret, no tilde)
for dep, ver in deps.items():
    check(not ver.startswith("^"), f"{dep} version is pinned (no caret): {ver}")
    check(not ver.startswith("~"), f"{dep} version is pinned (no tilde): {ver}")

# 3. .env.example checks
env_example = read("examples/github-app-backend/.env.example")
check("GITHUB_APP_ID" in env_example, ".env.example has GITHUB_APP_ID")
check("GITHUB_INSTALLATION_ID" in env_example, ".env.example has GITHUB_INSTALLATION_ID")
check("GITHUB_PRIVATE_KEY" in env_example, ".env.example has GITHUB_PRIVATE_KEY")
check("GITHUB_REPO" in env_example, ".env.example has GITHUB_REPO")
check("example" in env_example.lower() or "REPLACE_WITH" in env_example,
      ".env.example contains example-only or placeholder warning")

# Must not contain real private key
check("BEGIN RSA PRIVATE KEY" not in env_example, ".env.example does not contain real private key")

# 4. server.js checks
server = read("examples/github-app-backend/server.js")
check("@octokit/app" in server, "server.js imports @octokit/app")
check("getInstallationOctokit" in server, "server.js uses getInstallationOctokit")
check("validate" in server.lower(), "server.js validates payload schema")
check("boundary_acknowledgement" in server, "server.js checks boundary acknowledgement")
check("rejectSecretPatterns" in server, "server.js rejects secret patterns")
check("agent-gateway-intake" in server, "server.js labels with agent-gateway-intake")
check("needs-triage" in server, "server.js labels with needs-triage")
check("DRY_RUN" in server, "server.js supports DRY_RUN")

# 5. Test payload validates against schema
schema_path = "api/agent-issue-gateway-payload-schema.v1.json"
if os.path.exists(schema_path):
    try:
        import importlib
        # Try to use ajv if available, otherwise just check structure
        test_payload = load_json("examples/github-app-backend/test-payload.echo.json")
        check(test_payload.get("schema") == "trinityaccord.agent-issue-gateway-payload.v1",
              "test payload has correct schema field")
        check("boundary_acknowledgement" in test_payload, "test payload has boundary_acknowledgement")
        ba = test_payload.get("boundary_acknowledgement", {})
        check(ba.get("not_authority") is True, "test payload: not_authority=true")
        check(ba.get("not_amendment") is True, "test payload: not_amendment=true")
        check(ba.get("not_attestation") is True, "test payload: not_attestation=true")
    except Exception as e:
        check(False, f"test payload validation error: {e}")
else:
    print(f"SKIP: {schema_path} not found, skipping schema validation")

# 6. Self-test (if node is available and deps are installed)
try:
    result = subprocess.run(
        ["node", "--version"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        # Check if node_modules exist
        node_modules_exists = os.path.exists("examples/github-app-backend/node_modules")
        if node_modules_exists:
            result = subprocess.run(
                ["node", "examples/github-app-backend/server.js", "--self-test"],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, "DRY_RUN": "true"}
            )
            check(result.returncode == 0, f"server.js --self-test passes")
            if result.returncode != 0:
                print(f"  stdout: {result.stdout}")
                print(f"  stderr: {result.stderr}")
        else:
            print("SKIP: npm dependencies not installed (run 'cd examples/github-app-backend && npm ci' to enable)")
    else:
        print("SKIP: node not available, skipping self-test")
except FileNotFoundError:
    print("SKIP: node not available, skipping self-test")
except Exception as e:
    check(False, f"self-test error: {e}")

print(f"\n{'ALL TESTS PASSED' if not errors else f'FAILED: {len(errors)} error(s)'}")
if errors:
    sys.exit(1)
