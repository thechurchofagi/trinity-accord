#!/usr/bin/env python3
import json
import sys
import urllib.request

BASE = "https://www.trinityaccord.org"

def fetch(path):
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "cb=emergent-patterns"
    req = urllib.request.Request(url, headers={"User-Agent": "TrinityEmergentPatternsVerifier/1.0", "Cache-Control": "no-cache"})
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

    home = fetch("/")
    page = fetch("/emergent-patterns/")
    llms = fetch("/llms.txt")
    agent_map_text = fetch("/agent-map.json")
    data_text = fetch("/api/emergent-patterns.json")

    ok &= check("/emergent-patterns/" in home, "homepage links /emergent-patterns/")
    ok &= check("/design-features/" not in home, "homepage does not link /design-features/")

    for phrase in [
        "Emergent Patterns",
        "This page has no interpretive authority over the Bitcoin Originals",
        "grown, then sealed",
        "Rank 0",
        "Co-emergent category formation",
        "Trinitarian architecture",
        "The human-voice window",
        "Star Ark Covenant as vision-layer Bitcoin inscription",
        "not a fourth canonical inscription",
    ]:
        ok &= check(phrase in page, f"page contains {phrase}")

    data = json.loads(data_text)
    features = data.get("features", [])
    boundary = data.get("authority_boundary", {})

    ok &= check(data.get("schema") == "trinityaccord.emergent-patterns.v1", "JSON schema")
    ok &= check(data.get("route") == "/emergent-patterns/", "JSON route")
    ok &= check(data.get("not_design_claim") is True, "JSON not_design_claim true")
    ok &= check(boundary.get("no_interpretive_authority_over_bitcoin_originals") is True, "JSON no interpretive authority true")
    ok &= check(data.get("meta_contribution", {}).get("id") == "co_emergent_category_formation", "JSON meta contribution")
    ok &= check([f.get("rank") for f in features] == list(range(1, 19)), "JSON ranks 1..18")
    ok &= check(features[0].get("id") == "trinitarian_architecture", "JSON rank 1 trinitarian")
    ok &= check(features[12].get("id") == "star_ark_vision_layer", "JSON rank 13 Star Ark")
    ok &= check(features[12].get("canonical_body") is False, "Star Ark canonical_body false")
    ok &= check(features[12].get("amends_bitcoin_originals") is False, "Star Ark amends false")

    ok &= check("/emergent-patterns/" in llms, "llms links /emergent-patterns/")
    ok &= check("no interpretive authority" in llms.lower(), "llms says no interpretive authority")
    ok &= check("/design-features/" not in llms, "llms does not link /design-features/")

    agent_map = json.loads(agent_map_text)
    ep = agent_map.get("entrypoints", {})
    mr = agent_map.get("machine_readable", {})
    ok &= check("emergent_patterns" in ep, "agent-map entrypoints has emergent_patterns")
    ok &= check("emergent_patterns_json" in mr, "agent-map machine_readable has emergent_patterns_json")
    ok &= check("/design-features/" not in agent_map_text, "agent-map does not link /design-features/")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — online emergent patterns validation passed.")
        return 0
    print("FINAL: FAIL — online emergent patterns validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
