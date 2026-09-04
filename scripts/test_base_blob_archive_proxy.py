#!/usr/bin/env python3
import hashlib
import json
import pathlib
import tempfile

from base_blob_archive_proxy import Archive, BLOB_BYTES, normalize_hash


def main():
    versioned_hash = "0x01" + "22" * 31
    blob = b"\0" * BLOB_BYTES
    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        archive = Archive(root, "https://metadata.invalid")
        metadata = {
            "versionedHash": versioned_hash,
            "commitment": "0x" + "11" * 48,
            "proof": "0x" + "33" * 48,
            "dataStorageReferences": [{"url": "https://store.invalid/blob"}],
        }
        archive.metadata = lambda _: (metadata, "https://metadata.invalid/blob", hashlib.sha256(json.dumps(metadata).encode()).hexdigest())
        archive.request = lambda _: (blob, {"etag": "test"})
        assert archive.get(versioned_hash) == blob
        assert archive.get(versioned_hash) == blob
        rows = archive.ledger_path.read_text().splitlines()
        assert len(rows) == 1
        row = json.loads(rows[0])
        assert row["versioned_hash"] == versioned_hash
        assert row["blob_sha256"] == hashlib.sha256(blob).hexdigest()
        assert row["blob_bytes"] == BLOB_BYTES
        assert normalize_hash(versioned_hash.upper().replace("0X", "0x")) == versioned_hash
    print("base blob archive proxy tests: PASS")


if __name__ == "__main__":
    main()
