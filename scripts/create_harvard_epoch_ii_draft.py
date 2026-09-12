#!/usr/bin/env python3
"""Create exactly one metadata-only Harvard Preservation Epoch II draft.

The write boundary is intentionally narrow: one new Dataset may be created in
the Harvard root collection and its license may be changed to the frozen Custom
Dataset Terms.  The script never uploads a file, submits for review, publishes,
or mutates the released Preservation Epoch I Dataset.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


SERVER = "https://dataverse.harvard.edu"
COLLECTION = "harvard"
OLD_DATASET_ID = 14_153_533
OLD_PID = "doi:10.7910/DVN/YUCG12"
TITLE = "Trinity Accord — Research Corpus and Preservation Mirror · Preservation Epoch II"
EXPECTED_TERMS_SHA256 = "881ee6b94f3fddaa53d66bcd5c64d6510a6fdf9ce0a7d61bca0ba72555dd361c"
AUTHORIZATION = "Harvard Epoch II metadata-only draft creation authorized: 2026-09-12"


class DraftError(RuntimeError):
    pass


def headers(token: str, *, json_body: bool = False) -> dict[str, str]:
    result = {
        "X-Dataverse-key": token,
        "Accept": "application/json",
        "User-Agent": "trinity-accord-harvard-epoch-ii-draft/1.0",
    }
    if json_body:
        result["Content-Type"] = "application/json"
    return result


def request_json(
    token: str,
    method: str,
    path: str,
    *,
    body: dict[str, Any] | None = None,
    expected: tuple[int, ...] = (200,),
) -> dict[str, Any]:
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        f"{SERVER}{path}",
        data=payload,
        method=method,
        headers=headers(token, json_body=body is not None),
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            if response.status not in expected:
                raise DraftError(f"{method} {path} returned HTTP {response.status}")
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        text = exc.read(1500).decode("utf-8", errors="replace")
        raise DraftError(f"{method} {path} returned HTTP {exc.code}: {text}") from exc
    if not isinstance(result, dict) or result.get("status") == "ERROR":
        raise DraftError(f"{method} {path} returned an invalid/error response")
    return result


def primitive(type_name: str, value: Any, *, multiple: bool = False) -> dict[str, Any]:
    return {
        "typeName": type_name,
        "multiple": multiple,
        "typeClass": "primitive",
        "value": value,
    }


def controlled(type_name: str, values: list[str]) -> dict[str, Any]:
    return {
        "typeName": type_name,
        "multiple": True,
        "typeClass": "controlledVocabulary",
        "value": values,
    }


def compound(type_name: str, values: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "typeName": type_name,
        "multiple": True,
        "typeClass": "compound",
        "value": values,
    }


def load_inputs(root: Path) -> tuple[dict[str, Any], str, str]:
    meta_path = root / "preservation/epoch-ii/HARVARD-DRAFT-METADATA.json"
    description_path = root / "preservation/epoch-ii/HARVARD-DATASET-DESCRIPTION.md"
    terms_path = root / "preservation/epoch-ii/HARVARD-TERMS-OF-USE.txt"
    marker_path = root / ".github/harvard-epoch-ii-draft-create-authorized-v1"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    description = description_path.read_text(encoding="utf-8").strip()
    terms = terms_path.read_text(encoding="utf-8").strip()
    marker = marker_path.read_text(encoding="utf-8").strip()
    if marker != AUTHORIZATION:
        raise DraftError("exact metadata-only draft authorization marker is missing")
    if metadata.get("title") != TITLE:
        raise DraftError("frozen preview title mismatch")
    terms_sha = hashlib.sha256(terms.encode("utf-8")).hexdigest()
    if terms_sha != EXPECTED_TERMS_SHA256:
        raise DraftError(f"Terms hash mismatch: {terms_sha}")
    if metadata.get("license", {}).get("terms_of_use_sha256") != terms_sha:
        raise DraftError("preview metadata Terms binding mismatch")
    return metadata, description, terms


def build_metadata(
    preview: dict[str, Any], description: str, contact_name: str, contact_email: str
) -> dict[str, Any]:
    keyword_values = [
        {"keywordValue": primitive("keywordValue", value)}
        for value in preview["keywords"]
    ]
    related = preview["related_material"]
    fields = [
        primitive("title", TITLE),
        compound(
            "author",
            [{"authorName": primitive("authorName", item["authorName"])} for item in preview["authors"]],
        ),
        compound(
            "datasetContact",
            [
                {
                    "datasetContactName": primitive("datasetContactName", contact_name),
                    "datasetContactEmail": primitive("datasetContactEmail", contact_email),
                }
            ],
        ),
        compound(
            "dsDescription",
            [{"dsDescriptionValue": primitive("dsDescriptionValue", description)}],
        ),
        controlled("subject", preview["subjects"]),
        compound("keyword", keyword_values),
        compound(
            "producer",
            [{"producerName": primitive("producerName", preview["producer"])}],
        ),
        primitive("productionDate", preview["production_date"]),
        controlled("language", preview["language"]),
        primitive("relatedMaterial", related, multiple=True),
    ]
    return {
        "datasetVersion": {
            "metadataBlocks": {
                "citation": {"displayName": "Citation Metadata", "fields": fields}
            }
        }
    }


def field_value(version: dict[str, Any], type_name: str) -> Any:
    fields = version.get("metadataBlocks", {}).get("citation", {}).get("fields", [])
    for field in fields:
        if isinstance(field, dict) and field.get("typeName") == type_name:
            return field.get("value")
    return None


def latest(token: str, dataset_id: int) -> dict[str, Any]:
    payload = request_json(token, "GET", f"/api/datasets/{dataset_id}")
    version = payload.get("data", {}).get("latestVersion")
    if not isinstance(version, dict):
        raise DraftError(f"Dataset {dataset_id} has no latestVersion")
    return version


def verify_old(version: dict[str, Any]) -> dict[str, Any]:
    state = {
        "version_state": version.get("versionState"),
        "version_number": version.get("versionNumber"),
        "version_minor_number": version.get("versionMinorNumber"),
        "file_count": len(version.get("files") or []),
    }
    if state["version_state"] != "RELEASED" or state["version_number"] != 1:
        raise DraftError(f"old Harvard Dataset is not frozen RELEASED v1: {state}")
    return state


def find_existing_draft(token: str) -> tuple[int, str] | None:
    query = urllib.parse.urlencode({"q": f'title:"{TITLE}"', "type": "dataset", "per_page": 100})
    payload = request_json(token, "GET", f"/api/search?{query}")
    items = payload.get("data", {}).get("items", [])
    matches: list[tuple[int, str]] = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict) or item.get("name") != TITLE:
            continue
        entity_id = item.get("entity_id") or item.get("entityId")
        pid = item.get("global_id") or item.get("globalId")
        if entity_id and pid:
            matches.append((int(entity_id), str(pid)))
    if len(matches) > 1:
        raise DraftError("multiple exact-title Epoch II Datasets found; refusing another creation")
    if not matches:
        return None
    dataset_id, pid = matches[0]
    version = latest(token, dataset_id)
    if version.get("versionState") != "DRAFT":
        raise DraftError("exact-title Epoch II Dataset exists but is not a DRAFT")
    return dataset_id, pid


def verify_new(token: str, dataset_id: int, pid: str, terms: str) -> dict[str, Any]:
    version = latest(token, dataset_id)
    if version.get("versionState") != "DRAFT":
        raise DraftError("new Epoch II Dataset is not DRAFT")
    if field_value(version, "title") != TITLE:
        raise DraftError("new Epoch II title readback mismatch")
    files = version.get("files") or []
    if files:
        raise DraftError("metadata-only draft unexpectedly contains files")
    observed_terms = str(version.get("termsOfUse") or "").strip()
    if observed_terms != terms:
        raise DraftError("new Epoch II Custom Terms readback mismatch")
    return {
        "dataset_id": dataset_id,
        "persistent_id": pid,
        "title": TITLE,
        "version_state": version.get("versionState"),
        "version_number": version.get("versionNumber"),
        "version_minor_number": version.get("versionMinorNumber"),
        "file_count": 0,
        "terms_sha256": hashlib.sha256(observed_terms.encode("utf-8")).hexdigest(),
    }


def main() -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise DraftError("HD_API_TOKEN is missing")
    root = Path(__file__).resolve().parents[1]
    preview, description, terms = load_inputs(root)
    user_payload = request_json(token, "GET", "/api/users/:me")
    user = user_payload.get("data") or {}
    identifier = str(user.get("identifier") or "")
    contact_name = str(user.get("displayName") or "")
    contact_email = str(user.get("email") or "")
    if not identifier or not contact_name or "@" not in contact_email:
        raise DraftError("HD account identity/contact fields are incomplete")
    permissions = request_json(token, "GET", f"/api/dataverses/{COLLECTION}/userPermissions")
    if permissions.get("data", {}).get("canAddDataset") is not True:
        raise DraftError("HD account cannot add a Dataset to the Harvard collection")

    old_before = verify_old(latest(token, OLD_DATASET_ID))
    existing = find_existing_draft(token)
    if existing is None:
        body = build_metadata(preview, description, contact_name, contact_email)
        created = request_json(
            token,
            "POST",
            f"/api/dataverses/{COLLECTION}/datasets",
            body=body,
            expected=(200, 201),
        ).get("data", {})
        dataset_id = int(created.get("id") or 0)
        pid = str(created.get("persistentId") or created.get("persistentIdentifier") or "")
        if dataset_id <= 0 or not pid:
            raise DraftError("create Dataset response lacks id or persistent identifier")
        action = "created"
    else:
        dataset_id, pid = existing
        action = "reused_existing_draft"

    request_json(
        token,
        "PUT",
        f"/api/datasets/{dataset_id}/license",
        body={"customTerms": {"termsOfUse": terms}},
    )
    new_state = verify_new(token, dataset_id, pid, terms)
    old_after = verify_old(latest(token, OLD_DATASET_ID))
    if old_after != old_before:
        raise DraftError("old Harvard Dataset state changed during Epoch II creation")

    result = {
        "schema": "trinityaccord.harvard-epoch-ii-draft-state.v1",
        "action": action,
        "account_identifier": identifier,
        "dataset": new_state,
        "old_dataset": {
            "persistent_id": OLD_PID,
            **old_after,
            "mutated": False,
        },
        "files_uploaded": 0,
        "submitted_for_review": False,
        "published": False,
        "automatic_resubmission_enabled": False,
    }
    output = Path(os.environ.get("DRAFT_STATE_OUTPUT", "harvard-epoch-ii-draft-state.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Epoch II metadata-only draft {action}: dataset_id={dataset_id} persistent_id={pid}")
    print("Files uploaded: 0")
    print("Submitted for review: false")
    print("Old DOI mutated: false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except DraftError as exc:
        print(f"EPOCH II DRAFT ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
