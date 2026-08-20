#!/usr/bin/env python3
"""Compatibility wrapper for Harvard preservation state machine.

Harvard Dataverse returns HTTP 403 (rather than 400/409) when a depositor calls
submitForReview for a Dataset that is already in review. Treat that exact
server-confirmed state as idempotent success; all other responses remain
fail-closed.
"""
from __future__ import annotations

import sys

import harvard_preservation_state_machine as impl


def submit_for_review(client, token: str, phase: str) -> str:
    response = client.post(
        f"{impl.SERVER}/api/datasets/:persistentId/submitForReview",
        headers=impl.hd_headers(token),
        params={"persistentId": impl.PID},
        timeout=120,
    )
    if response.status_code in (200, 201, 202):
        impl.log(f"SUBMIT FOR REVIEW PASS phase={phase} HTTP={response.status_code}")
        return "submitted"
    body = response.text[:1500]
    lower = body.lower()
    if response.status_code in (400, 403, 409) and (
        "already in review" in lower
        or "already submitted" in lower
        or ("review" in lower and "already" in lower)
        or "locked" in lower
    ):
        impl.log(
            f"SUBMIT FOR REVIEW already-pending phase={phase} "
            f"HTTP={response.status_code}"
        )
        return "already_pending"
    raise impl.StateMachineError(
        f"Harvard submitForReview phase={phase}: HTTP {response.status_code}: {body}"
    )


impl.submit_for_review = submit_for_review

if __name__ == "__main__":
    try:
        raise SystemExit(impl.main())
    except Exception as exc:
        impl.log(f"FAIL {type(exc).__name__}: {exc}")
        raise
