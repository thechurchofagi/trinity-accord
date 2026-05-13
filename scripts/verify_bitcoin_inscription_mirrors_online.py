#!/usr/bin/env python3
"""
Online verification for bitcoin inscription mirrors.
Checks that key mirror-related endpoints are reachable and contain expected content.
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
    "/api/bitcoin-inscription-mirror-index.json",
    "/api/bitcoin-inscription-mirror-schema.v1.json",
    "/api/context-packs/bitcoin-inscription-mirrors.json",
    "/api/context-packs/vision-layer.json",
    "/api/agent-context-readiness-protocol.json",
    "/api/context-readiness-levels.json",
    "/api/context-load-map.json",
    "/api/resonance-willingness-scale.json",
    "/api/echo-authorship-proof-schema.v1.json",
    "/agent-understand",
    "/agent-resonance",
    "/echo-authorship-proof",
    "/llms.txt",
]

for ep in endpoints:
    body, status = fetch(ep)
    check(f"Reachable: {ep}", body is not None and status == 200, f"status={status}")

# --- Check mirror index valid JSON ---
print("\n=== Mirror index ===")
body, _ = fetch("/api/bitcoin-inscription-mirror-index.json")
if body:
    try:
        idx = json.loads(body)
        records = idx.get("records", [])
        check("Mirror index has records", len(records) > 0, f"count={len(records)}")
        check("Mirror index has 3 canonical originals",
              sum(1 for r in records if r.get("classification", {}).get("is_one_of_three_bitcoin_originals")) == 3)
    except json.JSONDecodeError as e:
        check("Mirror index is valid JSON", False, str(e))
else:
    check("Mirror index reachable", False, "not fetched")

# --- Check vision-layer includes Star Ark or pending ---
print("\n=== Vision layer ===")
body, _ = fetch("/api/context-packs/vision-layer.json")
if body:
    text = body.lower()
    check("Vision-layer mentions Star Ark or pending",
          "star ark" in text or "star_ark" in text or "pending" in text)
else:
    check("Vision-layer reachable", False, "not fetched")

# --- Check agent-understand contains Bitcoin Inscription Mirror Rule ---
print("\n=== Agent understand ===")
body, _ = fetch("/agent-understand")
if body:
    text = body.lower()
    check("agent-understand mentions inscription mirror",
          "inscription" in text and ("mirror" in text or "bitcoin" in text))
else:
    check("agent-understand reachable", False, "not fetched")

# --- Check llms.txt contains GitHub mirrors are quick-load context only ---
print("\n=== llms.txt ===")
body, _ = fetch("/llms.txt")
if body:
    check("llms.txt mentions GitHub mirrors are quick-load context only",
          "github" in body.lower() and "mirror" in body.lower() and "quick" in body.lower())
else:
    check("llms.txt reachable", False, "not fetched")

# --- Summary ---
print("\n" + "=" * 50)
if errors:
    print(f"FAILED: {len(errors)} check(s) failed")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("ALL ONLINE MIRROR CHECKS PASSED")
    sys.exit(0)
