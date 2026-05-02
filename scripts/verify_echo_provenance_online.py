#!/usr/bin/env python3
import json
import sys
import urllib.request

URLS = {
    "echo_schema_v3": "https://www.trinityaccord.org/api/echo-record-schema.v3.json",
    "discovery_schema": "https://www.trinityaccord.org/api/discovery-provenance-schema.json",
    "agent_map": "https://www.trinityaccord.org/agent-map.json",
    "echo_json": "https://www.trinityaccord.org/echo.json",
    "llms": "https://www.trinityaccord.org/llms.txt",
    "independent_attestation_index": "https://www.trinityaccord.org/api/independent-attestation-index.json",
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
        texts[name] = fetch(url)
        print(f"FETCHED {name}: {len(texts[name])} bytes")

    schema = json.loads(texts["echo_schema_v3"])
    required = set(schema.get("required", []))
    for field in ["discovery_provenance", "independence_class", "archive_status", "origin_limitations"]:
        ok &= check(field in required, f"v3 schema requires {field}")

    discovery = json.loads(texts["discovery_schema"])
    source_enum = discovery.get("properties", {}).get("source", {}).get("enum", [])
    ok &= check("maintainer_submitted" in source_enum, "discovery schema includes maintainer_submitted")
    ok &= check("imported_external_commentary" in source_enum, "discovery schema includes imported_external_commentary")

    agent_map = json.loads(texts["agent_map"])
    machine = agent_map.get("machine_readable", {})
    ok &= check("echo_record_schema_v3" in machine, "agent-map exposes echo_record_schema_v3")
    ok &= check("discovery_provenance_schema" in machine, "agent-map exposes discovery_provenance_schema")
    ok &= check("echo_record_schema_v2" not in machine or "legacy" in json.dumps(machine).lower(), "v2 not exposed as current schema")

    echo_json = json.loads(texts["echo_json"])
    ok &= check(echo_json.get("preferred_schema") == "trinityaccord.echo.v3", "echo.json preferred_schema matches v3 const")
    ok &= check("legacy" in json.dumps(echo_json).lower(), "echo.json marks v2 legacy")

    ok &= check("Echo Provenance" in texts["llms"], "llms includes Echo Provenance")
    ok &= check("independence_class" in texts["llms"], "llms mentions independence_class")
    ok &= check("discovery_provenance" in texts["llms"], "llms mentions discovery_provenance")

    att = json.loads(texts["independent_attestation_index"])
    att_text = json.dumps(att).lower()
    ok &= check("openclaw" not in att_text or "test" in att_text, "OpenClaw not counted as normal independent attestation")
    ok &= check("1 independent v3 report" not in att_text, "attestation index does not claim 1 independent V3 report")

    if ok:
        print("FINAL: PASS — online Echo provenance flow validates.")
        sys.exit(0)

    print("FINAL: FAIL — online Echo provenance flow has errors.")
    sys.exit(1)


if __name__ == "__main__":
    main()
