#!/usr/bin/env python3
"""Serve archived EIP-4844 blobs through the standard Beacon blobs API.

The OP Stack batch decoder intentionally accepts a Beacon API endpoint.  Old
blobs are no longer guaranteed to be available from ordinary consensus nodes,
so this adapter fetches them from redundant Blobscan storage references and
caches the exact 131072-byte field-element payload.  The decoder remains the
trust boundary: it recomputes each KZG commitment and compares its EIP-4844
versioned hash with the hash committed by the signed L1 transaction.

Every fetched byte string is recorded in a deterministic provenance ledger.
The adapter never substitutes a blob and fails closed if the requested hash,
size, or storage metadata is inconsistent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BLOB_BYTES = 131072
GENESIS_TIME = "1606824023"
SECONDS_PER_SLOT = "12"


def stable_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_hash(value: str) -> str:
    value = value.lower()
    if not value.startswith("0x") or len(value) != 66:
        raise ValueError(f"invalid EIP-4844 versioned hash: {value}")
    int(value[2:], 16)
    if not value.startswith("0x01"):
        raise ValueError(f"unsupported blob hash version: {value[:4]}")
    return value


class Archive:
    def __init__(self, cache: pathlib.Path, api: str, timeout: int = 60):
        self.cache = cache
        self.api = api.rstrip("/")
        self.timeout = timeout
        self.lock = threading.Lock()
        self.cache.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.cache / "ARCHIVE-PROVENANCE.jsonl"

    def request(self, url: str) -> tuple[bytes, dict[str, str]]:
        req = urllib.request.Request(url, headers={"user-agent": "trinity-accord-base-blob-proof/1.0"})
        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            data = response.read()
            headers = {key.lower(): value for key, value in response.headers.items()}
        return data, headers

    def metadata(self, versioned_hash: str) -> tuple[dict, str, str]:
        url = f"{self.api}/blobs/{versioned_hash}"
        raw, _ = self.request(url)
        value = json.loads(raw)
        actual = normalize_hash(value.get("versionedHash") or value.get("versioned_hash") or versioned_hash)
        if actual != versioned_hash:
            raise ValueError(f"Blobscan metadata hash mismatch expected={versioned_hash} actual={actual}")
        return value, url, hashlib.sha256(raw).hexdigest()

    @staticmethod
    def storage_urls(metadata: dict) -> list[str]:
        values = metadata.get("dataStorageReferences") or metadata.get("data_storage_references") or []
        out: list[str] = []
        for item in values:
            if not isinstance(item, dict):
                continue
            url = item.get("url")
            if isinstance(url, str) and url.startswith(("https://", "http://")) and url not in out:
                out.append(url)
        # Blobscan's stable public IPFS gateway is deterministic from its CID.
        ipfs = metadata.get("ipfs")
        if isinstance(ipfs, str) and ipfs:
            url = f"https://blobscan.com/ipfs/{ipfs}"
            if url not in out:
                out.append(url)
        return out

    def _record(self, row: dict) -> None:
        with self.lock:
            with self.ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(stable_json(row) + "\n")

    def get(self, raw_hash: str) -> bytes:
        versioned_hash = normalize_hash(raw_hash)
        target = self.cache / f"{versioned_hash[2:]}.blob"
        if target.exists():
            data = target.read_bytes()
            if len(data) != BLOB_BYTES:
                raise ValueError(f"cached blob has wrong size: {target}")
            return data

        metadata, metadata_url, metadata_sha = self.metadata(versioned_hash)
        urls = self.storage_urls(metadata)
        if not urls:
            raise ValueError(f"no archived data URL for {versioned_hash}")
        errors: list[str] = []
        for url in urls:
            started = time.monotonic()
            try:
                data, headers = self.request(url)
                if len(data) != BLOB_BYTES:
                    raise ValueError(f"blob bytes={len(data)} expected={BLOB_BYTES}")
                sha = hashlib.sha256(data).hexdigest()
                with self.lock:
                    if not target.exists():
                        target.write_bytes(data)
                self._record(
                    {
                        "event": "blob_archived",
                        "versioned_hash": versioned_hash,
                        "blob_sha256": sha,
                        "blob_bytes": len(data),
                        "kzg_commitment": metadata.get("commitment") or metadata.get("kzgCommitment"),
                        "kzg_proof": metadata.get("proof") or metadata.get("kzgProof"),
                        "metadata_url": metadata_url,
                        "metadata_sha256": metadata_sha,
                        "storage_url": url,
                        "storage_etag": headers.get("etag"),
                        "elapsed_ms": round((time.monotonic() - started) * 1000),
                    }
                )
                return data
            except Exception as exc:  # try every advertised redundant store
                errors.append(f"{url}: {exc!r}")
        raise RuntimeError(f"all archived stores failed for {versioned_hash}: {'; '.join(errors)}")


class Handler(BaseHTTPRequestHandler):
    archive: Archive

    def log_message(self, fmt: str, *args: object) -> None:
        print("[BLOB ARCHIVE] " + (fmt % args), flush=True)

    def json_response(self, value: object, status: int = 200) -> None:
        raw = (stable_json(value) + "\n").encode()
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/eth/v1/beacon/genesis":
            self.json_response({"data": {"genesis_time": GENESIS_TIME}})
            return
        if parsed.path == "/eth/v1/config/spec":
            self.json_response({"data": {"SECONDS_PER_SLOT": SECONDS_PER_SLOT}})
            return
        prefix = "/eth/v1/beacon/blobs/"
        if parsed.path.startswith(prefix):
            query = urllib.parse.parse_qs(parsed.query)
            hashes = query.get("versioned_hashes", [])
            if not hashes:
                self.json_response({"code": 400, "message": "versioned_hashes is required"}, 400)
                return
            try:
                blobs = [{"blob": "0x" + self.archive.get(item).hex()} for item in hashes]
                self.json_response({"data": blobs})
            except Exception as exc:
                self.json_response({"code": 502, "message": str(exc)}, 502)
            return
        self.json_response({"code": 404, "message": "not found"}, 404)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=pathlib.Path, required=True)
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5052)
    parser.add_argument("--api", default=os.getenv("BLOBSCAN_API", "https://api.blobscan.com"))
    parser.add_argument("--timeout", type=int, default=60)
    args = parser.parse_args()
    Handler.archive = Archive(args.cache, args.api, args.timeout)
    server = ThreadingHTTPServer((args.listen, args.port), Handler)
    print(f"[BLOB ARCHIVE READY] http://{args.listen}:{args.port} cache={args.cache}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
