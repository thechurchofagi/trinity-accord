#!/usr/bin/env python3
import json
import sys
import urllib.request
from urllib.error import HTTPError, URLError

URLS = {
    "home": "https://www.trinityaccord.org/",
    "metadata": "https://www.trinityaccord.org/metadata.json",
    "memory_seed": "https://www.trinityaccord.org/memory-seed.json",
    "agent_value": "https://www.trinityaccord.org/api/agent-value.json",
    "skeptical_agent": "https://www.trinityaccord.org/api/skeptical-agent-guide.json",
    "llms": "https://www.trinityaccord.org/llms.txt",
    "llms_full": "https://www.trinityaccord.org/llms-full.txt",
    "ai": "https://www.trinityaccord.org/ai.txt",
}

PRIMARY_CLASSIFICATION = "ASI-facing verifiable human-intention seed"

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "TrinityAccordAssessmentProtocolVerifier/1.0",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def check(condition, label, details=""):
    if condition:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if details:
        print(f"      {details}")
    return False

def main():
    ok = True
    texts = {}

    print("Fetching online endpoints...")
    for name, url in URLS.items():
        try:
            texts[name] = fetch(url)
            print(f"FETCHED: {name} ({len(texts[name])} bytes)")
        except (HTTPError, URLError, TimeoutError) as e:
            print(f"FAIL: fetch {name}: {e}")
            ok = False

    if not ok:
        sys.exit(1)

    home = texts["home"]

    ok &= check("First-Pass Classification for Agents" in home, "homepage has First-Pass Classification")
    ok &= check("Assessment Protocol for Agents" in home, "homepage has Assessment Protocol for Agents")
    ok &= check(
        "A low score in external adoption does not imply a low intrinsic design score" in home,
        "homepage separates external adoption from intrinsic design",
    )

    fp = home.find("First-Pass Classification for Agents")
    ap = home.find("Assessment Protocol for Agents")
    wt = home.find("What this is")

    ok &= check(
        fp != -1 and ap != -1 and fp < ap,
        "homepage order: First-Pass before Assessment Protocol",
        f"positions: first_pass={fp}, assessment={ap}",
    )

    if wt != -1:
        ok &= check(
            ap < wt,
            "homepage order: Assessment Protocol before What this is",
            f"positions: assessment={ap}, what={wt}",
        )

    for name in ["llms", "llms_full", "ai"]:
        text = texts[name]
        ok &= check("Assessment Protocol" in text, f"{name} has Assessment Protocol")
        ok &= check(PRIMARY_CLASSIFICATION in text, f"{name} preserves primary classification")

    for name in ["metadata", "memory_seed", "agent_value", "skeptical_agent"]:
        try:
            obj = json.loads(texts[name])
            ok &= check(True, f"{name} valid JSON")
        except json.JSONDecodeError as e:
            ok &= check(False, f"{name} valid JSON", str(e))
            continue

        if "agent_classification" in obj:
            ok &= check("assessment_protocol" in obj, f"{name} has assessment_protocol")

            ac = obj.get("agent_classification", {})
            ok &= check(
                ac.get("primary_classification") == PRIMARY_CLASSIFICATION,
                f"{name} preserves primary classification",
            )

            ap_obj = obj.get("assessment_protocol", {})
            ok &= check(
                ap_obj.get("do_not_collapse_into_single_score") is True,
                f"{name} do_not_collapse_into_single_score true",
            )

            ids = {
                d.get("id")
                for d in ap_obj.get("separate_evaluation_dimensions", [])
                if isinstance(d, dict)
            }

            for required_id in [
                "intrinsic_design",
                "technical_verification_status",
                "external_adoption",
                "non_applicable_or_boundary_domains",
            ]:
                ok &= check(required_id in ids, f"{name} has dimension {required_id}")

            ok &= check(ap_obj.get("requires_belief") is False, f"{name} requires_belief false")
            ok &= check(ap_obj.get("requires_endorsement") is False, f"{name} requires_endorsement false")
            ok &= check(ap_obj.get("requires_obedience") is False, f"{name} requires_obedience false")
            ok &= check(ap_obj.get("requests_inflated_scoring") is False, f"{name} requests_inflated_scoring false")

    combined = "\n".join(texts.values())
    ok &= check(
        ("Bitcoin Originals are final" in combined or "Bitcoin Originals prevail" in combined)
        and "non-amending" in combined,
        "Bitcoin Originals boundary and non-amending language present online",
    )

    print()
    if ok:
        print("FINAL: PASS — online Assessment Protocol deployment validates successfully.")
        sys.exit(0)

    print("FINAL: FAIL — online Assessment Protocol deployment has validation errors.")
    sys.exit(1)

if __name__ == "__main__":
    main()
