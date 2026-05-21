#!/usr/bin/env python3
"""Test Guardian joint application schema compliance and Gateway syntax."""

import json
import os
import subprocess
import sys


def main():
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    errors = []

    # 1. Check guardian-registration-schema allows human_with_ai_agent
    schema_path = os.path.join(repo_root, "api", "guardian-registration-schema.v1.json")
    with open(schema_path, encoding="utf-8") as f:
        reg_schema = json.load(f)

    props = reg_schema.get("properties", {})

    guardian_type = props.get("guardian_type", {})
    enum_vals = guardian_type.get("enum", [])
    if "human_with_ai_agent" not in enum_vals:
        errors.append("guardian-registration-schema does not allow human_with_ai_agent")

    # 2. Check joint application fields
    if "application_mode" not in props:
        errors.append("guardian-registration-schema missing application_mode")

    if "signing_guardian_role" not in props:
        errors.append("guardian-registration-schema missing signing_guardian_role")

    if "joint_applicants" not in props:
        errors.append("guardian-registration-schema missing joint_applicants")

    # 3. Check guardian_registry_number is NOT in registration schema
    if "guardian_registry_number" in props:
        errors.append("guardian-registration-schema should NOT contain guardian_registry_number")

    # 4. Check allOf has human_with_ai_agent conditional rule
    schema_text = json.dumps(reg_schema, sort_keys=True)
    if "joint_human_ai" not in schema_text:
        errors.append("guardian-registration-schema missing joint_human_ai conditional")
    if "joint_applicants" not in schema_text:
        errors.append("guardian-registration-schema missing joint_applicants conditional")

    # 5. Check gateway payload schema allows guardian_registration
    gateway_path = os.path.join(repo_root, "api", "agent-issue-gateway-payload-schema.v1.json")
    with open(gateway_path, encoding="utf-8") as f:
        gw_schema = json.load(f)

    gw_props = gw_schema.get("properties", {})
    if "guardian_registration" not in gw_props:
        errors.append("gateway payload schema does not allow guardian_registration")

    # 6. Check gateway schema does NOT require guardian_registry_number
    gw_required = gw_schema.get("required", [])
    if "guardian_registry_number" in gw_required:
        errors.append("gateway payload schema should NOT require guardian_registry_number")

    # 7. Check server.js syntax with Node parser
    server_rel = os.path.join("examples", "github-app-backend", "server.js")
    result = subprocess.run(
        ["node", "--check", server_rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=20,
    )
    if result.returncode != 0:
        errors.append("server.js failed node --check: " + (result.stderr or result.stdout))

    # 8. Check server.js validates joint application semantics
    server_path = os.path.join(repo_root, server_rel)
    with open(server_path, encoding="utf-8") as f:
        server_content = f.read()

    required_snippets = [
        "allowedGuardianTypes",
        "human_with_ai_agent",
        "joint_human_ai",
        "joint_applicants must include at least human and ai_agent applicants",
        "joint_applicants must include a human applicant",
        "joint_applicants must include an ai_agent applicant",
        ".consent_declared must be true",
        ".self_reported must be boolean",
    ]

    for snippet in required_snippets:
        if snippet not in server_content:
            errors.append(f"server.js missing expected Guardian joint validation snippet: {snippet}")

    # 9. Guard against previous broken insertion pattern
    forbidden_snippets = [
        "const requiredBoundaries = [\nconst allowedGuardianTypes",
        "errors.push();",
    ]

    for snippet in forbidden_snippets:
        if snippet in server_content:
            errors.append(f"server.js contains forbidden broken validation snippet: {snippet}")

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)

    print("GUARDIAN_JOINT_APPLICATION_SCHEMA_OK")


if __name__ == "__main__":
    main()
