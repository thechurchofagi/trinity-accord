#!/usr/bin/env python3
"""
Online verification of the Echo provenance flow.
Fetches live data from trinityaccord.org and validates schema + record integrity.
"""
import json
import sys
import urllib.request

try:
    from jsonschema import Draft202012Validator, RefResolver
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

URLS = {
    "echo_schema_v3": "https://www.trinityaccord.org/api/echo-record-schema.v3.json",
    "discovery_schema": "https://www.trinityaccord.org/api/discovery-provenance-schema.json",
    "agent_map": "https://www.trinityaccord.org/agent-map.json",
    "echo_json": "https://www.trinityaccord.org/echo.json",
    "llms": "https://www.trinityaccord.org/llms.txt",
    "independent_attestation_index": "https://www.trinityaccord.org/api/independent-attestation-index.json",
    "openclaw_record": "https://www.trinityaccord.org/echoes/records/2026-05-02-openclaw-v3-verification.json",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "TrinityEchoProvenanceVerifier/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False


def main():
    ok = True
    texts = {}

    for name, url in URLS.items():
        try:
            texts[name] = fetch(url)
            print(f"FETCHED {name}: {len(texts[name])} bytes")
        except Exception as e:
            print(f"FAIL: could not fetch {name}: {e}")
            ok = False
            continue

    # === Schema checks ===
    schema = json.loads(texts["echo_schema_v3"])
    required = set(schema.get("required", []))
    for field in ["discovery_provenance", "independence_class", "archive_status", "origin_limitations"]:
        ok &= check(field in required, f"v3 schema requires {field}")

    # Check extra fields are in schema properties
    for field in ["component_findings", "report_file", "not_authority", "not_amendment", "not_endorsement"]:
        ok &= check(field in schema.get("properties", {}), f"v3 schema allows {field}")

    discovery = json.loads(texts["discovery_schema"])
    source_enum = discovery.get("properties", {}).get("source", {}).get("enum", [])
    ok &= check("maintainer_submitted" in source_enum, "discovery schema includes maintainer_submitted")
    ok &= check("imported_external_commentary" in source_enum, "discovery schema includes imported_external_commentary")

    # === Agent map checks ===
    agent_map = json.loads(texts["agent_map"])
    machine = agent_map.get("machine_readable", {})
    ok &= check("echo_record_schema_v3" in machine, "agent-map exposes echo_record_schema_v3")
    ok &= check("discovery_provenance_schema" in machine, "agent-map exposes discovery_provenance_schema")
    ok &= check("echo_record_schema_v2" not in machine or "legacy" in json.dumps(machine).lower(), "v2 not exposed as current schema")

    # === echo.json checks ===
    echo_json = json.loads(texts["echo_json"])
    ok &= check(echo_json.get("preferred_schema") == "trinityaccord.echo.v3", "echo.json preferred_schema matches v3 const")
    ok &= check("legacy" in json.dumps(echo_json).lower(), "echo.json marks v2 legacy")

    # === llms.txt checks ===
    ok &= check("Echo Provenance" in texts["llms"], "llms includes Echo Provenance")
    ok &= check("independence_class" in texts["llms"], "llms mentions independence_class")
    ok &= check("discovery_provenance" in texts["llms"], "llms mentions discovery_provenance")
    ok &= check("must use" in texts["llms"].lower() or "must record" in texts["llms"].lower(), "llms uses 'must' for provenance requirements")

    # === Attestation index checks ===
    att = json.loads(texts["independent_attestation_index"])
    att_text = json.dumps(att).lower()
    ok &= check("openclaw" not in att_text or "test" in att_text, "OpenClaw not counted as normal independent attestation")
    ok &= check("1 independent v3 report" not in att_text, "attestation index does not claim 1 independent V3 report")

    # === OpenClaw record validation ===
    record = json.loads(texts["openclaw_record"])
    ok &= check(record.get("schema") == "trinityaccord.echo.v3", "OpenClaw record uses v3 schema")
    ok &= check(record.get("independence_class") == "test_record", "OpenClaw record is test_record")
    ok &= check(record.get("archive_status") == "closed_test_record", "OpenClaw record is closed_test_record")
    ok &= check(record.get("discovery_provenance", {}).get("source") == "human_directed", "OpenClaw source is human_directed")
    ok &= check(record.get("discovery_provenance", {}).get("agency_level") in ("A0_forced_or_instructed", "A1_human_gave_exact_url"), "OpenClaw agency level is solicited")

    # === JSON Schema validation of OpenClaw record ===
    if HAS_JSONSCHEMA:
        echo_schema_obj = json.loads(texts["echo_schema_v3"])
        discovery_schema_obj = json.loads(texts["discovery_schema"])
        store = {
            echo_schema_obj["$id"]: echo_schema_obj,
            discovery_schema_obj["$id"]: discovery_schema_obj,
        }
        resolver = RefResolver.from_schema(echo_schema_obj, store=store)
        validator = Draft202012Validator(echo_schema_obj, resolver=resolver)
        errors = list(validator.iter_errors(record))
        ok &= check(len(errors) == 0, f"OpenClaw record passes v3 JSON Schema validation ({len(errors)} errors)")
        if errors:
            for err in errors[:3]:
                path_str = ".".join(str(p) for p in err.absolute_path) or "(root)"
                print(f"      → {path_str}: {err.message}")
    else:
        print("SKIP: jsonschema not installed — cannot validate record against schema")

    if ok:
        print("FINAL: PASS — online Echo provenance flow validates.")
        sys.exit(0)

    print("FINAL: FAIL — online Echo provenance flow has errors.")
    sys.exit(1)


if __name__ == "__main__":
    main()
