import json
import re
from pathlib import Path

from apps.record_chain_intake_gateway.gateway.validation import compute_oath_policy_sha256

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "api" / "record-chain-oath-policy.v1.json"
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"


def test_oath_policy_hash_agrees_across_api_gateway_and_builder():
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    expected = compute_oath_policy_sha256(policy)

    assert policy["oath_policy_sha256"] == expected

    builder_text = BUILDER.read_text(encoding="utf-8")
    match = re.search(r'const OATH_POLICY_SHA256\s*=\s*"([a-f0-9]{64})"', builder_text)
    assert match, "builder must define OATH_POLICY_SHA256"
    assert match.group(1) == expected
