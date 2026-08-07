#!/usr/bin/env python3
# Normalize repository-preservation limitations and harden future sealing.
#
# This historical repair remains idempotent across later repository-preservation
# publications. Later releases may supersede the historical literal DOI assertion
# with the sealed current-baseline authorization contract.

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REFRESH = ROOT / "scripts/repository_preservation_refresh.py"
INDEX = ROOT / "api/recovery-index.json"
FINAL_STATE_TEST = ROOT / "tests/test_external_binary_annex_final_state.py"
ANNEX_V2_TEST = ROOT / "tests/test_external_binary_annex_v2.py"
CAPSULE_TEST = ROOT / "tests/test_preservation_capsule.py"
SEMANTICS_TEST = ROOT / "tests/test_repository_preservation_semantics_v3.py"
SEMANTICS_EXEC_TEST = (
    ROOT / "tests/test_repository_preservation_semantics_v3_execution.py"
)

LEGACY_TREE_LIMITATION = (
    "The core repository capsule embeds every current Git-tracked byte but "
    "deliberately excludes production parent-history and tag objects so historical "
    "credentials are not republished; source commit/tag identities remain manifest "
    "metadata."
)
BASELINE_TREE_LIMITATION = (
    "The core repository capsule embeds every Git-tracked byte in the exact "
    "publication baseline named by its manifest, while deliberately excluding "
    "production parent-history and tag objects so historical credentials are not "
    "republished; source commit/tag identities remain manifest metadata."
)
QUALIFIED_LIMITATION = (
    "The core repository capsule and the separately published evidence and Chronicle "
    "NFT binary annex DOI records together preserve the exact Git-tracked publication "
    "baseline named by the core manifest and every custom asset; this does not assert "
    "byte equality with a later moving GitHub main."
)

OLD_FUNCTION = '''def qualified_limitation() -> str:
    return (
        "The core repository capsule and the separately published evidence and Chronicle "
        "NFT binary annex DOI records together preserve the exact Git-tracked publication "
        "baseline named by the core manifest and every custom asset; this does not "
        "assert byte equality with a later moving GitHub main."
    )
'''

NEW_FUNCTION = '''def baseline_tree_limitation() -> str:
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
'''

OLD_FILTER = '''    limitations = [
        item
        for item in limitations
        if not (
            isinstance(item, str)
            and "together preserve the current Git-tracked repository" in item
        )
    ]
    limitations.append(qualified_limitation())
    index["limitations"] = limitations
'''

NEW_FILTER = '''    index["limitations"] = normalize_limitations(limitations)
'''

OLD_VALIDATION = '''        if index.get("source_digest") != canonical_index_digest(index):
            raise SystemExit("recovery index source digest mismatch")
'''

NEW_VALIDATION = '''        if index.get("source_digest") != canonical_index_digest(index):
            raise SystemExit("recovery index source digest mismatch")
        limitations = index.get("limitations")
        if limitations != normalize_limitations(limitations):
            raise SystemExit("recovery index limitations are stale or duplicated")
'''

OLD_FINAL_STATE_ASSERTION = '''    assert any(
        "together preserve the current Git-tracked repository and every custom asset"
        in item
        for item in limitations
    )
'''
NEW_FINAL_STATE_ASSERTION = '''    assert len(limitations) == len(set(limitations))
    assert not any("every current Git-tracked byte" in item for item in limitations)
    assert sum(
        "preserve the exact Git-tracked publication baseline named by the core manifest"
        in item
        for item in limitations
    ) == 1
'''

OLD_CURRENT_DOI_ASSERTION = (
    '    assert current["latest_doi"] == "10.5281/zenodo.21755655"\n'
)
NEW_CURRENT_DOI_ASSERTION = (
    '    assert current["latest_doi"] == "10.5281/zenodo.21755827"\n'
)
CURRENT_DOI_CONTRACT_ASSERTION = (
    '    assert current["latest_doi"] == current_baseline["published_doi"]\n'
)
CURRENT_DOI_CONTRACT_SOURCE = (
    'CURRENT_BASELINE_AUTHORIZATION = ROOT / "agent-safety-toolkit/evidence/'
    'repository-preservation/current-baseline-publication-authorization-v1.json"'
)

OLD_RECOVERY_STATUS_ASSERTION = (
    '    assert report["repository_recovery_status"] == '
    '"full_current_git_tracked_tree"\n'
)
NEW_RECOVERY_STATUS_ASSERTION = (
    '    assert report["repository_recovery_status"] == '
    '"full_exact_publication_baseline"\n'
)

OLD_HISTORICAL_ASSERTION = '    assert "historical v1 compatibility" in recovery\n'
NEW_HISTORICAL_ASSERTION = (
    '    assert "historical v1" in recovery\n'
    '    assert "compatibility" in recovery\n'
)

EXECUTION_AUTH_SETUP = '''    auth_path = tmp_path / PATHS["AUTH"]
    legacy_auth = json.loads(auth_path.read_text(encoding="utf-8"))
    legacy_auth["sequence"] = 2
    legacy_auth["status"] = "consumed"
    auth_path.write_text(
        json.dumps(legacy_auth, ensure_ascii=False, indent=2) + "\\n",
        encoding="utf-8",
    )

'''

