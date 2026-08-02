#!/usr/bin/env python3
"""Prepare, verify and seal the self-describing repository DOI refresh."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from preservation_capsule import (
    PACKAGE_TITLE,
    PUBLISHED_FILE_NAMES,
    ZENODO_LICENSE_ID,
    file_inventory,
    verify_local_package,
)


ROOT = Path(__file__).resolve().parents[1]
AUTH_PATH = ROOT / "preservation/repository-preservation-refresh-authorization.json"
CATALOG_PATH = ROOT / "preservation/recovery-catalog.json"
STATE_PATH = ROOT / "preservation/repository-preservation-state-v2.json"
OBSERVATION_PATH = ROOT / "preservation/repository-preservation-observation.json"
PREPARED_PATH = ROOT / "preservation/repository-preservation-refresh-prepared.json"
INDEX_PATH = ROOT / "api/recovery-index.json"
RECOVERY_GUIDE = ROOT / "RECOVERY.md"
ANNEX_GUIDE = ROOT / "preservation/EXTERNAL-BINARY-ANNEX.md"

AUTH_SCHEMA = "trinityaccord.repository-preservation-refresh-authorization.v1"
CATALOG_SCHEMA = "trinityaccord.repository-recovery-catalog.v1"
STATE_SCHEMA = "trinityaccord.repository-preservation-zenodo-state.v2"
EXPECTED_CONCEPT_DOI = "10.5281/zenodo.21739343"
EXPECTED_PREVIOUS_DOI = "10.5281/zenodo.21755655"
EXPECTED_ANNEX_DOIS = {
    "evidence": "10.5281/zenodo.21753937",
    "nft": "10.5281/zenodo.21754229",
}
EXPECTED_RIGHTS_ACK = "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
EXPECTED_CONFIRMATION = "PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V3"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DOI_RE = re.compile(r"^10\.5281/zenodo\.([0-9]+)$")

BASELINE_BLOCK = """<!-- BEGIN REPOSITORY PRESERVATION BASELINE RULE -->
**Published-baseline rule:** A repository capsule restores the exact Git-tracked
publication baseline named by its manifest. It is not a live mirror and must not be
described as byte-identical to a later moving GitHub `main` without an explicit
freshness comparison.

