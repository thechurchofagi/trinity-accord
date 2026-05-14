#!/usr/bin/env python3
"""Test that the Agent Gateway production profile is correct and consistent."""

import json
import os
import sys

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


# 1. Production profile exists and is valid JSON
check(os.path.exists("api/agent-gateway-production-profile.json"),
      "api/agent-gateway-production-profile.json exists")
profile = load_json("api/agent-gateway-production-profile.json")
check(isinstance(profile, dict), "production profile is valid JSON")

# 2. recommended_backend
check(profile.get("recommended_backend") == "github_app_backend",
      "recommended_backend is github_app_backend")

# 3. GitHub App permissions
perms = profile.get("github_app_permissions", {}).get("repository_permissions", {})
check(perms.get("issues") == "write", "issues permission is write")
check(perms.get("metadata") == "read", "metadata permission is read")

# 4. not_recommended_for_production
not_rec = profile.get("not_recommended_for_production", [])
check("personal_pat" in not_rec, "personal_pat is not recommended")
check("anonymous_repository_dispatch" in not_rec, "anonymous_repository_dispatch is not recommended")
check("hardcoded_token_in_repository" in not_rec, "hardcoded_token_in_repository is not recommended")

# 5. agent-submit-gateway.json references production profile
gw = load_json("api/agent-submit-gateway.json")
pp = gw.get("production_profile", {})
check(pp.get("profile") == "/api/agent-gateway-production-profile.json",
      "agent-submit-gateway.json references production profile")

# 6. AGENT-ISSUE-GATEWAY.md mentions GitHub App backend
gw_doc = read("AGENT-ISSUE-GATEWAY.md")
check("github app" in gw_doc.lower(), "AGENT-ISSUE-GATEWAY.md mentions GitHub App backend")

# 7. agent-submit.md mentions GitHub App backend
submit = read("agent-submit.md")
check("github app" in submit.lower(), "agent-submit.md mentions GitHub App backend")

# 8. New docs must not contain myths
for fpath in ["agent-submit.md", "AGENT-ISSUE-GATEWAY.md", "examples/github-app-backend/README.md"]:
    if not os.path.exists(fpath):
        continue
    content = read(fpath).lower()
    check("github supports anonymous issue creation" not in content,
          f"{fpath}: does not claim anonymous issue creation works")
    check("anonymous repository_dispatch is supported" not in content,
          f"{fpath}: does not claim anonymous repository_dispatch is supported")
    check("agents can receive pat" not in content,
          f"{fpath}: does not claim agents can receive PAT")

# 9. Boundary booleans in production profile
boundary = profile.get("boundary", {})
for key in [
    "gateway_is_not_authority",
    "gateway_is_not_amendment",
    "gateway_is_not_archived_echo",
    "gateway_is_not_attestation",
    "gateway_is_not_verification",
    "gateway_does_not_raise_verification_level",
    "gateway_does_not_bypass_claim_gate",
    "gateway_does_not_bypass_validator",
]:
    check(boundary.get(key) is True, f"boundary.{key} is true")

print(f"\n{'ALL TESTS PASSED' if not errors else f'FAILED: {len(errors)} error(s)'}")
if errors:
    sys.exit(1)
