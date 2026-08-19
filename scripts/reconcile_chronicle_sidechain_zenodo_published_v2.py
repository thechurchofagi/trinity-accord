#!/usr/bin/env python3
"""Strictly reconcile the already-published sidechain Zenodo record.

The first published sidechain DOI package contains one historical builder field
(`RECOVERY-VERIFICATION.json.generated_at`) that was generated from wall-clock
time. Rebuilding the package later therefore cannot reproduce three auxiliary
file hashes byte-for-byte (recovery JSON, deposit JSON, and SHA256SUMS), even
though the immutable source archive is unchanged.

This recovery verifier does not weaken evidence acceptance. Instead it verifies
both sides of the boundary:

1. the locally rebuilt package is cold-verified against the immutable GitHub
   Release, exactly as before;
2. every byte of the public Zenodo record is streamed and SHA-256 hashed;
3. deterministic public files (archive, sidecar, README, source binding) must
   equal the local immutable-source build byte-for-byte;
4. the legacy recovery JSON must equal the local recovery semantics after
   removing only `generated_at`, whose value must be a valid UTC timestamp;
5. the published deposit inventory and package identity are recomputed from the
   public bytes and must be internally exact;
6. the published SHA256SUMS must match every public file it claims;
7. repository DOI state is written only after all seven public files have been
   fully read back and verified.

No Zenodo write, upload, edit, new-version, or publish operation is performed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from publish_chronicle_sidechain_to_zenodo import TITLE, verify_local

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_API = "https://zenodo.org/api"
DEFAULT_STATE = ROOT / "archive" / "chronicle-sidechain-zenodo-state.json"
CHUNK_BYTES = 8 * 1024 * 1024
PROGRESS_BYTES = 64 * 1024 * 1024
TRANSIENT_HTTP = {408, 425, 429, 500, 502, 503, 504}
SMALL_FILE_LIMIT = 4 * 1024 * 1024


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rec_meta(rec: dict[str, Any]) -> dict[str, Any]:
    value = rec.get("metadata")
    return value if isinstance(value, dict) else {}


def rec_version(rec: dict[str, Any]) -> str:
    return str(rec_meta(rec).get("version") or "")


def rec_doi(rec: dict[str, Any]) -> str:
    value = rec.get("doi") or rec_meta(rec).get("doi")
    if value:
        return str(value)
    pids = rec.get("pids") if isinstance(rec.get("pids"), dict) else {}
    doi_obj = pids.get("doi") if isinstance(pids.get("doi"), dict) else {}
    return str(doi_obj.get("identifier") or "")


def rec_concept_doi(rec: dict[str, Any]) -> str:
    value = rec.get("conceptdoi") or rec_meta(rec).get("conceptdoi")
    if value:
        return str(value)
    pids = rec.get("pids") if isinstance(rec.get("pids"), dict) else {}
    parent = pids.get("conceptdoi") if isinstance(pids.get("conceptdoi"), dict) else {}
    return str(parent.get("identifier") or "")


def is_published(rec: dict[str, Any]) -> bool:
    return rec.get("submitted") is True or str(rec.get("state") or "").lower() == "done" or bool(rec_doi(rec))


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def parse_checksum(value: Any) -> str:
    text = str(value or "").lower()
    return text.split(":", 1)[-1] if text else ""


def remote_size(item: dict[str, Any]) -> int:
    for key in ("size", "filesize"):
        if item.get(key) is not None:
            try:
                return int(item[key])
            except (TypeError, ValueError):
                pass
    raise SystemExit(f"Zenodo public file metadata lacks numeric size: {item.get('key') or item.get('filename')}")


class PublicVerifier:
    def __init__(self, *, token: str, api_base: str, debug_path: pathlib.Path, attempts: int, timeout: int, delay: int):
        if not token:
            raise SystemExit("ZENODO_ACCESS_TOKEN is required for owner-deposition discovery")
        self.token = token
        self.base = api_base.rstrip("/")
        self.debug_path = debug_path
        self.attempts = max(1, attempts)
        self.timeout = max(60, timeout)
        self.delay = max(1, delay)
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        if debug_path.exists():
            debug_path.unlink()

    def log(self, event: str, **fields: Any) -> None:
        row = {"ts": now(), "event": event, **fields}
        with self.debug_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        print("[ZENODO PUBLIC V2] " + event + (" " if fields else "") + " ".join(f"{k}={v}" for k, v in fields.items()), flush=True)

    def headers(self, authenticated: bool) -> dict[str, str]:
        out = {"Accept": "application/json", "User-Agent": "trinity-sidechain-zenodo-reconcile/2.0"}
        if authenticated:
            out["Authorization"] = f"Bearer {self.token}"
        return out

    def get_json(self, url: str, *, authenticated: bool, retry_404: bool, label: str) -> Any:
        target = self.base + url if url.startswith("/") else url
        for attempt in range(1, self.attempts + 1):
            request = urllib.request.Request(target, method="GET", headers=self.headers(authenticated))
            self.log("json_get_start", label=label, attempt=attempt, path=urllib.parse.urlparse(target).path)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw = response.read()
                value = json.loads(raw.decode("utf-8"))
                self.log("json_get_ok", label=label, attempt=attempt, bytes=len(raw))
                return value
            except urllib.error.HTTPError as exc:
                retryable = exc.code in TRANSIENT_HTTP or (retry_404 and exc.code == 404)
                self.log("json_get_http_error", label=label, attempt=attempt, status=exc.code, retryable=retryable)
                if not retryable or attempt >= self.attempts:
                    raise SystemExit(f"Zenodo {label} HTTP {exc.code}") from exc
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                self.log("json_get_error", label=label, attempt=attempt, error=repr(exc))
                if attempt >= self.attempts:
                    raise SystemExit(f"Zenodo {label} failed: {exc}") from exc
            time.sleep(min(self.delay * attempt, 30))
        raise SystemExit(f"Zenodo {label} retry budget exhausted")

    def find_deposition(self, version_id: str) -> dict[str, Any]:
        matches: list[dict[str, Any]] = []
        for page in range(1, 21):
            query = urllib.parse.urlencode({"size": 100, "page": page, "sort": "mostrecent", "all_versions": "true"})
            rows = self.get_json(f"/deposit/depositions?{query}", authenticated=True, retry_404=False, label=f"depositions-{page}")
            if not isinstance(rows, list):
                raise SystemExit("Zenodo owner deposition list is not an array")
            page_rows = [row for row in rows if isinstance(row, dict)]
            matches.extend(row for row in page_rows if rec_meta(row).get("title") == TITLE and rec_version(row) == version_id)
            if len(page_rows) < 100:
                break
        if len(matches) != 1:
            raise SystemExit(f"expected exactly one Zenodo deposition for version {version_id}, found {len(matches)}")
        result = matches[0]
        if not is_published(result):
            raise SystemExit(f"Zenodo deposition for version {version_id} is not published")
        if not rec_doi(result):
            raise SystemExit("published Zenodo deposition lacks DOI")
        return result

    def public_record(self, deposition: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        raw_id = deposition.get("record_id") or deposition.get("recid") or deposition.get("id")
        try:
            record_id = int(raw_id)
        except Exception as exc:
            raise SystemExit("published deposition lacks numeric record id") from exc
        record = self.get_json(f"/records/{record_id}", authenticated=False, retry_404=True, label="public-record")
        if not isinstance(record, dict):
            raise SystemExit("public Zenodo record is not an object")
        self.log("public_record_visible", record_id=record_id, doi=rec_doi(record) or rec_doi(deposition))
        return record_id, record

    @staticmethod
    def files(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
        rows = record.get("files")
        if not isinstance(rows, list):
            raise SystemExit("public Zenodo record lacks files array")
        out: dict[str, dict[str, Any]] = {}
        for item in rows:
            if not isinstance(item, dict):
                continue
            name = str(item.get("key") or item.get("filename") or item.get("name") or "")
            if name:
                out[name] = item
        return out

    def candidate_urls(self, record_id: int, name: str, item: dict[str, Any]) -> list[str]:
        links = item.get("links") if isinstance(item.get("links"), dict) else {}
        candidates: list[str] = []
        for key in ("content", "download"):
            if links.get(key):
                candidates.append(str(links[key]))
        quoted = urllib.parse.quote(name, safe="")
        candidates.append(f"{self.base}/records/{record_id}/files/{quoted}/content")
        parsed = urllib.parse.urlparse(self.base)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        candidates.append(f"{origin}/records/{record_id}/files/{quoted}?download=1")
        return list(dict.fromkeys(candidates))

    def download_file(self, *, record_id: int, name: str, item: dict[str, Any]) -> dict[str, Any]:
        expected_size = remote_size(item)
        expected_md5 = parse_checksum(item.get("checksum"))
        if len(expected_md5) != 32:
            raise SystemExit(f"Zenodo public file lacks MD5 checksum: {name}")
        failures: list[str] = []
        for candidate, url in enumerate(self.candidate_urls(record_id, name, item), 1):
            for attempt in range(1, self.attempts + 1):
                total = 0
                sha = hashlib.sha256()
                md5 = hashlib.md5(usedforsecurity=False)
                buffer = bytearray() if expected_size <= SMALL_FILE_LIMIT else None
                next_progress = PROGRESS_BYTES
                request = urllib.request.Request(url, method="GET", headers={"User-Agent": "trinity-sidechain-zenodo-reconcile/2.0"})
                self.log("file_get_start", name=name, candidate=candidate, attempt=attempt, expected_size=expected_size, path=urllib.parse.urlparse(url).path)
                try:
                    with urllib.request.urlopen(request, timeout=self.timeout) as response:
                        while True:
                            chunk = response.read(CHUNK_BYTES)
                            if not chunk:
                                break
                            total += len(chunk)
                            sha.update(chunk)
                            md5.update(chunk)
                            if buffer is not None:
                                buffer.extend(chunk)
                            if total >= next_progress:
                                self.log("file_get_progress", name=name, candidate=candidate, attempt=attempt, bytes=total)
                                while next_progress <= total:
                                    next_progress += PROGRESS_BYTES
                    digest = sha.hexdigest()
                    md5_hex = md5.hexdigest()
                    if total == expected_size and md5_hex == expected_md5:
                        self.log("file_get_verified_metadata", name=name, bytes=total, md5=md5_hex, sha256=digest, candidate=candidate, attempt=attempt)
                        return {"bytes": total, "md5": md5_hex, "sha256": digest, "raw": bytes(buffer) if buffer is not None else None, "url": url}
                    failures.append(f"candidate={candidate} attempt={attempt} size={total}/{expected_size} md5={md5_hex}/{expected_md5}")
                    self.log("file_get_mismatch", name=name, candidate=candidate, attempt=attempt, bytes=total, md5=md5_hex)
                    break
                except urllib.error.HTTPError as exc:
                    retryable = exc.code in TRANSIENT_HTTP or exc.code == 404
                    failures.append(f"candidate={candidate} attempt={attempt} HTTP {exc.code}")
                    self.log("file_get_http_error", name=name, candidate=candidate, attempt=attempt, status=exc.code, retryable=retryable)
                    if not retryable:
                        break
                except OSError as exc:
                    failures.append(f"candidate={candidate} attempt={attempt} {exc!r}")
                    self.log("file_get_error", name=name, candidate=candidate, attempt=attempt, error=repr(exc))
                if attempt < self.attempts:
                    time.sleep(min(self.delay * attempt, 20))
        raise SystemExit(f"public Zenodo readback failed for {name}: {'; '.join(failures[-8:])}")


def parse_json_raw(raw: bytes | None, name: str) -> dict[str, Any]:
    if raw is None:
        raise SystemExit(f"expected buffered small JSON file: {name}")
    try:
        value = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid public JSON file: {name}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"public JSON file is not an object: {name}")
    return value


def validate_legacy_recovery(public: dict[str, Any], local: dict[str, Any]) -> str:
    public_copy = dict(public)
    local_copy = dict(local)
    generated = str(public_copy.pop("generated_at", ""))
    local_copy.pop("generated_at", None)
    if public_copy != local_copy:
        raise SystemExit("public RECOVERY-VERIFICATION semantics differ from current cold-verified source build beyond generated_at")
    if not generated:
        raise SystemExit("public RECOVERY-VERIFICATION missing legacy generated_at")
    try:
        parsed = dt.datetime.fromisoformat(generated.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SystemExit("public RECOVERY-VERIFICATION generated_at is not ISO-8601") from exc
    if parsed.tzinfo is None:
        raise SystemExit("public RECOVERY-VERIFICATION generated_at lacks timezone")
    if parsed.astimezone(dt.timezone.utc) > dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=5):
        raise SystemExit("public RECOVERY-VERIFICATION generated_at is implausibly in the future")
    return generated


def validate_public_deposit(public: dict[str, Any], local_package: dict[str, Any], downloaded: dict[str, dict[str, Any]]) -> str:
    for key in ("schema", "version", "source_release_tag", "source_commit_sha", "metadata", "rights_boundary"):
        if public.get(key) != local_package.get(key):
            raise SystemExit(f"public SIDECHAIN-ZENODO-DEPOSIT field mismatch: {key}")
    rows = public.get("inventory")
    if not isinstance(rows, list):
        raise SystemExit("public SIDECHAIN-ZENODO-DEPOSIT inventory missing")
    expected_core = {"README.md", "RECOVERY-VERIFICATION.json", "SOURCE-BINDING.json", next(name for name in downloaded if name.endswith(".tar.gz")), next(name for name in downloaded if name.endswith(".tar.gz.sha256"))}
    declared: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not row.get("name"):
            raise SystemExit("invalid public deposit inventory row")
        declared[str(row["name"])] = row
    if set(declared) != expected_core:
        raise SystemExit(f"public deposit core inventory set mismatch: {sorted(declared)}")
    normalized_rows: list[dict[str, Any]] = []
    for name in sorted(expected_core):
        row = declared[name]
        observed = downloaded[name]
        if int(row.get("bytes", -1)) != int(observed["bytes"]) or str(row.get("sha256") or "") != observed["sha256"]:
            raise SystemExit(f"public deposit inventory digest mismatch: {name}")
        normalized_rows.append({"name": name, "bytes": int(observed["bytes"]), "sha256": observed["sha256"]})
    package_identity = hashlib.sha256(json.dumps(normalized_rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if str(public.get("package_identity_sha256") or "") != package_identity:
        raise SystemExit("public deposit package_identity_sha256 does not recompute")
    return package_identity


def validate_sha256s(raw: bytes | None, downloaded: dict[str, dict[str, Any]]) -> None:
    if raw is None:
        raise SystemExit("public SHA256SUMS not buffered")
    rows: dict[str, str] = {}
    for line in raw.decode("utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        name = name.strip().lstrip("*")
        if len(digest) != 64:
            raise SystemExit(f"invalid public SHA256SUMS digest: {name}")
        rows[name] = digest
    expected_names = set(downloaded) - {"SHA256SUMS"}
    if set(rows) != expected_names:
        raise SystemExit(f"public SHA256SUMS file set mismatch missing={sorted(expected_names-set(rows))} unexpected={sorted(set(rows)-expected_names)}")
    for name in sorted(expected_names):
        if rows[name] != downloaded[name]["sha256"]:
            raise SystemExit(f"public SHA256SUMS mismatch: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deposit-dir", required=True)
    parser.add_argument("--state", default=str(DEFAULT_STATE.relative_to(ROOT)))
    parser.add_argument("--api-base", default=os.getenv("ZENODO_API_BASE", DEFAULT_API))
    parser.add_argument("--attempts", type=int, default=int(os.getenv("ZENODO_PUBLIC_ATTEMPTS", "5")))
    parser.add_argument("--timeout", type=int, default=int(os.getenv("ZENODO_PUBLIC_TIMEOUT_SECONDS", "1200")))
    parser.add_argument("--retry-delay", type=int, default=int(os.getenv("ZENODO_PUBLIC_RETRY_DELAY_SECONDS", "5")))
    args = parser.parse_args()

    deposit = (ROOT / args.deposit_dir).resolve()
    if ROOT not in deposit.parents or not deposit.is_dir():
        raise SystemExit("deposit directory must exist inside repository")
    local = verify_local(deposit)
    local_package = local["package"]
    local_inventory = local["inventory"]
    version_id = str(local_package.get("version") or "")
    if not version_id:
        raise SystemExit("local DOI package missing version")

    verifier = PublicVerifier(
        token=os.getenv("ZENODO_ACCESS_TOKEN", "").strip(),
        api_base=args.api_base,
        debug_path=deposit / "DEBUG-PUBLISHED-RECONCILE-V2.jsonl",
        attempts=args.attempts,
        timeout=args.timeout,
        delay=args.retry_delay,
    )
    verifier.log("reconcile_start", version=version_id, local_package_identity=local_package.get("package_identity_sha256"))
    deposition = verifier.find_deposition(version_id)
    record_id, record = verifier.public_record(deposition)
    if rec_meta(record).get("title") != TITLE:
        raise SystemExit("public Zenodo title mismatch")
    public_version = rec_version(record)
    if public_version and public_version != version_id:
        raise SystemExit(f"public Zenodo version mismatch {public_version} != {version_id}")
    public_doi = rec_doi(record) or rec_doi(deposition)
    if public_doi != rec_doi(deposition):
        raise SystemExit(f"public/deposition DOI mismatch {public_doi} != {rec_doi(deposition)}")

    remote = verifier.files(record)
    expected_names = set(local_inventory)
    if set(remote) != expected_names:
        raise SystemExit(f"public Zenodo file set mismatch missing={sorted(expected_names-set(remote))} unexpected={sorted(set(remote)-expected_names)}")

    downloaded: dict[str, dict[str, Any]] = {}
    for name in sorted(remote):
        downloaded[name] = verifier.download_file(record_id=record_id, name=name, item=remote[name])

    stable_names = {name for name in expected_names if name not in {"RECOVERY-VERIFICATION.json", "SIDECHAIN-ZENODO-DEPOSIT.json", "SHA256SUMS"}}
    for name in sorted(stable_names):
        if downloaded[name]["bytes"] != local_inventory[name]["bytes"] or downloaded[name]["sha256"] != local_inventory[name]["sha256"]:
            raise SystemExit(f"public deterministic file differs from immutable-source rebuild: {name}")
        verifier.log("deterministic_file_exact", name=name, sha256=downloaded[name]["sha256"])

    public_recovery = parse_json_raw(downloaded["RECOVERY-VERIFICATION.json"]["raw"], "RECOVERY-VERIFICATION.json")
    local_recovery = json.loads((deposit / "RECOVERY-VERIFICATION.json").read_text(encoding="utf-8"))
    generated_at = validate_legacy_recovery(public_recovery, local_recovery)
    verifier.log("legacy_recovery_semantics_verified", generated_at=generated_at, public_sha256=downloaded["RECOVERY-VERIFICATION.json"]["sha256"])

    public_deposit = parse_json_raw(downloaded["SIDECHAIN-ZENODO-DEPOSIT.json"]["raw"], "SIDECHAIN-ZENODO-DEPOSIT.json")
    public_package_identity = validate_public_deposit(public_deposit, local_package, downloaded)
    verifier.log("public_package_identity_verified", package_identity_sha256=public_package_identity)

    validate_sha256s(downloaded["SHA256SUMS"]["raw"], downloaded)
    verifier.log("public_sha256s_verified", entries=len(downloaded) - 1, sha256=downloaded["SHA256SUMS"]["sha256"])

    state_path = (ROOT / args.state).resolve()
    if ROOT not in state_path.parents:
        raise SystemExit("state path must be inside repository")
    state = {
        "schema": "trinity-accord/chronicle-sidechain-zenodo-state/v1",
        "updated_at": now(),
        "latest_version": version_id,
        "source_release_tag": local_package["source_release_tag"],
        "source_commit_sha": local_package["source_commit_sha"],
        "package_identity_sha256": public_package_identity,
        "local_rebuild_package_identity_sha256": local_package.get("package_identity_sha256"),
        "legacy_generated_at": generated_at,
        "legacy_nondeterministic_builder_field_reconciled": True,
        "deposition_id": int(deposition.get("id")),
        "record_id": record_id,
        "doi": public_doi,
        "concept_doi": rec_concept_doi(record) or rec_concept_doi(deposition),
        "api_base": args.api_base,
        "remote_full_readback_sha256_verified": True,
        "remote_readback_surface": "public_records_api",
        "public_record_api": f"{args.api_base.rstrip('/')}/records/{record_id}",
        "published_reconcile": True,
        "verified_file_count": len(downloaded),
        "public_file_sha256": {name: downloaded[name]["sha256"] for name in sorted(downloaded)},
    }
    write_json(state_path, state)
    print(json.dumps(state, indent=2, sort_keys=True))
    output = os.getenv("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as handle:
            handle.write(f"doi={state['doi']}\nconcept_doi={state['concept_doi']}\nrecord_id={record_id}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
