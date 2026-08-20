#!/usr/bin/env python3
"""Publish one verified full-project GitHub artifact to Harvard Dataverse.

Security / authority boundary:
- Reads the exact successful `Full Project Preservation Bundle` Actions artifact.
- Creates a new Harvard Dataverse Dataset under collection alias `harvard`.
- Publishes the artifact as an opaque `.zip.bin` file so Dataverse will not unzip it.
- Performs full public-byte readback and SHA-256 verification before writing the final receipt.
- Does not write Arweave, Bitcoin, Ethereum, or amend any canonical Trinity Accord record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import threading
import time
import urllib.parse
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import httpx

SERVER = "https://dataverse.harvard.edu"
COLLECTION_ALIAS = "harvard"
WORKFLOW_NAME = "Full Project Preservation Bundle"
WORKFLOW_FILE = "full-project-preservation-bundle.yml"
ARTIFACT_NAME = "full-project-preservation-bundle"
ARCHIVE_NAME = "trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin"
USER_AGENT = "trinity-accord-harvard-preservation/1.0"
CHUNK = 8 * 1024 * 1024


class PublishError(RuntimeError):
    pass


def log(message: str) -> None:
    print(f"[harvard-preservation] {message}", flush=True)


@dataclass
class Progress:
    stage: str = "initializing"
    done: int = 0
    total: int = 0
    detail: str = ""


class Heartbeat:
    def __init__(self, progress: Progress, interval: int = 30) -> None:
        self.progress = progress
        self.interval = interval
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=2)

    def _run(self) -> None:
        n = 0
        while not self.stop_event.wait(self.interval):
            n += 1
            p = self.progress
            log(
                f"heartbeat={n} stage={p.stage} bytes={p.done}/{p.total or '?'} "
                f"detail={p.detail or 'none'}"
            )


def github_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": USER_AGENT,
    }


def hd_headers(token: str) -> dict[str, str]:
    return {"X-Dataverse-key": token, "User-Agent": USER_AGENT}


def require_status(response: httpx.Response, expected: Iterable[int], label: str) -> None:
    if response.status_code not in set(expected):
        body = response.text[:4000]
        raise PublishError(f"{label}: HTTP {response.status_code}: {body}")


def json_response(response: httpx.Response, expected: Iterable[int], label: str) -> dict[str, Any]:
    require_status(response, expected, label)
    try:
        payload = response.json()
    except ValueError as exc:
        raise PublishError(f"{label}: response is not JSON") from exc
    if isinstance(payload, dict) and payload.get("status") == "ERROR":
        raise PublishError(f"{label}: Dataverse ERROR: {payload}")
    return payload


def resolve_latest_successful_run(
    client: httpx.Client, repo: str, github_token: str
) -> tuple[int, str]:
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/runs"
    response = client.get(
        url,
        headers=github_headers(github_token),
        params={"branch": "main", "status": "success", "per_page": 20},
    )
    payload = json_response(response, (200,), "GitHub successful-run lookup")
    runs = payload.get("workflow_runs", [])
    if not runs:
        raise PublishError("no successful Full Project Preservation Bundle run exists on main")
    return int(runs[0]["id"]), str(runs[0]["head_sha"])


def get_run(
    client: httpx.Client, repo: str, github_token: str, run_id: int
) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    response = client.get(url, headers=github_headers(github_token))
    run = json_response(response, (200,), f"GitHub run {run_id}")
    if run.get("name") != WORKFLOW_NAME:
        raise PublishError(f"source run is {run.get('name')!r}, not {WORKFLOW_NAME!r}")
    if run.get("conclusion") != "success":
        raise PublishError(f"source run {run_id} is not successful: {run.get('conclusion')}")
    if run.get("head_branch") != "main":
        raise PublishError(f"source run {run_id} is not from main")
    return run


def download_exact_artifact(
    client: httpx.Client,
    repo: str,
    github_token: str,
    run_id: int,
    output: Path,
    progress: Progress,
) -> tuple[int, int, str]:
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"
    response = client.get(url, headers=github_headers(github_token), params={"per_page": 100})
    payload = json_response(response, (200,), "GitHub artifact listing")
    matches = [
        item
        for item in payload.get("artifacts", [])
        if item.get("name") == ARTIFACT_NAME and not item.get("expired", False)
    ]
    if len(matches) != 1:
        raise PublishError(f"expected one live {ARTIFACT_NAME!r} artifact, found {len(matches)}")
    artifact = matches[0]
    artifact_id = int(artifact["id"])
    progress.stage = "github_artifact_download"
    progress.done = 0
    progress.total = int(artifact.get("size_in_bytes") or 0)
    progress.detail = f"run_id={run_id} artifact_id={artifact_id}"
    h = hashlib.sha256()
    total = 0
    with client.stream(
        "GET",
        str(artifact["archive_download_url"]),
        headers=github_headers(github_token),
        follow_redirects=True,
        timeout=300,
    ) as stream:
        require_status(stream, (200,), "GitHub artifact download")
        with output.open("wb") as fh:
            for chunk in stream.iter_bytes(CHUNK):
                if not chunk:
                    continue
                fh.write(chunk)
                h.update(chunk)
                total += len(chunk)
                progress.done = total
    if total <= 0:
        raise PublishError("downloaded GitHub artifact is empty")
    return artifact_id, total, h.hexdigest()


def find_zip_member(zf: zipfile.ZipFile, basename: str) -> str:
    names = [name for name in zf.namelist() if not name.endswith("/")]
    exact = [name for name in names if name == basename]
    if exact:
        return exact[0]
    suffix = [name for name in names if name.endswith("/" + basename)]
    if len(suffix) != 1:
        raise PublishError(f"artifact ZIP does not contain a unique {basename!r}")
    return suffix[0]


def verify_embedded_bundle(archive: Path, source_sha: str) -> dict[str, Any]:
    with zipfile.ZipFile(archive, "r") as zf:
        manifest_name = find_zip_member(zf, "full-project-manifest.json")
        report_name = find_zip_member(zf, "verification-report.json")
        find_zip_member(zf, "SHA256SUMS")
        find_zip_member(zf, "verify-and-restore-full-project.py")
        manifest = json.loads(zf.read(manifest_name).decode("utf-8"))
        report = json.loads(zf.read(report_name).decode("utf-8"))
    if report.get("status") != "PASS":
        raise PublishError(f"embedded verification report is not PASS: {report.get('status')}")
    if manifest.get("source_git_commit_sha") != source_sha:
        raise PublishError(
            "bundle manifest source_git_commit_sha does not match the successful Actions run"
        )
    identity = manifest.get("bundle_identity_sha256")
    if not isinstance(identity, str) or len(identity) != 64:
        raise PublishError("bundle manifest has no valid bundle_identity_sha256")
    return manifest


def validate_hd_access(client: httpx.Client, token: str) -> dict[str, Any]:
    me = json_response(
        client.get(f"{SERVER}/api/users/:me", headers=hd_headers(token)),
        (200,),
        "Harvard /api/users/:me",
    )
    permissions = json_response(
        client.get(
            f"{SERVER}/api/dataverses/{COLLECTION_ALIAS}/userPermissions",
            headers=hd_headers(token),
        ),
        (200,),
        "Harvard collection permissions",
    )
    if permissions.get("data", {}).get("canAddDataset") is not True:
        raise PublishError("Harvard collection no longer grants canAddDataset=true")
    user = me.get("data", {})
    if not user.get("email"):
        raise PublishError("Harvard account has no dataset-contact email")
    return user


def build_dataset_metadata(
    source_sha: str,
    run_id: int,
    bundle_identity: str,
    contact_name: str,
    contact_email: str,
) -> dict[str, Any]:
    title = f"Trinity Accord — Full Project Preservation Bundle — {source_sha[:12]}"
    description = (
        "Non-amending archival preservation copy of the Trinity Accord project. "
        "It mirrors the verified content-addressed GitHub preservation artifact, including the "
        "repository recovery capsule, custom GitHub Release assets, and exact published "
        "Polygon/Base sidechain preservation bytes. This Harvard copy does not replace the "
        "Bitcoin Originals or alter the project's authority model. "
        f"Source Git commit: {source_sha}. Source Actions run: {run_id}. "
        f"Bundle identity SHA-256: {bundle_identity}."
    )
    primitive = lambda name, value: {
        "typeName": name,
        "multiple": False,
        "typeClass": "primitive",
        "value": value,
    }
    return {
        "datasetVersion": {
            "metadataBlocks": {
                "citation": {
                    "displayName": "Citation Metadata",
                    "fields": [
                        primitive("title", title),
                        {
                            "typeName": "author",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [{"authorName": primitive("authorName", "Trinity Accord Project")}],
                        },
                        {
                            "typeName": "datasetContact",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [
                                {
                                    "datasetContactName": primitive(
                                        "datasetContactName", contact_name
                                    ),
                                    "datasetContactEmail": primitive(
                                        "datasetContactEmail", contact_email
                                    ),
                                }
                            ],
                        },
                        {
                            "typeName": "dsDescription",
                            "multiple": True,
                            "typeClass": "compound",
                            "value": [
                                {
                                    "dsDescriptionValue": primitive(
                                        "dsDescriptionValue", description
                                    )
                                }
                            ],
                        },
                        {
                            "typeName": "subject",
                            "multiple": True,
                            "typeClass": "controlledVocabulary",
                            "value": ["Computer and Information Science"],
                        },
                    ],
                }
            }
        }
    }


def create_dataset(
    client: httpx.Client, token: str, metadata: dict[str, Any]
) -> tuple[int, str]:
    response = client.post(
        f"{SERVER}/api/dataverses/{COLLECTION_ALIAS}/datasets",
        headers={**hd_headers(token), "Content-Type": "application/json"},
        content=json.dumps(metadata, ensure_ascii=False).encode("utf-8"),
    )
    payload = json_response(response, (200, 201), "Harvard create Dataset")
    data = payload.get("data", {})
    pid = str(data.get("persistentId") or data.get("persistentIdentifier") or "")
    if not pid:
        raise PublishError(f"create Dataset response has no persistent ID: {payload}")
    return int(data["id"]), pid


def direct_upload_archive(
    client: httpx.Client,
    token: str,
    pid: str,
    archive: Path,
    sha256: str,
    progress: Progress,
) -> bool:
    size = archive.stat().st_size
    response = client.get(
        f"{SERVER}/api/datasets/:persistentId/uploadurls",
        headers=hd_headers(token),
        params={"persistentId": pid, "size": size},
    )
    if response.status_code != 200:
        log(f"direct upload unavailable HTTP={response.status_code}; falling back to Native API")
        return False
    payload = response.json()
    data = payload.get("data", {}) if isinstance(payload, dict) else {}
    storage = data.get("storageIdentifier")
    if not storage:
        log("direct upload response lacks storageIdentifier; falling back to Native API")
        return False

    progress.stage = "harvard_direct_upload"
    progress.done = 0
    progress.total = size
    progress.detail = f"dataset={pid}"
    try:
        if data.get("url"):
            def body() -> Iterable[bytes]:
                with archive.open("rb") as fh:
                    while True:
                        chunk = fh.read(CHUNK)
                        if not chunk:
                            break
                        progress.done += len(chunk)
                        yield chunk

            uploaded = client.put(
                str(data["url"]),
                headers={
                    "x-amz-tagging": "dv-state=temp",
                    "Content-Length": str(size),
                    "User-Agent": USER_AGENT,
                },
                content=body(),
                timeout=300,
            )
            require_status(uploaded, range(200, 300), "Harvard S3 direct upload")
        elif data.get("urls"):
            part_size = int(data["partSize"])
            etags: dict[str, str] = {}
            with archive.open("rb") as fh:
                for number, part_url in sorted(data["urls"].items(), key=lambda kv: int(kv[0])):
                    chunk = fh.read(part_size)
                    if not chunk:
                        raise PublishError(f"multipart upload ran out of bytes at part {number}")
                    uploaded = client.put(
                        str(part_url),
                        headers={"x-amz-tagging": "dv-state=temp", "User-Agent": USER_AGENT},
                        content=chunk,
                        timeout=300,
                    )
                    require_status(uploaded, range(200, 300), f"Harvard multipart part {number}")
                    etag = uploaded.headers.get("ETag")
                    if not etag:
                        raise PublishError(f"multipart part {number} returned no ETag")
                    etags[str(number)] = etag
                    progress.done += len(chunk)
            complete = data.get("complete")
            if not complete:
                raise PublishError("multipart direct-upload response has no complete URL")
            complete_url = urllib.parse.urljoin(SERVER + "/", str(complete).lstrip("/"))
            finished = client.put(complete_url, json=etags, timeout=120)
            require_status(finished, range(200, 300), "Harvard multipart completion")
        else:
            return False
    except Exception:
        abort = data.get("abort")
        if abort:
            try:
                abort_url = urllib.parse.urljoin(SERVER + "/", str(abort).lstrip("/"))
                client.delete(abort_url, timeout=30)
            except Exception:
                pass
        raise

    file_meta = {
        "description": "Exact opaque GitHub Actions artifact bytes for the full Trinity Accord preservation bundle.",
        "categories": ["Data"],
        "restrict": "false",
        "storageIdentifier": storage,
        "fileName": ARCHIVE_NAME,
        "mimeType": "application/octet-stream",
        "fileSize": size,
        "checksum": {"@type": "SHA-256", "@value": sha256},
    }
    registered = client.post(
        f"{SERVER}/api/datasets/:persistentId/add",
        headers=hd_headers(token),
        params={"persistentId": pid},
        files={"jsonData": (None, json.dumps(file_meta, separators=(",", ":")))},
    )
    json_response(registered, (200, 201), "Harvard register direct-upload file")
    return True


def native_upload_archive(
    client: httpx.Client,
    token: str,
    pid: str,
    archive: Path,
    progress: Progress,
) -> None:
    progress.stage = "harvard_native_upload"
    progress.done = 0
    progress.total = archive.stat().st_size
    progress.detail = f"dataset={pid}"
    metadata = json.dumps(
        {
            "description": "Exact opaque GitHub Actions artifact bytes for the full Trinity Accord preservation bundle.",
            "categories": ["Data"],
            "restrict": "false",
        },
        separators=(",", ":"),
    )
    with archive.open("rb") as fh:
        response = client.post(
            f"{SERVER}/api/datasets/:persistentId/add",
            headers=hd_headers(token),
            params={"persistentId": pid},
            files={
                "file": (ARCHIVE_NAME, fh, "application/octet-stream"),
                "jsonData": (None, metadata),
            },
            timeout=300,
        )
    json_response(response, (200, 201), "Harvard Native API archive upload")
    progress.done = progress.total


def upload_small_file(
    client: httpx.Client,
    token: str,
    pid: str,
    path: Path,
    description: str,
) -> None:
    meta = json.dumps(
        {"description": description, "categories": ["Documentation"], "restrict": "false"},
        separators=(",", ":"),
    )
    with path.open("rb") as fh:
        response = client.post(
            f"{SERVER}/api/datasets/:persistentId/add",
            headers=hd_headers(token),
            params={"persistentId": pid},
            files={
                "file": (
                    path.name,
                    fh,
                    mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                ),
                "jsonData": (None, meta),
            },
        )
    json_response(response, (200, 201), f"Harvard upload {path.name}")


def publish_dataset(client: httpx.Client, token: str, pid: str, version_type: str) -> None:
    deadline = time.time() + 300
    while time.time() < deadline:
        response = client.post(
            f"{SERVER}/api/datasets/:persistentId/actions/:publish",
            headers=hd_headers(token),
            params={
                "persistentId": pid,
                "type": version_type,
                "assureIsIndexed": "true",
            },
        )
        if response.status_code in (200, 202):
            return
        if response.status_code == 409:
            log("publish waiting for Dataverse indexing")
            time.sleep(10)
            continue
        require_status(response, (200, 202), "Harvard publish Dataset")
    raise PublishError("Dataverse publish remained blocked on indexing for five minutes")


def wait_released_dataset(client: httpx.Client, pid: str) -> dict[str, Any]:
    deadline = time.time() + 300
    while time.time() < deadline:
        response = client.get(
            f"{SERVER}/api/datasets/:persistentId/",
            params={"persistentId": pid},
        )
        if response.status_code == 200:
            payload = response.json()
            version = payload.get("data", {}).get("latestVersion", {})
            if version.get("versionState") == "RELEASED":
                return payload
        time.sleep(10)
    raise PublishError("Dataset did not reach RELEASED state within five minutes")


def find_file_id(dataset: dict[str, Any], filename: str) -> int:
    version = dataset.get("data", {}).get("latestVersion", {})
    for item in version.get("files", []):
        data_file = item.get("dataFile", {})
        if data_file.get("filename") == filename:
            return int(data_file["id"])
    raise PublishError(f"released Dataset does not contain file {filename!r}")


def public_readback(
    client: httpx.Client, file_id: int, progress: Progress
) -> tuple[int, str]:
    progress.stage = "harvard_public_readback"
    progress.done = 0
    progress.total = 0
    progress.detail = f"file_id={file_id}"
    h = hashlib.sha256()
    total = 0
    with client.stream(
        "GET",
        f"{SERVER}/api/access/datafile/{file_id}",
        follow_redirects=True,
        timeout=300,
    ) as stream:
        require_status(stream, (200,), "Harvard public-byte readback")
        length = stream.headers.get("Content-Length")
        if length and length.isdigit():
            progress.total = int(length)
        for chunk in stream.iter_bytes(CHUNK):
            if not chunk:
                continue
            h.update(chunk)
            total += len(chunk)
            progress.done = total
    return total, h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-run-id", type=int)
    parser.add_argument("--source-head-sha")
    parser.add_argument("--output-dir", default="harvard-publication")
    args = parser.parse_args()

    github_token = os.environ.get("GITHUB_TOKEN", "")
    hd_token = os.environ.get("HD_API_TOKEN", "")
    if not github_token:
        raise PublishError("GITHUB_TOKEN is missing")
    if not hd_token:
        raise PublishError("HD_API_TOKEN is missing; expected GitHub Secret HD")

    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / ARCHIVE_NAME
    receipt_path = output / "harvard-publication-receipt.json"
    progress = Progress()
    heartbeat = Heartbeat(progress)
    heartbeat.start()

    try:
        with httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=httpx.Timeout(120.0, read=300.0),
        ) as client:
            progress.stage = "resolve_source_run"
            if args.source_run_id:
                run_id = args.source_run_id
                run = get_run(client, args.repository, github_token, run_id)
                source_sha = str(run["head_sha"])
            else:
                run_id, source_sha = resolve_latest_successful_run(
                    client, args.repository, github_token
                )
                run = get_run(client, args.repository, github_token, run_id)
            if args.source_head_sha and args.source_head_sha != source_sha:
                raise PublishError(
                    f"source SHA mismatch: event={args.source_head_sha} API={source_sha}"
                )
            log(f"source_run PASS run_id={run_id} source_sha={source_sha}")

            artifact_id, artifact_bytes, artifact_sha256 = download_exact_artifact(
                client,
                args.repository,
                github_token,
                run_id,
                archive,
                progress,
            )
            log(
                f"artifact_download PASS artifact_id={artifact_id} bytes={artifact_bytes} "
                f"sha256={artifact_sha256}"
            )

            progress.stage = "verify_embedded_bundle"
            manifest = verify_embedded_bundle(archive, source_sha)
            bundle_identity = str(manifest["bundle_identity_sha256"])
            log(f"embedded_bundle PASS bundle_identity_sha256={bundle_identity}")

            progress.stage = "validate_harvard_access"
            user = validate_hd_access(client, hd_token)
            contact_name = str(
                user.get("displayName")
                or " ".join(filter(None, [user.get("firstName"), user.get("lastName")]))
                or "Trinity Accord Project"
            )
            # Contact email is required by Dataverse metadata. It is consumed from the
            # authenticated Harvard account and is deliberately never printed to logs.
            contact_email = str(user["email"])
            log(f"Harvard access PASS collection={COLLECTION_ALIAS} canAddDataset=true")

            progress.stage = "create_harvard_dataset"
            metadata = build_dataset_metadata(
                source_sha,
                run_id,
                bundle_identity,
                contact_name,
                contact_email,
            )
            dataset_id, pid = create_dataset(client, hd_token, metadata)
            log(f"dataset_create PASS dataset_id={dataset_id} persistent_id={pid}")

            if not direct_upload_archive(
                client,
                hd_token,
                pid,
                archive,
                artifact_sha256,
                progress,
            ):
                native_upload_archive(client, hd_token, pid, archive, progress)
            log("archive_upload PASS")

            # Publish 1.0 only after the complete opaque archive is registered.
            progress.stage = "publish_dataset_1_0"
            publish_dataset(client, hd_token, pid, "major")
            released = wait_released_dataset(client, pid)
            artifact_file_id = find_file_id(released, ARCHIVE_NAME)
            log(f"dataset_1_0 RELEASED artifact_file_id={artifact_file_id}")

            readback_bytes, readback_sha256 = public_readback(
                client, artifact_file_id, progress
            )
            if readback_bytes != artifact_bytes:
                raise PublishError(
                    f"public readback byte-size mismatch {readback_bytes} != {artifact_bytes}"
                )
            if readback_sha256 != artifact_sha256:
                raise PublishError(
                    f"public readback SHA-256 mismatch {readback_sha256} != {artifact_sha256}"
                )
            log(
                f"PUBLIC BYTE READBACK PASS bytes={readback_bytes} sha256={readback_sha256}"
            )

            receipt = {
                "schema": "trinity-accord-harvard-publication-receipt-v1",
                "server": SERVER,
                "collection_alias": COLLECTION_ALIAS,
                "dataset_id": dataset_id,
                "persistent_id": pid,
                "source_repository": args.repository,
                "source_workflow": WORKFLOW_NAME,
                "source_workflow_run_id": run_id,
                "source_workflow_run_url": run.get("html_url"),
                "source_git_commit_sha": source_sha,
                "github_artifact_id": artifact_id,
                "github_artifact_name": ARTIFACT_NAME,
                "harvard_archive_filename": ARCHIVE_NAME,
                "artifact_bytes": artifact_bytes,
                "artifact_sha256": artifact_sha256,
                "bundle_identity_sha256": bundle_identity,
                "coverage": manifest.get("coverage"),
                "public_readback_verified": True,
                "public_readback_bytes": readback_bytes,
                "public_readback_sha256": readback_sha256,
                "publication_semantics": {
                    "role": "non_amending_archival_mirror",
                    "canonical_authority_changed": False,
                    "bitcoin_originals_replaced": False,
                },
            }
            receipt_path.write_text(
                json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            upload_small_file(
                client,
                hd_token,
                pid,
                receipt_path,
                "Machine-readable receipt proving exact GitHub-artifact to Harvard public-byte equivalence.",
            )
            log("final_receipt_upload PASS")

            progress.stage = "publish_dataset_1_1"
            publish_dataset(client, hd_token, pid, "minor")
            final_dataset = wait_released_dataset(client, pid)
            find_file_id(final_dataset, ARCHIVE_NAME)
            find_file_id(final_dataset, receipt_path.name)
            log(f"HARVARD PRESERVATION COMPLETE persistent_id={pid} version=1.1")
            return 0
    finally:
        heartbeat.stop()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log(f"FAIL {type(exc).__name__}: {exc}")
        raise
