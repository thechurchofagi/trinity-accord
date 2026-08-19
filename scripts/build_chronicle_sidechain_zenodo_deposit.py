#!/usr/bin/env python3
"""Build a DOI-ready cold-recovery deposit for Chronicle sidechain evidence.

The input is an already downloaded immutable GitHub Release archive plus its
SHA-256 sidecar and a cold-extracted, offline-verified evidence tree.  The
builder never contacts GitHub or Zenodo; it only binds exact bytes into a
small deterministic deposit directory with machine-readable recovery state.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import shutil
import sys
from typing import Any


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inventory(paths: list[pathlib.Path], root: pathlib.Path) -> list[dict[str, Any]]:
    rows=[]
    for path in sorted(paths, key=lambda p:p.name):
        rows.append({"name":path.name,"bytes":path.stat().st_size,"sha256":sha256_file(path)})
    return rows


def read_json(path: pathlib.Path) -> dict[str, Any]:
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--archive-sha256", required=True)
    ap.add_argument("--extracted-root", required=True)
    ap.add_argument("--source-tag", required=True)
    ap.add_argument("--source-sha", required=True)
    ap.add_argument("--output-dir", required=True)
    args=ap.parse_args()

    archive=pathlib.Path(args.archive).resolve()
    sidecar=pathlib.Path(args.archive_sha256).resolve()
    extracted=pathlib.Path(args.extracted_root).resolve()
    out=pathlib.Path(args.output_dir).resolve()
    if not archive.is_file() or not sidecar.is_file():
        raise SystemExit("source archive or SHA-256 sidecar missing")
    if not extracted.is_dir():
        raise SystemExit("cold-extracted source root missing")
    if len(args.source_sha)!=40 or any(c not in "0123456789abcdef" for c in args.source_sha):
        raise SystemExit("source SHA must be 40 lowercase hex characters")
    expected_short=args.source_sha[:12]
    if not args.source_tag.endswith(expected_short):
        raise SystemExit("source tag is not bound to source commit short SHA")

    sidecar_line=sidecar.read_text(encoding="utf-8").strip().split()
    if not sidecar_line or len(sidecar_line[0])!=64:
        raise SystemExit("invalid source archive SHA-256 sidecar")
    expected=sidecar_line[0].lower(); actual=sha256_file(archive)
    if actual!=expected:
        raise SystemExit(f"source archive SHA-256 mismatch expected={expected} actual={actual}")

    evidence=extracted/"evidence-v2"
    offline=read_json(evidence/"OFFLINE-VERIFICATION.json")
    coverage=read_json(evidence/"HISTORICAL-PAYLOAD-COVERAGE.json")
    anchor=read_json(evidence/"ANCHOR-REQUEST.json")
    summary=read_json(extracted/"SUMMARY.json")
    if offline.get("pass") is not True:
        raise SystemExit("cold-extracted OFFLINE-VERIFICATION is not PASS")
    if int(offline.get("records",-1))!=217 or int(offline.get("l2_records_checked",-1))!=217:
        raise SystemExit("cold-extracted L2 verification is not 217/217")
    total=int(coverage.get("total_unique_ipfs_roots",-1))
    exact=int(coverage.get("exact_verified_roots",-1))
    unresolved=int(coverage.get("unresolved_roots",-1))
    if total<1 or exact<0 or unresolved<0 or exact+unresolved!=total:
        raise SystemExit("historical payload coverage accounting mismatch")
    unresolved_cids=sorted(str(x.get("root_cid")) for x in coverage.get("unresolved",[]) if isinstance(x,dict) and x.get("root_cid"))
    if len(unresolved_cids)!=unresolved:
        raise SystemExit("unresolved CID inventory count mismatch")
    message_sha=str(anchor.get("message_sha256") or "")
    if len(message_sha)!=64 or any(c not in "0123456789abcdef" for c in message_sha):
        raise SystemExit("ANCHOR-REQUEST message_sha256 invalid")

    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    copied_archive=out/archive.name
    copied_sidecar=out/sidecar.name
    shutil.copy2(archive,copied_archive)
    shutil.copy2(sidecar,copied_sidecar)

    recovery={
        "schema":"trinity-accord/chronicle-sidechain-zenodo-recovery-verification/v1",
        "generated_at":dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00","Z"),
        "source_release_tag":args.source_tag,
        "source_commit_sha":args.source_sha,
        "source_archive_name":archive.name,
        "source_archive_sha256":actual,
        "cold_extract_offline_verification_pass":True,
        "records":217,
        "l2_records_checked":217,
        "car_total_unique_ipfs_roots":total,
        "car_exact_verified_roots":exact,
        "historical_payload_unresolved_roots":unresolved,
        "historical_payload_unresolved_cids":unresolved_cids,
        "anchor_message_sha256":message_sha,
        "summary_evidence_v2":summary.get("evidence_v2"),
        "boundary":"This deposit preserves the immutable sidechain evidence release byte-for-byte. Unresolved historical payloads are preserved as explicit gaps and are never promoted to verified content."
    }
    recovery_path=out/"RECOVERY-VERIFICATION.json"
    recovery_path.write_text(json.dumps(recovery,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    source_binding={
        "schema":"trinity-accord/chronicle-sidechain-source-binding/v1",
        "source_release_tag":args.source_tag,
        "source_commit_sha":args.source_sha,
        "source_archive_name":archive.name,
        "source_archive_sha256":actual,
        "anchor_message_sha256":message_sha,
    }
    (out/"SOURCE-BINDING.json").write_text(json.dumps(source_binding,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    readme=(
        "# Trinity Accord Chronicle Polygon + Base NFT Evidence v2 — Cold Recovery Deposit\n\n"
        f"Source GitHub Release: `{args.source_tag}`  \n"
        f"Source commit: `{args.source_sha}`  \n"
        f"Archive SHA-256: `{actual}`\n\n"
        "The archive is preserved byte-for-byte from the immutable GitHub Release. "
        "Before this deposit is built, the archive is cold-extracted and the repository's "
        "offline sidechain verifier must pass all 217 L2 transaction/receipt witnesses and "
        "all present exact-CID CARs. Historical payload coverage remains explicitly qualified; "
        f"this build records {exact}/{total} exact roots and {unresolved} unresolved roots.\n\n"
        "Recovery: verify `SHA256SUMS`, verify the original archive sidecar, extract the tar.gz, "
        "then execute `CHRONICLE_OUT=<extracted>/chronicle-sidechain-scan python3 scripts/verify-chronicle-sidechain-evidence.py` "
        "from a compatible copy of the Trinity Accord repository.\n"
    )
    (out/"README.md").write_text(readme,encoding="utf-8")

    core=[copied_archive,copied_sidecar,recovery_path,out/"SOURCE-BINDING.json",out/"README.md"]
    core_inv=inventory(core,out)
    package_identity=hashlib.sha256(json.dumps(core_inv,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    deposit={
        "schema":"trinity-accord/chronicle-sidechain-zenodo-deposit/v1",
        "version":expected_short,
        "source_release_tag":args.source_tag,
        "source_commit_sha":args.source_sha,
        "package_identity_sha256":package_identity,
        "inventory":core_inv,
        "metadata":{
            "title":"Trinity Accord Chronicle Polygon and Base NFT Evidence v2",
            "upload_type":"dataset",
            "description":"Cold-recovery mirror of the immutable Trinity Accord Chronicle Polygon/Base historical NFT evidence v2 release. Contains the original archive byte-for-byte plus cryptographic source binding and recovery-verification metadata. Exact historical IPFS payload coverage is qualified rather than overstated.",
            "creators":[{"name":"Trinity Accord"}],
            "version":expected_short,
            "keywords":["Trinity Accord","Polygon","Base","NFT","cryptographic evidence","IPFS","CAR","cold recovery"],
            "notes":"This is a non-amending preservation mirror. Mixed-rights publication requires an explicit operator acknowledgement before Zenodo publication."
        },
        "rights_boundary":"The archive may contain third-party NFT payloads. Building the DOI-ready package does not assert publication rights; external Zenodo publication is separately gated by an explicit versioned mixed-rights acknowledgement."
    }
    deposit_path=out/"SIDECHAIN-ZENODO-DEPOSIT.json"
    deposit_path.write_text(json.dumps(deposit,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    final_files=core+[deposit_path]
    sums=[]
    for path in sorted(final_files,key=lambda p:p.name):
        sums.append(f"{sha256_file(path)}  {path.name}")
    (out/"SHA256SUMS").write_text("\n".join(sums)+"\n",encoding="utf-8")

    final_inv=inventory(final_files+[out/"SHA256SUMS"],out)
    print(json.dumps({"status":"PASS","source_tag":args.source_tag,"source_sha":args.source_sha,"archive_sha256":actual,"records":217,"exact_roots":exact,"total_roots":total,"unresolved_roots":unresolved,"package_identity_sha256":package_identity,"files":final_inv},indent=2))
    return 0


if __name__=="__main__":
    try: raise SystemExit(main())
    except KeyboardInterrupt: raise SystemExit(130)
