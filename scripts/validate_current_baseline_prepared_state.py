#!/usr/bin/env python3
"""Validate a prepared current-baseline transition while the prior DOI remains active."""
from __future__ import annotations

from validate_current_baseline_publication_state import (
    INDEX_PATH,
    STATE_PATH,
    canonical_index_digest,
    require,
    strict_json,
    validate_authorization,
    validate_prepared,
)


def main() -> int:
    auth = validate_authorization()
    require(auth.get("status") == "prepared", "current-baseline authorization is not prepared")
    state = strict_json(STATE_PATH)
    index = strict_json(INDEX_PATH)
    require(
        state.get("publication_status") == "published_and_publicly_restored",
        "prepared transition must retain the prior verified publication status",
    )
    require(
        index.get("source_digest") == canonical_index_digest(index),
        "recovery index source digest mismatch",
    )
    # Reuse the complete prepared-state validator. Its synthetic status value
    # represents the transition phase; the committed state deliberately keeps
    # the last verified DOI active until the new DOI and Arweave readback pass.
    transition_state = dict(state)
    transition_state["publication_status"] = "prepared_for_current_baseline_publication"
    validate_prepared(auth, transition_state, index)
    print("Current baseline prepared transition valid; prior DOI remains active.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
