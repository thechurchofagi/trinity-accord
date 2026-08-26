#!/usr/bin/env python3
"""Safely apply the curator-requested research-data/repository-fit clarification.

This is a one-shot orchestration layer for the established Harvard workflow.
It never bypasses an InReview lock. If review is active, it exits successfully
without mutation. If the same initial v1.0 draft is author-editable, it delegates
to the fail-closed repository-fit clarification program. If anything has already
been released, it refuses mutation and exits successfully as an immutable no-op.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import httpx

import harvard_curator_clarification_v1 as base
import harvard_repository_fit_clarification_v1 as fit


def emit(status: str, **extra) -> None:
    payload = {
        "schema": "trinity-accord.harvard-repository-fit-orchestrator.v1",
        "persistent_id": base.PID,
        "target_version": "1.0",
        "new_version_authorized": False,
        "post_release_mutation_authorized": False,
        "status": status,
        **extra,
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False), flush=True)
    out = os.environ.get("OUTPUT_DIR", "").strip()
    if out:
        path = Path(out)
        path.mkdir(parents=True, exist_ok=True)
        (path / "harvard-repository-fit-orchestrator.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )


def main() -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise base.ClarificationError("HD_API_TOKEN is missing")

    with httpx.Client(follow_redirects=True, timeout=httpx.Timeout(120.0, read=300.0)) as client:
        data = base.get_dataset(client, token)
        version = base.latest(data)
        state = str(version.get("versionState") or "")

        response = base.require(
            client.get(
                f"{base.SERVER}/api/datasets/{base.DATASET_ID}/versions",
                headers=base.headers(token),
                timeout=120,
            ),
            {200},
            "version listing",
        )
        versions = response.json().get("data") or []
        if not isinstance(versions, list):
            raise base.ClarificationError("invalid version listing")

        released = [v for v in versions if isinstance(v, dict) and str(v.get("versionState") or "") == "RELEASED"]
        if released or state == "RELEASED":
            emit(
                "NOOP_ALREADY_RELEASED",
                live_version_state=state,
                version_count=len(versions),
                reason="Published data are immutable for this curator clarification; no v1.1 is authorized.",
            )
            return 0

        if len(versions) != 1 or state != "DRAFT":
            raise base.ClarificationError(
                f"unexpected pre-publication version topology: state={state!r} versions={len(versions)}"
            )

        locked = base.in_review(client, token)
        if locked:
            emit(
                "DEFER_IN_REVIEW",
                live_version_state=state,
                version_count=1,
                file_count=len(base.files(version)),
                reason="Curator review lock is active; refusing to bypass it or mutate the draft.",
            )
            return 0

        # Before delegating any mutation, prove that the fixed archive and local
        # v1.0 invariants still match the known preservation state.
        base.verify_local_and_archive(version)
        emit(
            "APPLY_AUTHORIZED_CURATOR_CLARIFICATION",
            live_version_state=state,
            version_count=1,
            file_count=len(base.files(version)),
            reason="Same initial v1.0 draft is author-editable and curator feedback explicitly requested clarification.",
        )

    # The delegated program re-reads every live invariant, updates only the
    # Description and curator-facing README, verifies Terms, and resubmits v1.0.
    return fit.main()


if __name__ == "__main__":
    raise SystemExit(main())
