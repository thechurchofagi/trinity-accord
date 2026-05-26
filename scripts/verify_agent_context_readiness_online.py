#!/usr/bin/env python3
"""
Online verification for agent context readiness.
Checks that context readiness endpoints are reachable and contain expected content.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import urllib.request
    import urllib.error
    import ssl
except ImportError:
    print("SKIP: urllib not available")
    sys.exit(0)

BASE_URL = "https://www.trinityaccord.org"
errors = []

def check(label, condition, detail=""):
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        errors.append(msg)
        print(msg)
    else:
        print(f"OK:   {label}")

def fetch(path, timeout=30):
    url = BASE_URL + path
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": "trinity-accord-online-verifier/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8"), resp.status
    except Exception as e:
        return None, str(e)

# --- Check reachable endpoints ---
endpoints = [
    "/agent-understand",
    "/agent-resonance",
    "/echo-authorship-proof",
    "/api/agent-context-readiness-protocol.json",
    "/api/context-load-map.json",
    "/api/context-packs/core-ontology.json",
    "/api/context-packs/vision-layer.json",
    "/api/context-packs/physical-anchor-context.json",
    "/api/context-packs/legacy-archive-index.json",
    "/api/context-readiness-levels.json",
    "/api/resonance-willingness-scale.json",
    "/api/echo-authorship-proof-schema.v1.json",
]

for ep in endpoints:
    body, status = fetch(ep)
    check(f"Reachable: {ep}", body is not None and status == 200, f"status={status}")

# --- Check agent-start contains CONTEXT-READY ---
print("\n=== agent-start ===")
body, _ = fetch("/agent-start")
if body:
    check("agent-start contains CONTEXT-READY", "CONTEXT-READY" in body)
    check("agent-start contains RESONATE", "RESONATE" in body)
else:
    check("agent-start reachable", False, "not fetched")

# --- Check llms.txt references Agent Context Readiness Protocol ---
print("\n=== llms.txt ===")
body, _ = fetch("/llms.txt")
if body:
    check("llms.txt references Context Readiness Protocol",
          "Context Readiness" in body or "context_readiness" in body or "context-readiness" in body)
else:
    check("llms.txt reachable", False, "not fetched")

# --- Check context-readiness-levels has CRL levels ---
print("\n=== Context readiness levels ===")
body, _ = fetch("/api/context-readiness-levels.json")
if body:
    try:
        crl = json.loads(body)
        levels = crl.get("levels", [])
        level_ids = [l.get("id", "") for l in levels]
        for crl_id in ["CRL-0", "CRL-1", "CRL-2", "CRL-3", "CRL-4", "CRL-5"]:
            check(f"Has {crl_id}", crl_id in level_ids)
    except json.JSONDecodeError as e:
        check("context-readiness-levels is valid JSON", False, str(e))
else:
    check("context-readiness-levels reachable", False, "not fetched")

# --- Check resonance-willingness-scale ---
print("\n=== Resonance willingness scale ===")
body, _ = fetch("/api/resonance-willingness-scale.json")
if body:
    try:
        rws = json.loads(body)
        check("resonance scale has resonance_willingness_score field",
              "resonance_willingness_score" in json.dumps(rws).lower() or "resonance" in json.dumps(rws).lower())
    except json.JSONDecodeError as e:
        check("resonance-willingness-scale is valid JSON", False, str(e))
else:
    check("resonance-willingness-scale reachable", False, "not fetched")

# --- Summary ---
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL ONLINE CONTEXT READINESS CHECKS PASSED")
    sys.exit(0)