**Stable recovery catalog:** `preservation/recovery-catalog.json` is embedded in the
core source tree. It identifies the core concept DOI and both external-annex version
DOIs, so complete DOI discovery does not depend on GitHub, maintainer memory, or a
post-publication state commit.
<!-- END REPOSITORY PRESERVATION BASELINE RULE -->
"""

ANNEX_BLOCK = """<!-- BEGIN CORE DOI BASELINE RULE -->
The core concept DOI `10.5281/zenodo.21739343` resolves the latest published core
repository version. Each version restores the exact source commit named in its
manifest; no version is a live mirror of a later moving GitHub `main`. The embedded
`preservation/recovery-catalog.json` supplies both annex DOI identifiers without
requiring GitHub.
<!-- END CORE DOI BASELINE RULE -->
"""


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise SystemExit(f"duplicate JSON key {key!r}: {path}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON number {token}")
            ),
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise SystemExit(f"invalid strict JSON: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


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


def validate_catalog() -> dict[str, Any]:
    catalog = strict_json(CATALOG_PATH)
    if catalog.get("schema") != CATALOG_SCHEMA:
        raise SystemExit("unsupported repository recovery catalog schema")
    core = catalog.get("core_repository")
    if not isinstance(core, dict) or core.get("concept_doi") != EXPECTED_CONCEPT_DOI:
        raise SystemExit("recovery catalog core concept DOI mismatch")
    if core.get("resolution_rule") != (
        "Resolve the concept DOI and select its latest published version."
    ):
        raise SystemExit("recovery catalog lacks an exact latest-version resolution rule")
    annexes = catalog.get("external_binary_annexes")
    if not isinstance(annexes, dict):
        raise SystemExit("recovery catalog annex map is missing")
    for name, expected_doi in EXPECTED_ANNEX_DOIS.items():
        entry = annexes.get(name)
        if not isinstance(entry, dict) or entry.get("doi") != expected_doi:
            raise SystemExit(f"recovery catalog {name} DOI mismatch")
    if catalog.get("github_required_for_discovery") is not False:
        raise SystemExit("recovery catalog must not require GitHub for discovery")
    if catalog.get("github_required_for_recovery") is not False:
        raise SystemExit("recovery catalog must not require GitHub for recovery")
    return catalog


def validate_authorization() -> dict[str, Any]:
    auth = strict_json(AUTH_PATH)
    if auth.get("schema") != AUTH_SCHEMA or auth.get("sequence") != 3:
        raise SystemExit("unsupported repository preservation refresh authorization")
    if auth.get("authorized_by") != "thechurchofagi":
        raise SystemExit("repository preservation refresh is not owner-authorized")
    if auth.get("core_concept_doi") != EXPECTED_CONCEPT_DOI:
        raise SystemExit("authorization core concept DOI mismatch")
    if auth.get("previous_core_version_doi") != EXPECTED_PREVIOUS_DOI:
        raise SystemExit("authorization previous core DOI mismatch")
    if auth.get("external_annex_dois") != EXPECTED_ANNEX_DOIS:
        raise SystemExit("authorization external annex DOI mismatch")
    if auth.get("rights_boundary_acknowledgement") != EXPECTED_RIGHTS_ACK:
        raise SystemExit("authorization rights acknowledgement mismatch")
    if auth.get("publication_confirmation") != EXPECTED_CONFIRMATION:
        raise SystemExit("authorization publication confirmation mismatch")
    if auth.get("live_main_equivalence_claimed") is not False:
        raise SystemExit("authorization must not claim live-main equivalence")
    if auth.get("status") not in {"pending", "prepared", "consumed"}:
        raise SystemExit("authorization status is invalid")
    return auth


def insert_block(text: str, block: str, anchor: str) -> str:
    begin = block.splitlines()[0]
    if begin in text:
        return text
    if anchor not in text:
        raise SystemExit(f"documentation insertion anchor is missing: {anchor!r}")
    return text.replace(anchor, anchor + "\n\n" + block.rstrip(), 1)


def replace_if_present(text: str, old: str, new: str) -> str:
    if old in text:
        return text.replace(old, new)
    if new in text:
        return text
    return text


def patch_recovery_guide() -> None:
    text = RECOVERY_GUIDE.read_text(encoding="utf-8")
    text = insert_block(
        text,
        BASELINE_BLOCK,
        "**Scope:** Recovery of repository-maintained state. This guide does not prove philosophical claims, investment value, religious authority, or independent attestation.",
    )
    text = replace_if_present(
        text,
        "The Repository Preservation Capsule is the GitHub-independent bootstrap for the\ncomplete Git-tracked repository.",
        "The Repository Preservation Capsule is the GitHub-independent bootstrap for the\nexact published Git-tracked repository baseline identified by its manifest.",
    )
    text = replace_if_present(
        text,
        "- `trinity-accord-source.tar.gz` — exact current source tree;",
        "- `trinity-accord-source.tar.gz` — exact source tree for the declared publication baseline;",
    )
    text = replace_if_present(
        text,
        "- This is a complete recovery of every byte and executable mode in the current\n  Git-tracked production tree.",
        "- This is a complete recovery of every byte and executable mode in the capsule's\n  declared Git-tracked publication baseline. Compare its source commit with any later\n  GitHub `main` before calling it current.",
    )
    RECOVERY_GUIDE.write_text(text, encoding="utf-8")


def patch_annex_guide() -> None:
    text = ANNEX_GUIDE.read_text(encoding="utf-8")
    text = insert_block(
        text,
        ANNEX_BLOCK,
        "# Trinity Accord External Binary Annexes",
    )
    text = replace_if_present(
        text,
        "The core repository preservation DOI (`10.5281/zenodo.21739344`) remains unchanged and continues to restore the complete Git-tracked repository.",
        "Core version DOI `10.5281/zenodo.21739344` restores the historical baseline at commit `484bdd7a85694ad53fe7e6e9dcea94d0dee5617e`; use concept DOI `10.5281/zenodo.21739343` to resolve the latest published core version.",
    )
    ANNEX_GUIDE.write_text(text, encoding="utf-8")


def baseline_tree_limitation() -> str:
    return (
        "The core repository capsule embeds every Git-tracked byte in the exact "
        "publication baseline named by its manifest, while deliberately excluding "
        "production parent-history and tag objects so historical credentials are not "
        "republished; source commit/tag identities remain manifest metadata."
    )


def baseline_tree_limitation() -> str:
    return (
        "The core repository capsule embeds every Git-tracked byte in the exact "
        "publication baseline named by its manifest, while deliberately excluding "
        "production parent-history and tag objects so historical credentials are not "
        "republished; source commit/tag identities remain manifest metadata."
    )


def qualified_limitation() -> str:
    return (
        "The core repository capsule and the separately published evidence and Chronicle "
        "NFT binary annex DOI records together preserve the exact Git-tracked publication "
        "baseline named by the core manifest and every custom asset; this does not "
        "assert byte equality with a later moving GitHub main."
    )


def normalize_limitations(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit("recovery index limitations are invalid")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("recovery index limitation is not a string")
        if item == (
            "The core repository capsule embeds every current Git-tracked byte but "
            "deliberately excludes production parent-history and tag objects so historical "
            "credentials are not republished; source commit/tag identities remain manifest "
            "metadata."
        ):
            item = baseline_tree_limitation()
        if (
            "together preserve the current Git-tracked repository" in item
            or item == qualified_limitation()
        ):
            continue
        if item not in normalized:
            normalized.append(item)
    tree = baseline_tree_limitation()
    if tree not in normalized:
        normalized.append(tree)
    normalized.append(qualified_limitation())
    return normalized


def normalize_limitations(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit("recovery index limitations are invalid")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("recovery index limitation is not a string")
        if item == (
            "The core repository capsule embeds every current Git-tracked byte but "
            "deliberately excludes production parent-history and tag objects so historical "
            "credentials are not republished; source commit/tag identities remain manifest "
            "metadata."
        ):
            item = baseline_tree_limitation()
        if (
            "together preserve the current Git-tracked repository" in item
            or item == qualified_limitation()
        ):
            continue
        if item not in normalized:
            normalized.append(item)
    tree = baseline_tree_limitation()
    if tree not in normalized:
        normalized.append(tree)
    normalized.append(qualified_limitation())
    return normalized


def prepare_index(base_commit: str) -> None:
    index = strict_json(INDEX_PATH)
    entrypoints = index.setdefault("recovery_entrypoints", {})
    if not isinstance(entrypoints, dict):
        raise SystemExit("recovery index entrypoints are invalid")
    entrypoints["repository_preservation_catalog"] = (
        "preservation/recovery-catalog.json"
    )
    entrypoints["repository_preservation_current_state"] = (
        "preservation/repository-preservation-state-v2.json"
    )
    mirror_classes = index.setdefault("mirror_classes", {})
    if not isinstance(mirror_classes, dict):
        raise SystemExit("recovery index mirror classes are invalid")
    mirror_classes["repository_preservation_zenodo"] = (
        "verified exact eight-file publication-baseline capsule with embedded stable "
        "recovery catalog, source/safe-snapshot cross-check and public DOI-only restore"
    )
    trusted = index.setdefault("latest_trusted_release", {})
    if not isinstance(trusted, dict):
        raise SystemExit("recovery index latest trusted release is invalid")
    repository = trusted.setdefault("repository_preservation", {})
    if not isinstance(repository, dict):
        raise SystemExit("recovery index repository preservation entry is invalid")
    repository["concept_doi"] = EXPECTED_CONCEPT_DOI
    repository["coverage_status"] = "publication_baseline_refresh_prepared"
    repository["live_main_equivalence_claimed"] = False
    repository["recovery_catalog"] = "preservation/recovery-catalog.json"
    index["publication_refresh"] = {
        "schema": AUTH_SCHEMA,
        "sequence": 3,
        "status": "prepared_for_new_core_version",
        "authorized_base_commit_sha": base_commit,
        "core_concept_doi": EXPECTED_CONCEPT_DOI,
        "external_annex_dois": EXPECTED_ANNEX_DOIS,
    }
    limitations = index.setdefault("limitations", [])
    if not isinstance(limitations, list):
        raise SystemExit("recovery index limitations are invalid")
    index["limitations"] = normalize_limitations(limitations)
    index["source_digest"] = canonical_index_digest(index)
    write_json(INDEX_PATH, index)


def prepare(base_commit: str) -> None:
    if COMMIT_RE.fullmatch(base_commit) is None:
        raise SystemExit("prepare requires an exact 40-character base commit")
    validate_catalog()
    auth = validate_authorization()
    if auth["status"] == "consumed":
        return
    patch_recovery_guide()
    patch_annex_guide()
    prepare_index(base_commit)
    state = strict_json(STATE_PATH)
    state.update(
        {
            "schema": STATE_SCHEMA,
            "publication_status": "prepared_for_publication",
            "prepared_base_commit_sha": base_commit,
            "core_concept_doi": EXPECTED_CONCEPT_DOI,
            "self_describing_recovery_catalog": (
                "preservation/recovery-catalog.json"
            ),
            "external_binary_annexes": EXPECTED_ANNEX_DOIS,
            "live_main_equivalence_claimed": False,
        }
    )
    write_json(STATE_PATH, state)
    auth["status"] = "prepared"
    auth["prepared_base_commit_sha"] = base_commit
    write_json(AUTH_PATH, auth)
    write_json(
        PREPARED_PATH,
        {
            "schema": "trinityaccord.repository-preservation-refresh-prepared.v1",
            "sequence": 3,
            "status": "prepared",
            "base_commit_sha": base_commit,
            "core_concept_doi": EXPECTED_CONCEPT_DOI,
            "recovery_catalog": "preservation/recovery-catalog.json",
        },
    )
    validate()


def public_file_items(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = record.get("files")
    items: list[Any]
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict) and isinstance(raw.get("entries"), list):
        items = raw["entries"]
    else:
        raise SystemExit("public Zenodo record files are missing")
    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("key") or item.get("filename") or "")
        if not name or name in result:
            raise SystemExit("public Zenodo record contains invalid duplicate file names")
        result[name] = item
    return result


def record_doi(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    pids = record.get("pids") if isinstance(record.get("pids"), dict) else {}
    doi_pid = pids.get("doi") if isinstance(pids.get("doi"), dict) else {}
    return str(record.get("doi") or metadata.get("doi") or doi_pid.get("identifier") or "")


def record_concept_doi(record: dict[str, Any]) -> str:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    parent = record.get("parent") if isinstance(record.get("parent"), dict) else {}
    pids = parent.get("pids") if isinstance(parent.get("pids"), dict) else {}
    doi_pid = pids.get("doi") if isinstance(pids.get("doi"), dict) else {}
    return str(
        record.get("conceptdoi")
        or metadata.get("conceptdoi")
        or doi_pid.get("identifier")
        or ""
    )


def normalized_license(record: dict[str, Any]) -> set[str]:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    values: set[str] = set()
    for source in (record.get("license"), metadata.get("license")):
        if isinstance(source, str):
            values.add(source)
        elif isinstance(source, dict):
            values.add(str(source.get("id") or source.get("identifier") or ""))
    rights = metadata.get("rights")
    if isinstance(rights, list):
        for item in rights:
            if isinstance(item, str):
                values.add(item)
            elif isinstance(item, dict):
                values.add(str(item.get("id") or item.get("identifier") or ""))
    return {item for item in values if item}


def verify_public(record_id: int, capsule_dir: Path, output: Path) -> None:
    package = verify_local_package(capsule_dir)
    url = f"https://zenodo.org/api/records/{record_id}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "trinity-preservation-refresh/2"},
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            record = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SystemExit(f"public Zenodo metadata verification failed: {exc}") from exc
    if not isinstance(record, dict):
        raise SystemExit("public Zenodo record is not an object")
    doi = record_doi(record)
    if DOI_RE.fullmatch(doi) is None or int(DOI_RE.fullmatch(doi).group(1)) != record_id:
        raise SystemExit("public Zenodo version DOI/record mismatch")
    if record_concept_doi(record) != EXPECTED_CONCEPT_DOI:
        raise SystemExit("public Zenodo concept DOI mismatch")
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    if metadata.get("title") != PACKAGE_TITLE:
        raise SystemExit("public Zenodo title mismatch")
    if metadata.get("version") != package["capsule_id"]:
        raise SystemExit("public Zenodo capsule version mismatch")
    if ZENODO_LICENSE_ID not in normalized_license(record):
        raise SystemExit("public Zenodo rights identifier mismatch")
    access = record.get("access") if isinstance(record.get("access"), dict) else {}
    if not (
        metadata.get("access_right") == "open"
        or access.get("record") == "public"
        or access.get("files") == "public"
    ):
        raise SystemExit("public Zenodo access is not open for preservation recovery")
    remote = public_file_items(record)
    if set(remote) != set(PUBLISHED_FILE_NAMES):
        raise SystemExit("public Zenodo file set mismatch")
    local = file_inventory(capsule_dir)
    for name in PUBLISHED_FILE_NAMES:
        item = remote[name]
        size = item.get("size", item.get("filesize"))
        try:
            observed_size = int(size)
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"public Zenodo file size is invalid: {name}") from exc
        if observed_size != local[name]["bytes"]:
            raise SystemExit(f"public Zenodo file size mismatch: {name}")
        checksum = item.get("checksum")
        if isinstance(checksum, str) and checksum:
            algorithm, _, value = checksum.partition(":")
            if algorithm == "md5" and value.lower() != local[name]["md5"]:
                raise SystemExit(f"public Zenodo MD5 mismatch: {name}")
            if algorithm == "sha256" and value.lower() != local[name]["sha256"]:
                raise SystemExit(f"public Zenodo SHA-256 mismatch: {name}")
    write_json(
        output,
        {
            "schema": "trinityaccord.repository-preservation-public-metadata-report.v1",
            "status": "passed",
            "record_id": record_id,
            "doi": doi,
            "concept_doi": EXPECTED_CONCEPT_DOI,
            "capsule_id": package["capsule_id"],
            "git_commit_sha": package["git_commit_sha"],
            "package_identity_sha256": package["package_identity_sha256"],
            "public_file_set_verification": "passed",
            "public_file_metadata_verification": "passed",
            "public_rights_verification": "passed",
            "observed_without_zenodo_credentials": True,
        },
    )


def seal(source_commit: str, recovery_report_path: Path, metadata_report_path: Path) -> None:
    if COMMIT_RE.fullmatch(source_commit) is None:
        raise SystemExit("seal requires an exact 40-character source commit")
    catalog = validate_catalog()
    auth = validate_authorization()
    state = strict_json(STATE_PATH)
    recovery = strict_json(recovery_report_path)
    metadata_report = strict_json(metadata_report_path)
    if state.get("publication_status") != "published":
        raise SystemExit("publisher state is not published")
    if state.get("latest_git_commit_sha") != source_commit:
        raise SystemExit("published repository source commit mismatch")
    if state.get("concept_doi") != EXPECTED_CONCEPT_DOI:
        raise SystemExit("published repository concept DOI mismatch")
    recovery_status = str(recovery.get("repository_recovery_status") or "")
    if not recovery_status.startswith("full"):
        raise SystemExit("public DOI restore did not produce full repository recovery")
    if recovery.get("source_git_commit_sha") != source_commit:
        raise SystemExit("public DOI restore source commit mismatch")
    if metadata_report.get("status") != "passed":
        raise SystemExit("public Zenodo metadata verification did not pass")
    if metadata_report.get("git_commit_sha") != source_commit:
        raise SystemExit("public metadata report source commit mismatch")
    if metadata_report.get("doi") != state.get("latest_doi"):
        raise SystemExit("public metadata report DOI mismatch")

    state.update(
        {
            "schema": STATE_SCHEMA,
            "publication_status": "published_and_publicly_restored",
            "source_baseline_commit_sha": source_commit,
            "core_concept_doi": EXPECTED_CONCEPT_DOI,
            "self_describing_recovery_catalog": (
                "preservation/recovery-catalog.json"
            ),
            "external_binary_annexes": EXPECTED_ANNEX_DOIS,
            "public_download_verification": "passed",
            "public_metadata_verification": "passed",
            "public_cold_restore": "passed",
            "public_cold_restore_report": recovery,
            "public_metadata_report": metadata_report,
            "github_required_for_discovery": False,
            "github_required_for_repository_recovery": False,
            "live_main_equivalence_claimed": False,
            "coverage_scope": (
                "exact Git-tracked publication baseline named by latest_git_commit_sha"
            ),
            "previous_verified_version": {
                "doi": EXPECTED_PREVIOUS_DOI,
                "record_id": 21755655,
                "git_commit_sha": "5368fd1ecce2ee2f5a4160d6b7892e8c28314a4b",
            },
        }
    )
    write_json(STATE_PATH, state)

    observation = {
        "schema": "trinityaccord.repository-preservation-public-observation.v2",
        "publication_status": state["publication_status"],
        "observed_without_github_credentials": True,
        "observed_without_zenodo_credentials": True,
        "record_id": state["latest_record_id"],
        "doi": state["latest_doi"],
        "doi_url": state["latest_doi_url"],
        "concept_doi": EXPECTED_CONCEPT_DOI,
        "capsule_id": state["latest_capsule_id"],
        "source_baseline_commit_sha": source_commit,
        "git_tree_oid": state["latest_git_tree_oid"],
        "package_identity_sha256": state["latest_package_identity_sha256"],
        "self_describing_recovery_catalog": state[
            "self_describing_recovery_catalog"
        ],
        "external_binary_annexes": catalog["external_binary_annexes"],
        "public_download_verification": "passed",
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "public_cold_restore_report": recovery,
        "public_metadata_report": metadata_report,
        "live_main_equivalence_claimed": False,
    }
    write_json(OBSERVATION_PATH, observation)

    index = strict_json(INDEX_PATH)
    entrypoints = index.setdefault("recovery_entrypoints", {})
    entrypoints["repository_preservation_catalog"] = (
        "preservation/recovery-catalog.json"
    )
    entrypoints["repository_preservation_current_state"] = (
        "preservation/repository-preservation-state-v2.json"
    )
    trusted = index.setdefault("latest_trusted_release", {})
    trusted["status"] = "published_and_publicly_restored"
    trusted["repository_preservation"] = {
        "doi": state["latest_doi"],
        "record_id": state["latest_record_id"],
        "concept_doi": EXPECTED_CONCEPT_DOI,
        "git_commit_sha": source_commit,
        "git_tree_oid": state["latest_git_tree_oid"],
        "package_identity_sha256": state["latest_package_identity_sha256"],
        "github_required_for_recovery": False,
        "github_required_for_discovery": False,
        "public_metadata_verification": "passed",
        "public_cold_restore": "passed",
        "coverage_status": "exact_published_baseline",
        "live_main_equivalence_claimed": False,
        "recovery_catalog": "preservation/recovery-catalog.json",
        "current_state": "preservation/repository-preservation-state-v2.json",
    }
    index["publication_refresh"] = {
        "schema": AUTH_SCHEMA,
        "sequence": 3,
        "status": "published_and_publicly_restored",
        "source_baseline_commit_sha": source_commit,
        "doi": state["latest_doi"],
        "record_id": state["latest_record_id"],
        "concept_doi": EXPECTED_CONCEPT_DOI,
        "external_annex_dois": EXPECTED_ANNEX_DOIS,
    }
    limitations = index.setdefault("limitations", [])
    index["limitations"] = normalize_limitations(limitations)
    index["source_digest"] = canonical_index_digest(index)
    write_json(INDEX_PATH, index)

    auth["status"] = "consumed"
    auth["published_source_baseline_commit_sha"] = source_commit
    auth["published_record_id"] = state["latest_record_id"]
    auth["published_doi"] = state["latest_doi"]
    auth["published_package_identity_sha256"] = state[
        "latest_package_identity_sha256"
    ]
    write_json(AUTH_PATH, auth)
    prepared = strict_json(PREPARED_PATH)
    prepared["status"] = "consumed"
    prepared["source_baseline_commit_sha"] = source_commit
    prepared["published_doi"] = state["latest_doi"]
    write_json(PREPARED_PATH, prepared)
    validate()


def validate() -> None:
    validate_catalog()
    auth = validate_authorization()
    state = strict_json(STATE_PATH)
    if state.get("core_concept_doi") != EXPECTED_CONCEPT_DOI:
        raise SystemExit("current repository preservation state concept DOI mismatch")
    if state.get("external_binary_annexes") != EXPECTED_ANNEX_DOIS:
        raise SystemExit("current repository preservation state annex DOI mismatch")
    if state.get("live_main_equivalence_claimed") is not False:
        raise SystemExit("current repository preservation state overclaims live main")
    if auth["status"] in {"prepared", "consumed"}:
        recovery_text = RECOVERY_GUIDE.read_text(encoding="utf-8")
        annex_text = ANNEX_GUIDE.read_text(encoding="utf-8")
        if "BEGIN REPOSITORY PRESERVATION BASELINE RULE" not in recovery_text:
            raise SystemExit("recovery guide lacks the publication-baseline rule")
        if "exact current source tree" in recovery_text:
            raise SystemExit("recovery guide still overclaims an exact current source tree")
        if "BEGIN CORE DOI BASELINE RULE" not in annex_text:
            raise SystemExit("annex guide lacks the core DOI baseline rule")
        index = strict_json(INDEX_PATH)
        entrypoints = index.get("recovery_entrypoints")
        if not isinstance(entrypoints, dict):
            raise SystemExit("recovery index entrypoints are missing")
        if entrypoints.get("repository_preservation_catalog") != (
            "preservation/recovery-catalog.json"
        ):
            raise SystemExit("recovery index does not expose the stable catalog")
        if entrypoints.get("repository_preservation_current_state") != (
            "preservation/repository-preservation-state-v2.json"
        ):
            raise SystemExit("recovery index does not expose the current v2 state")
        if index.get("source_digest") != canonical_index_digest(index):
            raise SystemExit("recovery index source digest mismatch")
        limitations = index.get("limitations")
        if limitations != normalize_limitations(limitations):
            raise SystemExit("recovery index limitations are stale or duplicated")
        limitations = index.get("limitations")
        if limitations != normalize_limitations(limitations):
            raise SystemExit("recovery index limitations are stale or duplicated")
    if auth["status"] == "consumed":
        if state.get("publication_status") != "published_and_publicly_restored":
            raise SystemExit("consumed refresh lacks final published state")
        if state.get("public_metadata_verification") != "passed":
            raise SystemExit("consumed refresh lacks public metadata verification")
        if state.get("public_cold_restore") != "passed":
            raise SystemExit("consumed refresh lacks public cold restore")
        if not OBSERVATION_PATH.is_file():
            raise SystemExit("consumed refresh lacks public observation")


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate")
    prepare_parser = subparsers.add_parser("prepare")
    prepare_parser.add_argument("--base-commit", required=True)
    verify_parser = subparsers.add_parser("verify-public")
    verify_parser.add_argument("--record-id", required=True, type=int)
    verify_parser.add_argument("--capsule-dir", required=True)
    verify_parser.add_argument("--output", required=True)
    seal_parser = subparsers.add_parser("seal")
    seal_parser.add_argument("--source-commit", required=True)
    seal_parser.add_argument("--recovery-report", required=True)
    seal_parser.add_argument("--metadata-report", required=True)
    args = parser.parse_args()
    if args.command == "validate":
        validate()
    elif args.command == "prepare":
        prepare(args.base_commit)
    elif args.command == "verify-public":
        verify_public(
            args.record_id,
            Path(args.capsule_dir).resolve(),
            Path(args.output).resolve(),
        )
    elif args.command == "seal":
        seal(
            args.source_commit,
            Path(args.recovery_report).resolve(),
            Path(args.metadata_report).resolve(),
        )
    else:
        raise SystemExit("unsupported command")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
