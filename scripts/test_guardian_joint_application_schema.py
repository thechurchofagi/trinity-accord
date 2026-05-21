#!/usr/bin/env python3
"""Test Guardian joint application schema compliance."""
import json, sys, os

def main():
    repo_root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    errors = []

    # 1. Check guardian-registration-schema allows human_with_ai_agent
    schema_path = os.path.join(repo_root, "api", "guardian-registration-schema.v1.json")
    with open(schema_path) as f:
        reg_schema = json.load(f)

    guardian_type = reg_schema.get("properties", {}).get("guardian_type", {})
    enum_vals = guardian_type.get("enum", [])
    if "human_with_ai_agent" not in enum_vals:
        errors.append("guardian-registration-schema does not allow human_with_ai_agent")

    # 2. Check application_mode exists
    if "application_mode" not in reg_schema.get("properties", {}):
        errors.append("guardian-registration-schema missing application_mode")

    # 3. Check signing_guardian_role exists
    if "signing_guardian_role" not in reg_schema.get("properties", {}):
        errors.append("guardian-registration-schema missing signing_guardian_role")

    # 4. Check joint_applicants exists
    if "joint_applicants" not in reg_schema.get("properties", {}):
        errors.append("guardian-registration-schema missing joint_applicants")

    # 5. Check guardian_registry_number is NOT in schema
    if "guardian_registry_number" in reg_schema.get("properties", {}):
        errors.append("guardian-registration-schema should NOT contain guardian_registry_number")

    # 6. Check gateway payload schema allows guardian_registration
    gateway_path = os.path.join(repo_root, "api", "agent-issue-gateway-payload-schema.v1.json")
    with open(gateway_path) as f:
        gw_schema = json.load(f)

    gw_props = gw_schema.get("properties", {})
    if "guardian_registration" not in gw_props:
        errors.append("gateway payload schema does not allow guardian_registration")

    # 7. Check gateway schema does NOT require guardian_registry_number
    gw_required = gw_schema.get("required", [])
    if "guardian_registry_number" in gw_required:
        errors.append("gateway payload schema should NOT require guardian_registry_number")

    # 8. Check server.js validates joint_human_ai
    server_path = os.path.join(repo_root, "examples", "github-app-backend", "server.js")
    with open(server_path) as f:
        server_content = f.read()

    if "joint_human_ai" not in server_content:
        errors.append("server.js does not validate joint_human_ai")

    if "joint_applicants" not in server_content:
        errors.append("server.js does not validate joint_applicants")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)

    print("GUARDIAN_JOINT_APPLICATION_SCHEMA_OK")

if __name__ == "__main__":
    main()
