#!/usr/bin/env python3
"""Validate historical checkpoint v4 without treating it as the permanent repository tip.

The v4 publication validator predates the Bitcoin-12 DOI-only closure and therefore
expects recovery-catalog.json's generic current pointer to equal the v4 DOI forever.
This adapter preserves every v4 validation check while separately fail-closing over
the one later, independently authorized and observed repository publication.
"""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "scripts" / "current_baseline_publication_v4.py"
CATALOG = ROOT / "preservation" / "recovery-catalog.json"
V4_AUTH = ROOT / "preservation" / "current-baseline-publication-authorization-v4.json"
BITCOIN12_AUTH = ROOT / "preservation" / "bitcoin12-external-closure-authorization-v1.json"
BITCOIN12_OBSERVATION = ROOT / "preservation" / "bitcoin12-doi-closure-observation-v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def equal(observed, expected, label: str) -> None:
    require(observed == expected, f"{label} mismatch: observed={observed!r} expected={expected!r}")


def load_legacy_module():
    spec = importlib.util.spec_from_file_location("current_baseline_publication_v4_legacy", LEGACY)
    require(spec is not None and spec.loader is not None, "cannot load v4 publication validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_historical_checkpoint(catalog_core: dict, v4: dict) -> None:
    checkpoint = catalog_core.get("current_evidence_checkpoint")
    require(isinstance(checkpoint, dict), "catalog.current_evidence_checkpoint missing")
    equal(checkpoint.get("sequence"), 4, "catalog.checkpoint.sequence")
    equal(checkpoint.get("status"), "published_verified_and_consumed", "catalog.checkpoint.status")
    equal(checkpoint.get("authorization"), "preservation/current-baseline-publication-authorization-v4.json", "catalog.checkpoint.authorization")
    equal(checkpoint.get("version_doi"), v4.get("published_doi"), "catalog.checkpoint.doi")
    equal(checkpoint.get("source_baseline_commit_sha"), v4.get("published_source_baseline_commit_sha"), "catalog.checkpoint.source")
    equal(checkpoint.get("package_identity_sha256"), v4.get("published_package_identity_sha256"), "catalog.checkpoint.package")


def validate_later_current_pointer(catalog_core: dict, v4: dict) -> bool:
    current_doi = catalog_core.get("current_verified_version_doi")
    if current_doi == v4.get("published_doi"):
        equal(catalog_core.get("current_verified_source_git_commit_sha"), v4.get("published_source_baseline_commit_sha"), "catalog.current_source")
        equal(catalog_core.get("current_verified_package_identity_sha256"), v4.get("published_package_identity_sha256"), "catalog.current_package")
        equal(catalog_core.get("current_verified_record_id"), v4.get("published_record_id"), "catalog.current_record_id")
        return False

    auth = load(BITCOIN12_AUTH)
    observation = load(BITCOIN12_OBSERVATION)
    equal(auth.get("schema"), "trinityaccord.bitcoin12-external-closure-authorization.v1", "bitcoin12.auth.schema")
    equal(auth.get("status"), "doi_published_arweave_deferred", "bitcoin12.auth.status")
    equal(auth.get("publication_scope"), "doi_only_arweave_deferred", "bitcoin12.auth.scope")
    equal(auth.get("publish_new_repository_doi_version"), True, "bitcoin12.auth.publish_doi")
    equal(auth.get("publish_new_repository_arweave_capsule"), False, "bitcoin12.auth.publish_arweave")
    equal(auth.get("non_amending_boundary"), True, "bitcoin12.auth.non_amending")
    equal(auth.get("three_bitcoin_originals_remain_canonical"), True, "bitcoin12.auth.canon_boundary")
    equal(auth.get("live_main_equivalence_claimed"), False, "bitcoin12.auth.live_main_equivalence")

    equal(observation.get("schema"), "trinityaccord.bitcoin12-doi-closure-observation.v1", "bitcoin12.observation.schema")
    equal(observation.get("status"), "passed", "bitcoin12.observation.status")
    equal(observation.get("public_doi_only_cold_restore"), "passed", "bitcoin12.observation.restore")
    equal(observation.get("arweave_publication_status"), "deferred_by_owner", "bitcoin12.observation.arweave")
    equal(observation.get("new_arweave_transaction_created"), False, "bitcoin12.observation.new_arweave_tx")
    equal(observation.get("bitcoin_l1_l2_l3"), "12/12 PASS", "bitcoin12.observation.bitcoin_proof")
    equal(observation.get("non_amending_boundary"), True, "bitcoin12.observation.non_amending")
    equal(observation.get("three_bitcoin_originals_remain_canonical"), True, "bitcoin12.observation.canon_boundary")
    equal(observation.get("live_main_equivalence_claimed"), False, "bitcoin12.observation.live_main_equivalence")

    doi = auth.get("published_repository_doi")
    source = auth.get("published_source_baseline_commit_sha")
    package = auth.get("published_package_identity_sha256")
    record_id = auth.get("published_repository_record_id")
    equal(observation.get("repository_doi"), doi, "bitcoin12.auth_observation.doi")
    equal(observation.get("source_git_commit_sha"), source, "bitcoin12.auth_observation.source")
    equal(observation.get("package_identity_sha256"), package, "bitcoin12.auth_observation.package")
    equal(observation.get("zenodo_record_id"), record_id, "bitcoin12.auth_observation.record_id")

    equal(current_doi, doi, "catalog.current_doi")
    equal(catalog_core.get("current_verified_source_git_commit_sha"), source, "catalog.current_source")
    equal(catalog_core.get("current_verified_package_identity_sha256"), package, "catalog.current_package")
    equal(catalog_core.get("current_verified_record_id"), record_id, "catalog.current_record_id")
    equal(catalog_core.get("current_repository_arweave_publication_status"), "deferred_by_owner", "catalog.current_arweave_status")
    return True


def main() -> int:
    catalog = load(CATALOG)
    v4 = load(V4_AUTH)
    equal(v4.get("status"), "consumed", "v4.authorization.status")
    core = catalog.get("core_repository")
    require(isinstance(core, dict), "catalog.core_repository missing")

    validate_historical_checkpoint(core, v4)
    advanced = validate_later_current_pointer(core, v4)

    # Run the original validator unchanged against a temporary historical view.
    # Only the generic moving repository pointer is projected back to checkpoint v4;
    # every actual historical file, digest, proof topology and generated inventory is
    # still validated by the original implementation. The real moving pointer was
    # independently fail-closed above before this projection is created.
    projected = copy.deepcopy(catalog)
    projected_core = projected["core_repository"]
    projected_core["current_verified_version_doi"] = v4["published_doi"]
    projected_core["current_verified_source_git_commit_sha"] = v4["published_source_baseline_commit_sha"]
    projected_core["current_verified_package_identity_sha256"] = v4["published_package_identity_sha256"]
    projected_core["current_verified_record_id"] = v4["published_record_id"]

    legacy = load_legacy_module()
    with tempfile.TemporaryDirectory(prefix="trinity-v4-history-") as temp_dir:
        historical_catalog = Path(temp_dir) / "recovery-catalog-v4-historical.json"
        historical_catalog.write_text(json.dumps(projected, indent=2) + "\n", encoding="utf-8")
        legacy.RECOVERY_CATALOG = historical_catalog
        legacy.validate()

    if advanced:
        print(
            "Historical checkpoint v4 PASS; current repository pointer advancement PASS "
            f"({v4['published_doi']} -> {core['current_verified_version_doi']})."
        )
    else:
        print(f"Historical checkpoint v4 PASS; repository pointer remains at {v4['published_doi']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
