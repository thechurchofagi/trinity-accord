#!/usr/bin/env python3
"""Migrate repository preservation from moving-main wording to exact baseline semantics.

The migration is intentionally idempotent. It reauthorizes sequence 3 only from the
fully consumed sequence-2 state. Prepared or consumed sequence-3 states are left
untouched so retries remain bound to one immutable source baseline.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/repository-preservation-refresh-authorization.json"
STATE = ROOT / "preservation/repository-preservation-state-v2.json"
PREPARED = ROOT / "preservation/repository-preservation-refresh-prepared.json"
CATALOG = ROOT / "preservation/recovery-catalog.json"
INDEX = ROOT / "api/recovery-index.json"
RECOVERY = ROOT / "RECOVERY.md"
BUILD = ROOT / "scripts/build_preservation_capsule.py"
VERIFY = ROOT / "scripts/preservation_capsule.py"
RESTORE = ROOT / "scripts/restore_preservation_capsule.py"
REFRESH = ROOT / "scripts/repository_preservation_refresh.py"
CAPSULE_TEST = ROOT / "tests/test_preservation_capsule.py"
REFRESH_TEST = ROOT / "tests/test_repository_preservation_refresh_contract.py"

PREVIOUS_DOI = "10.5281/zenodo.21755655"
PREVIOUS_RECORD_ID = 21755655
PREVIOUS_SOURCE_SHA = "5368fd1ecce2ee2f5a4160d6b7892e8c28314a4b"
CONCEPT_DOI = "10.5281/zenodo.21739343"
ANNEX_DOIS = {
    "evidence": "10.5281/zenodo.21753937",
    "nft": "10.5281/zenodo.21754229",
}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise SystemExit(f"semantic migration anchor missing in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


def canonical_index_digest(value: dict[str, Any]) -> str:
    canonical = dict(value)
    canonical.pop("source_digest", None)
    raw = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def migrate_json_state() -> None:
    auth = read_json(AUTH)
    sequence = auth.get("sequence")
    status = auth.get("status")
    if sequence == 3:
        if status not in {"pending", "prepared", "consumed"}:
            raise SystemExit("sequence-3 authorization has invalid status")
        return
    if sequence != 2 or status != "consumed":
        raise SystemExit(
            "semantic v3 migration requires the fully consumed sequence-2 state"
        )

    write_json(
        AUTH,
        {
            "schema": "trinityaccord.repository-preservation-refresh-authorization.v1",
            "sequence": 3,
            "status": "pending",
            "authorized_by": "thechurchofagi",
            "authorized_purpose": (
                "Publish a final self-describing core repository version whose metadata, "
                "manifest, recovery report and discovery entrypoints consistently describe "
                "an exact immutable publication baseline rather than a moving GitHub main."
            ),
            "previous_core_version_doi": PREVIOUS_DOI,
            "core_concept_doi": CONCEPT_DOI,
            "external_annex_dois": ANNEX_DOIS,
            "publication_confirmation": "PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V3",
            "rights_boundary_acknowledgement": (
                "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
            ),
            "non_amending_boundary": True,
            "live_main_equivalence_claimed": False,
        },
    )
    write_json(
        STATE,
        {
            "schema": "trinityaccord.repository-preservation-zenodo-state.v2",
            "publication_status": "semantic_refresh_authorized",
            "rights_boundary_schema": "trinityaccord.repository-preservation-rights.v1",
            "core_concept_doi": CONCEPT_DOI,
            "previous_verified_version": {
                "doi": PREVIOUS_DOI,
                "record_id": PREVIOUS_RECORD_ID,
                "git_commit_sha": PREVIOUS_SOURCE_SHA,
            },
            "self_describing_recovery_catalog": "preservation/recovery-catalog.json",
            "external_binary_annexes": ANNEX_DOIS,
            "live_main_equivalence_claimed": False,
            "github_required_for_discovery": False,
            "github_required_for_repository_recovery": False,
            "external_large_binary_annex_embedded": False,
            "versions": [],
        },
    )
    if PREPARED.exists():
        PREPARED.unlink()

    catalog = read_json(CATALOG)
    core = catalog.get("core_repository")
    if not isinstance(core, dict):
        raise SystemExit("recovery catalog core entry is missing")
    core["previous_verified_version_doi"] = PREVIOUS_DOI
    core["coverage_rule"] = (
        "Each version restores the exact immutable Git-tracked publication baseline named "
        "in its manifest; no version claims byte equality with a later moving GitHub main."
    )
    catalog["core_repository"] = core
    write_json(CATALOG, catalog)

    index = read_json(INDEX)
    entrypoints = index.get("recovery_entrypoints")
    if not isinstance(entrypoints, dict):
        raise SystemExit("recovery index entrypoints are missing")
    entrypoints["repository_preservation_state"] = (
        "preservation/repository-preservation-state-v2.json"
    )
    entrypoints["repository_preservation_legacy_state"] = (
        "preservation/zenodo-state.json"
    )
    index["recovery_entrypoints"] = entrypoints
    repository = index.get("latest_trusted_release", {}).get(
        "repository_preservation"
    )
    if not isinstance(repository, dict):
        raise SystemExit("recovery index repository preservation state is missing")
    repository["coverage_status"] = "exact_published_baseline_semantic_refresh_authorized"
    repository["live_main_equivalence_claimed"] = False
    index["publication_refresh"] = {
        "schema": "trinityaccord.repository-preservation-refresh-authorization.v1",
        "sequence": 3,
        "status": "semantic_refresh_authorized",
        "previous_verified_version_doi": PREVIOUS_DOI,
        "core_concept_doi": CONCEPT_DOI,
        "external_annex_dois": ANNEX_DOIS,
    }
    index["source_digest"] = canonical_index_digest(index)
    write_json(INDEX, index)


def migrate_recovery_guide() -> None:
    replace_exact(
        RECOVERY,
        "Check `preservation/zenodo-state.json` from any known copy or query Zenodo for the\n"
        "title `Trinity Accord Repository Preservation Capsule`. A published version contains:",
        "Use `preservation/repository-preservation-state-v2.json` as the current machine\n"
        "state and `preservation/recovery-catalog.json` as the stable DOI discovery entrypoint.\n"
        "The older `preservation/zenodo-state.json` is retained only as historical v1\n"
        "compatibility. A published version contains:",
    )
    replace_exact(
        RECOVERY,
        "  the exact current production tree;",
        "  the exact declared publication-baseline tree;",
    )


def migrate_builder() -> None:
    replace_exact(
        BUILD,
        "recovery bundle for the exact current production tree, allowing every current "
        "Git-tracked byte to be restored without GitHub.",
        "recovery bundle for the exact immutable publication-baseline tree, allowing every "
        "Git-tracked byte in that baseline to be restored without GitHub.",
    )
    replace_exact(
        BUILD,
        '"This core capsule embeds every Git-tracked byte. Large external evidence and\\n"',
        '"This core capsule embeds every Git-tracked byte in the declared publication\\n"\n'
        '        "baseline. Large external evidence and NFT payload bytes are not duplicated\\n"',
    )
    replace_exact(
        BUILD,
        '"NFT payload bytes are not duplicated here; their TXIDs, hashes, manifests, and\\n"\n'
        '        "recovery tools are embedded in the repository. A separate mixed-rights binary\\n"',
        '"here; their TXIDs, hashes, manifests, and recovery tools are embedded in the\\n"\n'
        '        "repository. A separate mixed-rights binary\\n"',
    )
    replace_exact(
        BUILD,
        "The exact current tree is preserved through a synthetic root ",
        "The exact declared publication-baseline tree is preserved through a synthetic root ",
    )
    replace_exact(
        BUILD,
        '"exact_current_production_tree_embedded": True,',
        '"exact_publication_baseline_tree_embedded": True,\n'
        '            "live_main_equivalence_claimed": False,',
    )
    replace_exact(
        BUILD,
        '"zenodo_only_restores_complete_git_tracked_repository": True,',
        '"zenodo_only_restores_complete_git_tracked_repository": True,\n'
        '            "coverage_scope": "exact_immutable_publication_baseline",',
    )


def migrate_verifiers() -> None:
    old = '''    if (
        scope.get("github_required_for_repository_recovery") is not False
        or scope.get("git_tracked_repository_embedded") is not True
        or scope.get("main_history_and_tags_embedded") is not False
        or scope.get("exact_current_production_tree_embedded") is not True
        or scope.get("cloneable_single_root_recovery_bundle_embedded") is not True
        or scope.get("external_large_binary_annex_embedded") is not False
    ):
        raise SystemExit("preservation capsule recovery scope is inconsistent")
'''
    new = '''    baseline_tree = scope.get("exact_publication_baseline_tree_embedded")
    legacy_current_tree = scope.get("exact_current_production_tree_embedded")
    if (
        scope.get("github_required_for_repository_recovery") is not False
        or scope.get("git_tracked_repository_embedded") is not True
        or scope.get("main_history_and_tags_embedded") is not False
        or (baseline_tree is not True and legacy_current_tree is not True)
        or scope.get("cloneable_single_root_recovery_bundle_embedded") is not True
        or scope.get("external_large_binary_annex_embedded") is not False
    ):
        raise SystemExit("preservation capsule recovery scope is inconsistent")
    if baseline_tree is True and scope.get("live_main_equivalence_claimed") is not False:
        raise SystemExit("publication-baseline capsule overclaims live-main equivalence")
'''
    replace_exact(VERIFY, old, new)

    replace_exact(
        RESTORE,
        '''    scope = manifest.get("scope")
    if not isinstance(scope, dict) or scope.get("github_required_for_repository_recovery") is not False:
        raise SystemExit("capsule does not declare GitHub-independent repository recovery")
''',
        '''    scope = manifest.get("scope")
    if not isinstance(scope, dict) or scope.get("github_required_for_repository_recovery") is not False:
        raise SystemExit("capsule does not declare GitHub-independent repository recovery")
    baseline_tree = scope.get("exact_publication_baseline_tree_embedded")
    legacy_current_tree = scope.get("exact_current_production_tree_embedded")
    if baseline_tree is not True and legacy_current_tree is not True:
        raise SystemExit("capsule does not declare an exact recoverable tree")
    if baseline_tree is True and scope.get("live_main_equivalence_claimed") is not False:
        raise SystemExit("publication-baseline capsule overclaims live-main equivalence")
''',
    )
    replace_exact(
        RESTORE,
        '"repository_recovery_status": "full_current_git_tracked_tree",',
        '"repository_recovery_status": "full_exact_publication_baseline",',
    )
    replace_exact(
        RESTORE,
        '"The capsule restores every byte and executable mode in the current Git-tracked production tree.",',
        '"The capsule restores every byte and executable mode in the exact immutable Git-tracked publication baseline named by its manifest.",',
    )
    replace_exact(
        RESTORE,
        '"capsule_is_a_non_authoritative_mirror": True,',
        '"capsule_is_a_non_authoritative_mirror": True,\n'
        '                "live_main_equivalence_claimed": False,',
    )


def migrate_refresh_contract() -> None:
    replace_exact(
        REFRESH,
        'EXPECTED_PREVIOUS_DOI = "10.5281/zenodo.21739344"',
        f'EXPECTED_PREVIOUS_DOI = "{PREVIOUS_DOI}"',
    )
    replace_exact(
        REFRESH,
        'auth.get("sequence") != 2',
        'auth.get("sequence") != 3',
    )
    replace_exact(REFRESH, '"sequence": 2,', '"sequence": 3,')
    replace_exact(
        REFRESH,
        '''            "previous_verified_version": {
                "doi": EXPECTED_PREVIOUS_DOI,
                "record_id": 21739344,
                "git_commit_sha": "484bdd7a85694ad53fe7e6e9dcea94d0dee5617e",
            },''',
        f'''            "previous_verified_version": {{
                "doi": EXPECTED_PREVIOUS_DOI,
                "record_id": {PREVIOUS_RECORD_ID},
                "git_commit_sha": "{PREVIOUS_SOURCE_SHA}",
            }},''',
    )


def migrate_tests() -> None:
    replace_exact(
        CAPSULE_TEST,
        'assert entrypoints["repository_preservation_state"] == "preservation/zenodo-state.json"',
        'assert entrypoints["repository_preservation_state"] == (\n'
        '        "preservation/repository-preservation-state-v2.json"\n'
        '    )\n'
        '    assert entrypoints["repository_preservation_legacy_state"] == (\n'
        '        "preservation/zenodo-state.json"\n'
        '    )',
    )
    replace_exact(
        REFRESH_TEST,
        'assert auth["sequence"] == 2',
        'assert auth["sequence"] == 3',
    )
    replace_exact(
        REFRESH_TEST,
        '"PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V2"',
        '"PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V3"',
    )


def main() -> int:
    migrate_json_state()
    auth = read_json(AUTH)
    if auth.get("sequence") == 3 and auth.get("status") in {"prepared", "consumed"}:
        print("REPOSITORY_PRESERVATION_SEMANTICS_V3_ALREADY_FROZEN")
        return 0
    migrate_recovery_guide()
    migrate_builder()
    migrate_verifiers()
    migrate_refresh_contract()
    migrate_tests()
    print("REPOSITORY_PRESERVATION_SEMANTICS_V3_MIGRATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
