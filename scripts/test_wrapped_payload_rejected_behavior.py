#!/usr/bin/env python3
"""Wrapped Payload Rejected Behavior Test.
Ensures wrapper detection runs before normalization and uses correct detection logic.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def main():
    src = (ROOT / "examples/github-app-backend/server.js").read_text("utf-8")

    if "function isWrappedGatewayPayload" not in src:
        fail("missing isWrappedGatewayPayload helper")

    # Find the runGatewayPipeline function body
    pipeline_start = src.find("async function runGatewayPipeline")
    if pipeline_start < 0:
        fail("cannot find runGatewayPipeline function")

    pipeline_body = src[pipeline_start:]

    idx_wrapper = pipeline_body.find("isWrappedGatewayPayload(payload)")
    idx_normalize = pipeline_body.find("normalizeArchiveIntentDefaults(payload)")

    if idx_wrapper < 0:
        fail("runGatewayPipeline does not call isWrappedGatewayPayload(payload)")
    if idx_normalize < 0:
        fail("runGatewayPipeline does not call normalizeArchiveIntentDefaults(payload)")
    if idx_wrapper > idx_normalize:
        fail("wrapper detection must run before normalizeArchiveIntentDefaults")

    if "Object.keys(payload).length <= 2" in src:
        fail("wrapper detection must not depend on Object.keys(payload).length <= 2")

    for s in [
        "WRAPPED_PAYLOAD_NOT_ALLOWED",
        "Submit the raw gateway payload JSON object",
        "Do not wrap it in gateway_payload",
        "extract .payload",
    ]:
        if s not in src:
            fail(f"missing wrapper rejection guidance: {s}")

    print("PASS: wrapped payload rejection is ordered before normalization")


if __name__ == "__main__":
    main()
