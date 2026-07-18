#!/usr/bin/env python3
"""Verify committed retired Gateway v1 builder archives without executing them."""
from __future__ import annotations
import argparse, hashlib, json, sys, tarfile
from pathlib import Path, PurePosixPath

REQUIRED_REPLACEMENT = {
    "contract": "/api/record-chain-intake-gateway.v1.json",
    "builder": "/downloads/record-chain-builder.mjs",
    "preflight": "/record-chain/preflight",
    "submit": "/record-chain/submit",
}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def safe_member(member: tarfile.TarInfo) -> bool:
    path = PurePosixPath(member.name)
    if path.is_absolute() or ".." in path.parts or not member.name:
        return False
    return not (member.issym() or member.islnk() or member.isdev() or member.isfifo())

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--site-dir", type=Path)
    args=parser.parse_args()
    root=(args.site_dir or Path(__file__).resolve().parents[1]).resolve()
    manifest_path=root / "api/formal-builder-bundles.v1.json"
    helper=root / "builder-bundles/download_and_run_builder_bundle.py"
    errors=[]
    try:
        doc=json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: cannot read retired bundle manifest: {exc}")
        return 1
    for key in ("historical_archive_only","do_not_use_for_new_public_submissions","all_bundles_retired"):
        if doc.get(key) is not True: errors.append(f"top-level {key} must be true")
    if doc.get("status") != "historical_archive_only": errors.append("top-level status must be historical_archive_only")
    if doc.get("replacement") != "/api/agent-first-contact.json": errors.append("top-level replacement must be current First Contact")
    bundles=doc.get("bundles")
    if not isinstance(bundles,dict) or not bundles: errors.append("bundles must be a non-empty object"); bundles={}
    for route, meta in bundles.items():
        if meta.get("route_id") != route: errors.append(f"{route}: route_id mismatch")
        if meta.get("status") != "historical_archive_only" or meta.get("retired") is not True or meta.get("do_not_use_for_new_public_submissions") is not True:
            errors.append(f"{route}: retirement flags incomplete")
        if meta.get("retired_replacement") != REQUIRED_REPLACEMENT: errors.append(f"{route}: current replacement drifted")
        archive=root / "builder-bundles" / str(meta.get("archive_name",""))
        archive_url=str(meta.get("archive_url",""))
        if archive_url != f"/builder-bundles/{archive.name}": errors.append(f"{route}: archive_url mismatch")
        if not archive.is_file(): errors.append(f"{route}: missing archive {archive.name}"); continue
        raw=archive.read_bytes()
        if sha256(raw) != meta.get("sha256"): errors.append(f"{route}: archive sha256 mismatch")
        if len(raw) != meta.get("size_bytes"): errors.append(f"{route}: archive size mismatch")
        manifest_url=str(meta.get("manifest_url",""))
        bundle_manifest=root / manifest_url.lstrip("/")
        if not bundle_manifest.is_file(): errors.append(f"{route}: missing bundle manifest"); continue
        try: bm=json.loads(bundle_manifest.read_text(encoding="utf-8"))
        except Exception as exc: errors.append(f"{route}: invalid bundle manifest: {exc}"); continue
        if bm.get("archive") != archive.name or bm.get("archive_sha256") != sha256(raw) or bm.get("archive_size_bytes") != len(raw):
            errors.append(f"{route}: bundle manifest archive binding mismatch")
        declared={item.get("path"):item for item in bm.get("files",[]) if isinstance(item,dict)}
        try:
            with tarfile.open(archive,"r:gz") as tar:
                members=[m for m in tar.getmembers() if m.isfile()]
                for member in tar.getmembers():
                    if not safe_member(member): errors.append(f"{route}: unsafe tar member {member.name}")
                actual={m.name for m in members}
                if actual != set(declared): errors.append(f"{route}: tar file set differs from manifest")
                for member in members:
                    fileobj=tar.extractfile(member)
                    data=fileobj.read() if fileobj else b""
                    item=declared.get(member.name,{})
                    if sha256(data) != item.get("sha256") or len(data) != item.get("size_bytes"):
                        errors.append(f"{route}: member binding mismatch {member.name}")
        except Exception as exc: errors.append(f"{route}: cannot inspect archive: {exc}")
        if bm.get("entrypoint") not in declared: errors.append(f"{route}: entrypoint absent from manifest files")
    if not helper.is_file(): errors.append("missing public retired-bundle helper")
    else:
        text=helper.read_text(encoding="utf-8")
        for marker in ("--allow-historical-retired-bundle","REFUSED: all formal Gateway v1 builder bundles are retired","HISTORICAL OUTPUT ONLY — DO NOT SUBMIT"):
            if marker not in text: errors.append(f"public helper missing fail-closed marker {marker!r}")
    if errors:
        print("FAIL: retired builder bundle archive contract errors:")
        for error in errors: print("  -",error)
        return 1
    print(f"PASS: {len(bundles)} retired builder archives are immutable, safe, and fail closed")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
