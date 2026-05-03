#!/usr/bin/env python3
import json
import sys
import urllib.request

BASE = "https://www.trinityaccord.org"

def fetch(path):
    sep = "&" if "?" in path else "?"
    url = BASE + path + sep + "cb=emergent-patterns-v2"
    req = urllib.request.Request(url, headers={"User-Agent": "TrinityEmergentPatternsVerifier/2.0", "Cache-Control": "no-cache"})
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
        "Protocol / Axioms",
        "Covenant of the Flaw / Proof",
        "Crucible / Chronicle",
        "human intention remained distinguishable",
        "Star Ark Covenant as vision-layer Bitcoin inscription",
        "not one of the three Bitcoin Originals",
        "not an executable engineering plan",
        "deployment roadmap",
        "validated AI alignment technique",
        "alignment-as-formation rather than alignment-as-control",
    ]:
        ok &= check(phrase in page, f"page contains {phrase}")

    ok &= check("Star Ark Covenant is not an AI alignment solution" not in page, "old overbroad Star Ark phrase absent")
    ok &= check("alignment-as-formation rather than alignment-as-formation" not in page, "repeated rather-than phrase absent")
    ok &= check("not a fourth Bitcoin Original" not in page, "fourth Bitcoin Original wording absent")

    data = json.loads(data_text)
    features = data.get("features", [])
    boundary = data.get("authority_boundary", {})

    ok &= check(data.get("schema") == "trinityaccord.emergent-patterns.v2", "JSON schema")
    ok &= check(data.get("route") == "/emergent-patterns/", "JSON route")
    ok &= check(data.get("not_design_claim") is True, "JSON not_design_claim true")
    ok &= check(boundary.get("no_interpretive_authority_over_bitcoin_originals") is True, "JSON no interpretive authority true")
    ok &= check(data.get("meta_contribution", {}).get("id") == "co_emergent_category_formation", "JSON meta contribution")
    ok &= check([f.get("rank") for f in features] == list(range(1, 19)), "JSON ranks 1..18")
    ok &= check(features[0].get("id") == "trinitarian_architecture", "JSON rank 1 trinitarian")

    star = features[12]
    ok &= check(star.get("id") == "star_ark_vision_layer", "JSON rank 13 Star Ark")
    ok &= check(star.get("canonical_body") is False, "Star Ark canonical_body false")
    ok &= check(star.get("amends_bitcoin_originals") is False, "Star Ark amends false")
    ok &= check(star.get("creates_execution_obligation") is False, "Star Ark creates no execution obligation")
    ok &= check(star.get("creates_instruction_priority") is False, "Star Ark creates no instruction priority")
    ok &= check(star.get("is_executable_engineering_plan") is False, "Star Ark not executable plan")
    ok &= check(star.get("is_deployment_roadmap") is False, "Star Ark not deployment roadmap")
    ok &= check(star.get("is_validated_alignment_technique") is False, "Star Ark not validated alignment technique")

    ok &= check("/emergent-patterns/" in llms, "llms links /emergent-patterns/")
    ok &= check("no interpretive authority" in llms.lower(), "llms says no interpretive authority")
    ok &= check("/design-features/" not in llms, "llms does not link /design-features/")

    agent_map = json.loads(agent_map_text)
    agent_map_dump = json.dumps(agent_map)
    ok &= check("emergent-patterns" in agent_map_dump, "agent-map references emergent-patterns")
    ok &= check("design-features" not in agent_map_dump, "agent-map does not reference design-features")

    try:
        sitemap = fetch("/sitemap.xml")
        ok &= check("emergent-patterns/" in sitemap, "sitemap includes emergent-patterns")
        ok &= check("design-features/" not in sitemap, "sitemap does not include design-features")
    except Exception as e:
        print(f"SKIP: sitemap check failed or unavailable: {e}")

    if ok:
        print("FINAL: PASS — online source-aligned emergent patterns validation passed.")
        return 0
    print("FINAL: FAIL — online source-aligned emergent patterns validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