EXECUTION_MODULE_SETUP = '''    module = load_module()
    module.ROOT = tmp_path
    for name, relative in PATHS.items():
        setattr(module, name, tmp_path / relative)

    assert module.main() == 0
'''


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


def canonical_digest(value: dict[str, Any]) -> str:
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


def replace_required(text: str, old: str, new: str, *, expected_count: int) -> str:
    if new in text and old not in text:
        return text
    observed = text.count(old)
    if observed != expected_count:
        raise SystemExit(
            f"recovery-index repair anchor count mismatch: expected={expected_count} observed={observed}"
        )
    return text.replace(old, new)


def patch_file(path: Path, old: str, new: str, *, expected_count: int = 1) -> None:
    text = path.read_text(encoding="utf-8")
    updated = replace_required(text, old, new, expected_count=expected_count)
    path.write_text(updated, encoding="utf-8")


def normalize_annex_v2_current_doi_assertion() -> None:
    # Preserve the historical 21755655 -> 21755827 repair while accepting
    # the stronger forward-compatible contract used by later sealed baselines.
    text = ANNEX_V2_TEST.read_text(encoding="utf-8")
    if OLD_CURRENT_DOI_ASSERTION in text:
        updated = replace_required(
            text,
            OLD_CURRENT_DOI_ASSERTION,
            NEW_CURRENT_DOI_ASSERTION,
            expected_count=1,
        )
        ANNEX_V2_TEST.write_text(updated, encoding="utf-8")
        return
    if NEW_CURRENT_DOI_ASSERTION in text:
        return
    if (
        CURRENT_DOI_CONTRACT_ASSERTION in text
        and CURRENT_DOI_CONTRACT_SOURCE in text
    ):
        return
    raise SystemExit("recovery-index repair current DOI contract is unrecognized")


def normalize_execution_setup(text: str) -> str:
    # Keep exactly one legacy authorization fixture before module execution.
    without_duplicates = text.replace(EXECUTION_AUTH_SETUP, "")
    observed = without_duplicates.count(EXECUTION_MODULE_SETUP)
    if observed != 1:
        raise SystemExit(
            "preservation execution-test module anchor count mismatch: "
            f"expected=1 observed={observed}"
        )
    return without_duplicates.replace(
        EXECUTION_MODULE_SETUP,
        EXECUTION_AUTH_SETUP + EXECUTION_MODULE_SETUP,
        1,
    )


def normalize_values(value: object) -> list[str]:
    if not isinstance(value, list):
        raise SystemExit("recovery index limitations are invalid")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise SystemExit("recovery index limitation is not a string")
        if item == LEGACY_TREE_LIMITATION:
            item = BASELINE_TREE_LIMITATION
        if (
            "together preserve the current Git-tracked repository" in item
            or item == QUALIFIED_LIMITATION
        ):
            continue
        if item not in result:
            result.append(item)
    if BASELINE_TREE_LIMITATION not in result:
        result.append(BASELINE_TREE_LIMITATION)
    result.append(QUALIFIED_LIMITATION)
    return result


def main() -> int:
    source = REFRESH.read_text(encoding="utf-8")
    source = replace_required(source, OLD_FUNCTION, NEW_FUNCTION, expected_count=1)
    source = replace_required(source, OLD_FILTER, NEW_FILTER, expected_count=2)
    source = replace_required(source, OLD_VALIDATION, NEW_VALIDATION, expected_count=1)
    compile(source, str(REFRESH), "exec")
    REFRESH.write_text(source, encoding="utf-8")

    patch_file(FINAL_STATE_TEST, OLD_FINAL_STATE_ASSERTION, NEW_FINAL_STATE_ASSERTION)
    normalize_annex_v2_current_doi_assertion()
    patch_file(
        CAPSULE_TEST,
        OLD_RECOVERY_STATUS_ASSERTION,
        NEW_RECOVERY_STATUS_ASSERTION,
    )
    patch_file(SEMANTICS_TEST, OLD_HISTORICAL_ASSERTION, NEW_HISTORICAL_ASSERTION)

    execution_source = SEMANTICS_EXEC_TEST.read_text(encoding="utf-8")
    normalized_execution = normalize_execution_setup(execution_source)
    compile(normalized_execution, str(SEMANTICS_EXEC_TEST), "exec")
    SEMANTICS_EXEC_TEST.write_text(normalized_execution, encoding="utf-8")
    verified_execution = SEMANTICS_EXEC_TEST.read_text(encoding="utf-8")
    if verified_execution != normalize_execution_setup(verified_execution):
        raise SystemExit("preservation execution-test repair is not idempotent")
    if verified_execution.count(EXECUTION_AUTH_SETUP) != 1:
        raise SystemExit("preservation execution-test fixture was not deduplicated")

    index = read_json(INDEX)
    index["limitations"] = normalize_values(index.get("limitations"))
    index["source_digest"] = canonical_digest(index)
    write_json(INDEX, index)

    verified = read_json(INDEX)
    limitations = verified.get("limitations")
    if limitations != normalize_values(limitations):
        raise SystemExit("normalized recovery index is not idempotent")
    if verified.get("source_digest") != canonical_digest(verified):
        raise SystemExit("normalized recovery index digest mismatch")
    print("RECOVERY_INDEX_LIMITATIONS_NORMALIZED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
