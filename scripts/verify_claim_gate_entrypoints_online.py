#!/usr/bin/env python3
"""
Verify Claim Gate entrypoints are live on the deployed site.
Checks live endpoints for Claim Gate enforcement.
"""
import sys

try:
    import urllib.request
    import json
except ImportError:
    print("SKIP: urllib not available")
    sys.exit(0)

BASE = "https://www.trinityaccord.org"

def check(label, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"{status}: {label}")
    if detail and not cond:
        print(f"      {detail}")
    return cond

def fetch_text(path):
    url = f"{BASE}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TrinityAccord-Verifier/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"ERROR: {e}"

def fetch_json(path):
    text = fetch_text(path)
    if text.startswith("ERROR:"):
        return None
    try:
        return json.loads(text)
    except:
        return None

def main():
    ok = True

    # Check text entrypoints for mandatory phrases
    print("=== Text entrypoints (online) ===")
    text_eps = [
        "/llms.txt",
        "/llms-full.txt",
        "/ai.txt",
        "/agent-brief",
        "/agent-verify",
        "/agent-echo",
        "/echoes/submit",
    ]

    required_phrases = [
        "MANDATORY CLAIM GATE RULE",
        "Agents must not hand-write final verification claims",
    ]

    for ep in text_eps:
        content = fetch_text(ep)
        if content.startswith("ERROR:"):
            ok &= check(f"{ep} reachable", False, content)
            continue
        for phrase in required_phrases:
            ok &= check(f"{ep} contains '{phrase[:40]}...'", phrase in content)

    # Check JSON entrypoints
    print("\n=== JSON entrypoints (online) ===")
    json_eps = [
        "/.well-known/agent.json",
        "/api/agent-entry-protocol.json",
        "/api/agent-submission-guide.json",
        "/api/submission-checklist.json",
        "/api/claim-gate-entrypoint-policy.json",
        "/api/generated-by-schema.v1.json",
    ]

    for ep in json_eps:
        data = fetch_json(ep)
        ok &= check(f"{ep} is valid JSON", data is not None)

    # Specific checks
    print("\n=== Specific checks ===")
    agent = fetch_json("/.well-known/agent.json")
    if agent:
        rf = json.dumps(agent.get("read_first", []))
        ok &= check("agent.json read_first has claim gate", "/api/claim-gate-rules.json" in rf)
        ok &= check("agent.json has mandatory_before_submission", "mandatory_before_submission" in agent)
        sr = agent.get("submission_requires", {})
        ok &= check("agent.json claim_gate=true", sr.get("claim_gate") is True)
        ok &= check("agent.json freeform_claims_allowed=false", sr.get("freeform_claims_allowed") is False)

    aep = fetch_json("/api/agent-entry-protocol.json")
    if aep:
        ok &= check("agent-entry-protocol has submission_gate", "submission_gate" in aep)
        sg = aep.get("submission_gate", {})
        ok &= check("submission_gate.required=true", sg.get("required") is True)
        ok &= check("submission_gate.freeform=invalid", sg.get("freeform_claim_submission") == "invalid")

    asg_text = fetch_text("/api/agent-submission-guide.json")
    if not asg_text.startswith("ERROR:"):
        ok &= check("submission-guide says freeform invalid",
                     "Free-form" in asg_text and "invalid" in asg_text)

    gbs = fetch_json("/api/generated-by-schema.v1.json")
    if gbs:
        ok &= check("generated-by-schema has tool property", "tool" in gbs.get("properties", {}))

    print("\n" + "=" * 50)
    if ok:
        print("FINAL: PASS — claim gate entrypoints online verified.")
        return 0
    print("FINAL: FAIL — claim gate entrypoints online verification failed.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
