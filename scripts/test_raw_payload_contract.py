#!/usr/bin/env python3
"""Raw Payload Contract Test."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
P = F = T = 0
def check(c, l):
    global P, F, T; T += 1
    if c: P += 1; print(f"  PASS: {l}")
    else: F += 1; print(f"  FAIL: {l}")
def rf(r):
    return (ROOT / r).read_text("utf-8")

def test():
    for fpath, getv in [
        ("api/agent-submit-gateway.json", lambda d: d.get("v0_v5_archive_submission", {})),
        ("api/agent-first-contact.json", lambda d: next((i for i in d.get("choose_one",[]) if i.get("intent")=="verify_v0_v5_agent_declared"), {})),
    ]:
        print(f"\n--- {fpath} ---")
        d = json.loads(rf(fpath))
        v = getv(d)
        check(v.get("raw_payload_only") is True, "raw_payload_only=true")
        check(v.get("do_not_wrap_payload") is True, "do_not_wrap_payload=true")
        check("gateway_payload" in v.get("forbidden_wrappers", []), "gateway_payload forbidden")
        sf = v.get("server_generated_fields_not_allowed_in_payload", [])
        for f in ["gateway_receipt_id","created_by_gateway","server_validated","server_rendered","render_api_only"]:
            check(f in sf, f"{f} forbidden in payload")

    d = json.loads(rf("api/agent-submission-guide.json"))
    v = next((e for e in d.get("decision_tree",[]) if "V0" in e.get("if","") and "V4+" in e.get("if","")), {})
    print("\n--- api/agent-submission-guide.json ---")
    check(v.get("raw_payload_only") is True, "raw_payload_only=true")
    check(v.get("do_not_wrap_payload") is True, "do_not_wrap_payload=true")

    print("\n--- server.js ---")
    s = rf("examples/github-app-backend/server.js")
    check("WRAPPED_PAYLOAD_NOT_ALLOWED" in s, "server has WRAPPED_PAYLOAD_NOT_ALLOWED")

if __name__ == "__main__":
    test()
    print(f"\n{'='*60}\nResults: {P}/{T} passed, {F}/{T} failed")
    sys.exit(1 if F else 0)
