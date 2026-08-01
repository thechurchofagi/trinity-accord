#!/usr/bin/env python3
"""Publish the first deterministic capsule from a fresh Zenodo deposition.

The failed V1-V3 attempts created one unpublished deposition whose file links
continued to resolve an obsolete immutable object even after delete/re-upload.
Zenodo explicitly permits deletion of unpublished depositions.  This publisher
therefore removes only unpublished depositions in the repository-preservation
series, proves that they disappeared, creates a fresh deposition, and applies
all deterministic V3 byte and metadata gates before publication.

Published records are never deleted or replaced.  If an exact capsule is
already published, it is verified and reconciled into repository state.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

import publish_preservation_capsule_to_zenodo as publisher
import publish_preservation_capsule_to_zenodo_v3 as publisher_v3


STALE_DRAFT_ID = 21739344


def delete_unpublished_series_drafts(
    client: publisher.ZenodoClient,
    records: list[dict[str, Any]],
    *,
    attempts: int = 20,
) -> list[int]:
    """Delete only unpublished drafts belonging to this preservation series."""
    drafts = [item for item in records if not publisher.is_published(item)]
    deleted_ids: list[int] = []
    for draft in drafts:
        draft_id = publisher.deposition_id(draft)
        client.delete(f"/deposit/depositions/{draft_id}")
        deleted_ids.append(draft_id)

    if not deleted_ids:
        return deleted_ids

    remaining = set(deleted_ids)
    for attempt in range(1, attempts + 1):
        current = publisher.series_records(publisher.list_depositions(client))
        remaining = {
            publisher.deposition_id(item)
            for item in current
            if not publisher.is_published(item)
            and publisher.deposition_id(item) in set(deleted_ids)
        }
        if not remaining:
            return deleted_ids
        if attempt < attempts:
            time.sleep(float(min(attempt, 5)))
    raise SystemExit(
        "Zenodo unpublished preservation draft deletion did not converge: "
        + ",".join(str(value) for value in sorted(remaining))
    )


def publish_from_fresh_draft(
    client: publisher.ZenodoClient,
    capsule_dir: Path,
    state: dict[str, Any],
    api_base: str,
) -> dict[str, Any]:
    package = publisher.verify_local_package(capsule_dir)
    records = publisher.series_records(publisher.list_depositions(client))

    same = [item for item in records if publisher.capsule_id(item) == package["capsule_id"]]
    published_matches = [item for item in same if publisher.is_published(item)]
    if len(published_matches) > 1:
        raise SystemExit(f"duplicate published Zenodo capsule id: {package['capsule_id']}")
    if published_matches:
        published = publisher.refresh(client, published_matches[0])
        publisher_v3.verify_remote_files(client, published, capsule_dir)
        return publisher.build_state(published, package, api_base, records, state)

    unpublished_series = [item for item in records if not publisher.is_published(item)]
    deleted_ids = delete_unpublished_series_drafts(client, unpublished_series)
    if deleted_ids:
        print(
            "ZENODO_UNPUBLISHED_DRAFTS_DELETED "
            + ",".join(str(value) for value in deleted_ids)
        )
    if STALE_DRAFT_ID in deleted_ids:
        print(f"ZENODO_STALE_DRAFT_REMOVED {STALE_DRAFT_ID}")

    remaining_records = publisher.series_records(publisher.list_depositions(client))
    remaining_drafts = [
        item for item in remaining_records if not publisher.is_published(item)
    ]
    if remaining_drafts:
        raise SystemExit("unpublished preservation drafts remain before fresh creation")
    published_series = [
        item for item in remaining_records if publisher.is_published(item)
    ]

    draft = publisher.create_draft(
        client,
        published_series[-1] if published_series else None,
        package["metadata"],
    )
    draft_id = publisher.deposition_id(draft)
    if draft_id in set(deleted_ids):
        raise SystemExit("Zenodo reused a deleted stale deposition id")
    print(f"ZENODO_FRESH_DRAFT_CREATED {draft_id}")

    updated = client.request(
        "PUT",
        f"/deposit/depositions/{draft_id}",
        payload={"metadata": package["metadata"]},
    )
    if not isinstance(updated, dict):
        raise SystemExit("Zenodo metadata update response is not an object")
    draft = publisher.refresh(client, updated)

    # A new-version draft can inherit files from its published predecessor.
    publisher_v3.clear_files(client, draft)
    draft = publisher.refresh(client, draft)
    publisher_v3.upload_files(client, draft, capsule_dir)
    draft = publisher.refresh(client, draft)
    publisher_v3.verify_remote_files(client, draft, capsule_dir)

    published = client.request(
        "POST", f"/deposit/depositions/{draft_id}/actions/publish", payload={}
    )
    if not isinstance(published, dict):
        raise SystemExit("Zenodo publish response is not an object")
    published = publisher.refresh(client, published)
    publisher_v3.verify_remote_files(client, published, capsule_dir)

    final_records = publisher.series_records(publisher.list_depositions(client))
    return publisher.build_state(published, package, api_base, final_records, state)


def main() -> int:
    publisher.publish_or_reconcile = publish_from_fresh_draft
    return publisher.main()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        raise SystemExit(130)
