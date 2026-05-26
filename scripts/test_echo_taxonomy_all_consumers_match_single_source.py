#!/usr/bin/env python3
"""All Echo taxonomy consumers must match protocol_echo_types.py."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from protocol_echo_types import allowed_canonical_echo_types

allowed = allowed_canonical_echo_types()

# 1. Echo record schema
echo_record_schema = json.loads((ROOT / "api/echo-record-schema.v3.json").read_text(encoding="utf-8"))
record_enum = set(echo_record_schema["properties"]["echo_type"]["enum"])
if record_enum != allowed:
    print("FAIL: echo-record-schema.v3.json echo_type enum does not match canonical taxonomy")
    print("Missing:", sorted(allowed - record_enum))
    print("Extra:", sorted(record_enum - allowed))
    sys.exit(1)

# 2. Gateway payload schema
gateway_schema = json.loads((ROOT / "api/agent-issue-gateway-payload-schema.v1.json").read_text(encoding="utf-8"))
gateway_enum = set(gateway_schema["properties"]["echo_type"]["enum"])
if gateway_enum != (allowed | {None}):
    print("FAIL: Gateway payload echo_type enum does not match canonical taxonomy + null")
    print("Missing:", sorted(x for x in (allowed | {None}) - gateway_enum if x is not None))
    print("Extra:", sorted(x for x in gateway_enum - (allowed | {None}) if x is not None))
    sys.exit(1)

# 3. Public status generator
public_status_src = (ROOT / "scripts/generate_public_home_status.py").read_text(encoding="utf-8")
if "allowed_canonical_echo_types" not in public_status_src:
    print("FAIL: generate_public_home_status.py does not use allowed_canonical_echo_types")
    sys.exit(1)

# 4. Archive script
archive_src = (ROOT / "scripts/archive_echo_issue.py").read_text(encoding="utf-8")
if "echo_type_map_for_archive" not in archive_src:
    print("FAIL: archive_echo_issue.py does not use echo_type_map_for_archive")
    sys.exit(1)
if "ECHO_TYPE_MAP = {" in archive_src:
    print("FAIL: archive_echo_issue.py still hardcodes ECHO_TYPE_MAP")
    sys.exit(1)

# 5. Validator
validator_src = (ROOT / "scripts/validate_agent_submission.py").read_text(encoding="utf-8")
if "allowed_canonical_echo_types" not in validator_src:
    print("FAIL: validate_agent_submission.py does not use allowed_canonical_echo_types")
    sys.exit(1)
if "CANONICAL_ECHO_TYPES = {" in validator_src:
    print("FAIL: validate_agent_submission.py still hardcodes CANONICAL_ECHO_TYPES")
    sys.exit(1)

# 6. Overrides
overrides = json.loads((ROOT / "api/agent-declared-archive-overrides.json").read_text(encoding="utf-8")).get("overrides", {})
for issue_number, override in overrides.items():
    if override.get("semantic_archive_kind") == "agent_declared_echo_archive":
        echo_type = override.get("echo_type")
        if echo_type not in allowed:
            print(f"FAIL: override #{issue_number} uses non-canonical echo_type={echo_type!r}")
            sys.exit(1)


# 7. Gateway builder route map echo_types
route_map = json.loads((ROOT / "api" / "gateway-builder-route-map.v1.json").read_text(encoding="utf-8"))
for route_id, route in route_map.get("routes", {}).items():
    for echo_type in route.get("echo_types", []):
        if echo_type not in allowed:
            print(
                f"FAIL: gateway-builder-route-map.v1.json route {route_id!r} "
                f"uses non-canonical echo_type={echo_type!r}"
            )
            sys.exit(1)

print("PASS: all Echo taxonomy consumers match single source")
