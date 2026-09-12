#!/usr/bin/env python3
"""Read-only Harvard Dataverse account and storage probe.

The probe accepts the Dataverse API token only through HD_API_TOKEN, performs
GET requests only, and writes a deliberately redacted JSON result.  It never
creates, edits, uploads, submits, publishes, or deletes a Dataverse object.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


SERVER = "https://dataverse.harvard.edu"
OLD_DATASET_ID = 14153533
OLD_PID = "doi:10.7910/DVN/YUCG12"
EPOCH_II_PLANNED_BYTES = 23_107_006_729


class ProbeError(RuntimeError):
    pass


def get_json(token: str, path: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{SERVER}{path}",
        method="GET",
        headers={
            "X-Dataverse-key": token,
            "Accept": "application/json",
            "User-Agent": "trinity-accord-harvard-hd-readonly-probe/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read(1500).decode("utf-8", errors="replace")
        raise ProbeError(f"GET {path} returned HTTP {exc.code}: {body}") from exc
    if not isinstance(payload, dict):
        raise ProbeError(f"GET {path} did not return a JSON object")
    if payload.get("status") == "ERROR":
        raise ProbeError(f"GET {path} returned Dataverse error: {payload.get('message', 'unknown')}")
    return payload


def data(payload: dict[str, Any]) -> Any:
    return payload.get("data")


def mask_email(value: Any) -> str | None:
    if not isinstance(value, str) or "@" not in value:
        return None
    local, domain = value.rsplit("@", 1)
    if not local or not domain:
        return None
    return f"{local[0]}***@{domain}"


def first_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    if isinstance(value, dict):
        preferred = (
            "quota",
            "quotaIn.src",
            "quotaInBytes",
            "storagenergies",
            "storageQuota",
            "size",
            "bytes",
            "storageSize",
            "total",
        )
        for key in preferred:
            if key in value:
                parsed = first_int(value[key])
                if parsed is not None:
                    return parsed
        for nested in value.values():
            parsed = first_int(nested)
            if parsed is not None:
                return parsed
    return None


def safe_identity(user: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "id": user.get("id"),
        "identifier": user.get("identifier"),
        "display_name": user.get("displayName"),
        "affiliation": user.get("affiliation"),
        "position": user.get("position"),
        "account_type": user.get("authenticationProviderId") or user.get("accountType"),
        "email_masked": mask_email(user.get("email")),
    }
    return {key: value for key, value in allowed.items() if value not in (None, "")}


def main() -> int:
    token = os.environ.get("HD_API_TOKEN", "").strip()
    if not token:
        raise ProbeError("HD_API_TOKEN is missing")

    output_path = Path(os.environ.get("PROBE_OUTPUT", "harvard-hd-readonly-probe.json"))
    me_payload = get_json(token, "/api/users/:me")
    user = data(me_payload)
    if not isinstance(user, dict) or not user.get("identifier"):
        raise ProbeError("authenticated user response lacks identifier")

    collection_permissions = data(
        get_json(token, "/api/dataverses/harvard/userPermissions")
    )
    dataset_permissions = data(
        get_json(token, f"/api/datasets/{OLD_DATASET_ID}/userPermissions")
    )
    quota_raw = data(
        get_json(token, f"/api/datasets/{OLD_DATASET_ID}/storage/quota?showInherited=true")
    )
    use_raw = data(get_json(token, f"/api/datasets/{OLD_DATASET_ID}/storage/use"))
    latest = data(get_json(token, f"/api/datasets/{OLD_DATASET_ID}/versions/:latest"))

    quota_bytes = first_int(quota_raw)
    use_bytes = first_int(use_raw)
    can_add = bool(
        isinstance(collection_permissions, dict)
        and collection_permissions.get("canAddDataset") is True
    )
    can_edit_old = bool(
        isinstance(dataset_permissions, dict)
        and (
            dataset_permissions.get("canEditDataset") is True
            or dataset_permissions.get("canEdit") is True
        )
    )

    result = {
        "schema": "trinityaccord.harvard-hd-readonly-probe.v1",
        "server": SERVER,
        "read_only": True,
        "http_methods_used": ["GET"],
        "token_valid": True,
        "account": safe_identity(user),
        "permissions": {
            "harvard_collection_can_add_dataset": can_add,
            "old_dataset_can_edit": can_edit_old,
        },
        "old_dataset": {
            "dataset_id": OLD_DATASET_ID,
            "persistent_id": OLD_PID,
            "version_state": latest.get("versionState") if isinstance(latest, dict) else None,
            "version_number": latest.get("versionNumber") if isinstance(latest, dict) else None,
            "storage_quota_response": quota_raw,
            "storage_use_response": use_raw,
            "applicable_quota_bytes": quota_bytes,
            "storage_use_bytes": use_bytes,
        },
        "epoch_ii": {
            "planned_bytes": EPOCH_II_PLANNED_BYTES,
            "fits_if_new_dataset_inherits_same_quota": (
                quota_bytes is not None and EPOCH_II_PLANNED_BYTES <= quota_bytes
            ),
        },
        "interpretation_limits": [
            "The quota endpoint is dataset-scoped, not an account-wide remaining-quota endpoint.",
            "The old Dataset's inherited quota does not prove the quota assigned to a future Dataset.",
            "No Harvard Dataset was created or modified by this probe.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Logs intentionally omit account identity, email, and token-derived details.
    print("HD token valid: PASS")
    print(f"Can add Dataset to Harvard collection: {'PASS' if can_add else 'FAIL'}")
    print(f"Can edit old Dataset: {'PASS' if can_edit_old else 'FAIL'}")
    print(f"Old Dataset applicable quota bytes: {quota_bytes if quota_bytes is not None else 'UNAVAILABLE'}")
    print(f"Old Dataset storage use bytes: {use_bytes if use_bytes is not None else 'UNAVAILABLE'}")
    print(
        "Epoch II fits if same quota is inherited: "
        + ("PASS" if quota_bytes is not None and EPOCH_II_PLANNED_BYTES <= quota_bytes else "UNKNOWN")
    )
    if not can_add:
        return 2
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"READ-ONLY PROBE FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
