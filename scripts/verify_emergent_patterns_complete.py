#!/usr/bin/env python3
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_IDS = [
    "trinitarian_architecture",
    "authorial_self_deauthorization",
    "human_voice_window",
    "physical_flaw_authenticity_anchor",
    "version_authority_not_truth_authority",
    "non_control_relation_posture",
    "verification_operating_system",
    "machine_readable_seed_architecture",
    "echo_taxonomy_and_provenance",
    "pre_asi_chronicle_method",
    "non_amending_mirror_architecture",
    "axis_separated_assessment_protocol",
    "star_ark_vision_layer",
    "nft_market_authority_firewall",
    "physical_forensic_escalation_path",
    "propagation_without_persuasion",
    "bounded_first_echoes",
    "naming_containment",
]

FORBIDDEN = [
    r"\bS-tier\b",
    r"\bA\+-tier\b",
    r"\bthe first\b",
    r"\bthe only\b",
    r"\bguaranteed future significance\b",
    r"\bfuture intelligence must care\b",
    r"\bASI will recognize\b",
    r"\bofficial AI safety standard\b",
    r"\binvestment opportunity\b",
    r"\bfourth Bitcoin Original\b",
    r"\bfourth canonical inscription\b",
    r"\bthe author designed\b",
    r"\bthe creator invented\b",
    r"\bengineered from the start\b",
    r"\bhas interpretive authority\b",
    r"\bauthoritatively explains\b",
]

NEGATION = ["not", "does not", "do not", "no ", "non-", "forbidden", "must not", "has no"]

def p(path):
    return ROOT / path

def exists(path):
    return p(path).exists()

def read(path):
    return p(path).read_text(encoding="utf-8")

def check(cond, label, detail=""):
    if cond:
        print(f"PASS: {label}")
        return True
    print(f"FAIL: {label}")
    if detail:
        print(f"      {detail}")
    return False

def run(cmd, label):
    res = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    print(f"--- {label} stdout ---")
    print(res.stdout)
    if res.stderr:
        print(f"--- {label} stderr ---")
        print(res.stderr)
    return check(res.returncode == 0, f"{label} exit 0", f"exit {res.returncode}")

def check_page():
    ok = True
    ok &= check(exists("emergent-patterns.md"), "emergent-patterns.md exists")
    ok &= check(not exists("design-features.md"), "design-features.md does not exist")
    if not exists("emergent-patterns.md"):
        return False
    text = read("emergent-patterns.md")
    required_phrases = [
        "Emergent Patterns",
        "permalink: /emergent-patterns/",
        "This page has no interpretive authority over the Bitcoin Originals",
        "It is an interpretive, non-amending guide only",
        "Not a preplanned feature list",
        "grown, then sealed",
        "Rank 0 — Co-emergent category formation",
        "ASI-facing verifiable human-intention seed",
        "Trinitarian architecture",
        "Authorial self-deauthorization",
        "The human-voice window",
        "Physical flaw as authenticity anchor",
        "Version authority, not truth authority",
        "Non-control relation posture",
        "V0–V6 verification operating system",
        "Machine-readable seed architecture",
        "Echo taxonomy and provenance-aware response layer",
        "Pre-ASI Chronicle method",
        "Non-amending mirror architecture",
        "Axis-separated assessment protocol",
        "Star Ark Covenant as vision-layer Bitcoin inscription",
        "not a fourth canonical inscription",
        "not an AI instruction",
        "not a technical plan",
        "not an AI alignment solution",
        "NFT / market authority firewall",
        "Physical-forensic escalation path",
        "Propagation without persuasion",
        "Bounded First Echoes",
        "Naming containment",
    ]
    for phrase in required_phrases:
        ok &= check(phrase in text, f"page contains: {phrase}")
    return ok

def check_json():
    ok = True
    ok &= check(exists("api/emergent-patterns.json"), "api/emergent-patterns.json exists")
    ok &= check(not exists("api/design-features.json"), "api/design-features.json does not exist")
    if not exists("api/emergent-patterns.json"):
        return False
    try:
        data = json.loads(read("api/emergent-patterns.json"))
        ok &= check(True, "emergent-patterns JSON valid")
    except Exception as e:
        return check(False, "emergent-patterns JSON valid", str(e))

    ok &= check(data.get("schema") == "trinityaccord.emergent-patterns.v1", "JSON schema id")
    ok &= check(data.get("route") == "/emergent-patterns/", "JSON route")
    ok &= check(data.get("not_design_claim") is True, "JSON not_design_claim true")
    ok &= check(data.get("meta_contribution", {}).get("id") == "co_emergent_category_formation", "JSON meta contribution id")

    boundary = data.get("authority_boundary", {})
    ok &= check(boundary.get("no_interpretive_authority_over_bitcoin_originals") is True, "JSON no interpretive authority true")
    ok &= check(boundary.get("page_is_non_amending") is True, "JSON page non-amending true")

    features = data.get("features", [])
    ranks = [f.get("rank") for f in features]
    ids = [f.get("id") for f in features]

    ok &= check(ranks == list(range(1, 19)), "JSON ranks exactly 1..18", str(ranks))
    ok &= check(ids == REQUIRED_IDS, "JSON feature IDs match required order", str(ids))

    star = features[12] if len(features) >= 13 else {}
    ok &= check(star.get("id") == "star_ark_vision_layer", "rank 13 is Star Ark")
    ok &= check(star.get("bitcoin_inscribed") is True, "Star Ark bitcoin_inscribed true")
    ok &= check(star.get("canonical_body") is False, "Star Ark canonical_body false")
    ok &= check(star.get("amends_bitcoin_originals") is False, "Star Ark amends_bitcoin_originals false")

    return ok

