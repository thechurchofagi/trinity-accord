#!/usr/bin/env python3
"""Fail-closed offline verifier for Ethereum Proof-Carrying Evidence Annex v1."""
from __future__ import annotations
import hashlib, json, pathlib, sys

ANNEX_DIR=pathlib.Path(__file__).resolve().parents[1]
REPO_ROOT=ANNEX_DIR.parents[1]
MANIFEST=ANNEX_DIR/"ANNEX-MANIFEST.json"

def sha256_file(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    failures=[]
    checks=[]
    try:
        data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"result":"FAIL","failures":[f"manifest parse: {exc}"]},indent=2))
        return 1

    if data.get("schema")!="trinityaccord.ethereum-proof-carrying-evidence-annex.v1":
        failures.append("unexpected schema")
    if data.get("network",{}).get("chain_id")!=1:
        failures.append("network chain_id must be 1")
    boundary=data.get("authority_boundary",{})
    if boundary.get("canonical_authority")!="three Bitcoin Originals only":
        failures.append("canonical authority boundary changed")
    if boundary.get("no_authority_escalation") is not True:
        failures.append("no_authority_escalation must be true")

    anchors=data.get("anchors")
    if not isinstance(anchors,list) or not anchors:
        failures.append("anchors missing")
        anchors=[]
    txs=[a.get("tx_hash") for a in anchors]
    if len(txs)!=len(set(txs)):
        failures.append("duplicate transaction hash")
    if len(anchors)!=10:
        failures.append(f"expected 10 audited non-NFT anchors, found {len(anchors)}")

    byte_pass=True
    for a in anchors:
        tx=a.get("tx_hash","")
        if not (isinstance(tx,str) and tx.startswith("0x") and len(tx)==66):
            failures.append(f"{a.get('id')}: invalid tx hash")
        payloads=a.get("payloads",[])
        if not payloads:
            failures.append(f"{tx}: no preserved payload mapping")
            byte_pass=False
        for p in payloads:
            rel=p.get("path")
            fp=REPO_ROOT/rel if rel else None
            result={"tx_hash":tx,"path":rel}
            if not fp or not fp.is_file():
                result["status"]="FAIL"
                result["reason"]="missing"
                failures.append(f"{tx}: missing {rel}")
                byte_pass=False
            else:
                size=fp.stat().st_size
                digest=sha256_file(fp)
                result.update({"size":size,"sha256":digest})
                if size!=p.get("size") or digest!=p.get("sha256"):
                    result["status"]="FAIL"
                    result["reason"]="size_or_sha256_mismatch"
                    failures.append(f"{tx}: byte mismatch {rel}")
                    byte_pass=False
                else:
                    result["status"]="PASS"
            checks.append(result)

    # Proof discipline: this v1 must not silently claim cryptographic L2/L3.
    for a in anchors:
        proof=a.get("proof_status",{})
        if proof.get("L2_EXECUTION_INCLUSION")=="PASS":
            failures.append(f"{a.get('tx_hash')}: L2 PASS forbidden without preserved proof object validation")
        if proof.get("L3_CONSENSUS_FINALITY")=="PASS":
            failures.append(f"{a.get('tx_hash')}: L3 PASS forbidden without preserved finality validation")

    summary={
      "schema":"trinityaccord.ethereum-annex-offline-verification.v1",
      "result":"PASS" if not failures else "FAIL",
      "L1_BYTE_INTEGRITY":"PASS" if byte_pass and not failures else "FAIL",
      "L2_EXECUTION_INCLUSION":"UNVERIFIED",
      "L3_CONSENSUS_FINALITY":"UNVERIFIED",
      "anchors":len(anchors),
      "payload_checks":len(checks),
      "checks":checks,
      "failures":failures,
      "claim_boundary":"PASS means preserved repository byte bindings only. It does not imply Ethereum execution inclusion or PoS finality."
    }
    print(json.dumps(summary,indent=2,ensure_ascii=False))
    return 0 if not failures else 1

if __name__=="__main__":
    sys.exit(main())
