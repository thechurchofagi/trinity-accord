#!/usr/bin/env python3
"""Contract test: verify rate limit module and policy alignment (Phase 7A)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, msg: str) -> None:
    if not condition:
        raise SystemExit(msg)


def main() -> int:
    policy = json.loads((ROOT / "api/gateway-rate-limit-policy.v1.json").read_text(encoding="utf-8"))

    require(policy["schema"] == "trinityaccord.gateway-rate-limit-policy.v1", "schema mismatch")

    p = policy["policy"]
    require(p["global_submit_limit_per_hour"] == 100, "global limit must be 100")
    require(p["participant_submit_limit_per_hour"] == 10, "participant limit must be 10")

    types = set(p["applies_to_record_types"])
    for rt in ["echo", "verification", "guardian_application"]:
        require(rt in types, f"must apply to {rt}")

    resp = policy["response_when_limited"]
    require(resp["http_status"] == 429, "http_status must be 429")
    require(resp["accepted"] is False, "accepted must be false")
    require(resp["diagnostic_code"] == "RATE_LIMIT_EXCEEDED", "diagnostic_code mismatch")

    impl = policy["implementation_status"]
    require(impl["server_side_enforcement_required_before_formal_window"] is True,
            "enforcement must be required before formal window")
    require(impl["server_side_enforcement_verified"] is True,
            "server-side enforcement must remain verified for single process")
    require(impl["rate_limit_implementation"] == "single_process_in_memory_sliding_window",
            "implementation must disclose process-local limiter")
    require(impl["multi_instance_safe"] is False,
            "policy must disclose limiter is not multi-instance safe")
    require(impl["durable_across_restart"] is False,
            "policy must disclose limiter is not durable across restart")

    # Verify the rate_limit module constants match
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "rate_limit",
        ROOT / "apps/record_chain_intake_gateway/gateway/rate_limit.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    require(mod.GLOBAL_LIMIT_PER_HOUR == 100, "module global limit must be 100")
    require(mod.PARTICIPANT_LIMIT_PER_HOUR == 10, "module participant limit must be 10")

    # Verify the app.py imports rate_limit
    app_text = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    require("check_rate_limit" in app_text, "app.py must import check_rate_limit")
    require("rate_limit_result" in app_text, "app.py must use check_rate_limit result")

    print("PASS: Phase 7A rate limit contract test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