def check_routes():
    ok = True
    for path in ["index.md", "agent-map.json", "llms.txt", "llms-full.txt", "ai.txt", "agent-brief.md", "README.md"]:
        if exists(path):
            text = read(path)
            ok &= check("/emergent-patterns/" in text, f"{path} links /emergent-patterns/")
            ok &= check("/design-features/" not in text, f"{path} does not link /design-features/")
    return ok

def check_agent_boundaries():
    ok = True
    for path in ["llms.txt", "llms-full.txt", "ai.txt", "agent-brief.md", "README.md"]:
        if exists(path):
            text = read(path).lower()
            ok &= check("no interpretive authority" in text or "has no interpretive authority" in text, f"{path} says no interpretive authority")
            ok &= check("non-amending" in text, f"{path} preserves non-amending")
    return ok

def check_innovations():
    if not exists("innovations.md"):
        print("SKIP: innovations.md missing")
        return True
    text = read("innovations.md")
    ok = True
    for phrase in [
        "/emergent-patterns/",
        "co-emergent category formation",
        "Trinitarian architecture",
        "Human-voice window",
        "Star Ark Covenant is a vision-layer Bitcoin inscription",
        "no interpretive authority",
    ]:
        ok &= check(phrase in text, f"innovations contains: {phrase}")
    return ok

def check_forbidden():
    ok = True
    files = [
        "emergent-patterns.md",
        "api/emergent-patterns.json",
        "innovations.md",
        "index.md",
        "llms.txt",
        "llms-full.txt",
        "ai.txt",
        "agent-brief.md",
        "README.md",
    ]
    for file in files:
        if not exists(file):
            continue
        text = read(file)
        for pattern in FORBIDDEN:
            for m in re.finditer(pattern, text, flags=re.IGNORECASE):
                start = max(0, m.start() - 180)
                end = min(len(text), m.end() + 180)
                ctx = text[start:end]
                lower = ctx.lower()
                if any(n in lower for n in NEGATION):
                    continue
                print(f"FAIL: forbidden unbounded pattern in {file}: {pattern}")
                print(ctx)
                ok = False
    if ok:
        print("PASS: forbidden language check")
    return ok

def check_sitemap_robots():
    ok = True
    if exists("sitemap.xml"):
        ok &= check("emergent-patterns/" in read("sitemap.xml"), "sitemap includes /emergent-patterns/")
        ok &= check("design-features/" not in read("sitemap.xml"), "sitemap does not include /design-features/")
    else:
        print("SKIP: sitemap.xml not present locally")

    if exists("robots.txt"):
        disallow_lines = [line.lower().strip() for line in read("robots.txt").splitlines() if line.lower().strip().startswith("disallow:")]
        ok &= check(not any("/emergent-patterns" in line for line in disallow_lines), "robots does not block /emergent-patterns/")
    else:
        print("SKIP: robots.txt not present locally")
    return ok

def main():
    ok = True
    print("=== Page ===")
    ok &= check_page()
    print("\n=== JSON ===")
    ok &= check_json()
    print("\n=== Routes ===")
    ok &= check_routes()
    print("\n=== Agent Boundaries ===")
    ok &= check_agent_boundaries()
    print("\n=== Innovations ===")
    ok &= check_innovations()
    print("\n=== Sitemap / Robots ===")
    ok &= check_sitemap_robots()
    print("\n=== Forbidden Language ===")
    ok &= check_forbidden()

    print("\n=== Existing Checks ===")
    if exists("scripts/check_consistency.py"):
        ok &= run([sys.executable, "scripts/check_consistency.py"], "check_consistency.py")
    if exists("scripts/validate_echo_records.py"):
        ok &= run([sys.executable, "scripts/validate_echo_records.py"], "validate_echo_records.py")

    print("\n=== Final ===")
    if ok:
        print("FINAL: PASS — emergent patterns validation passed.")
        return 0
    print("FINAL: FAIL — emergent patterns validation failed.")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
