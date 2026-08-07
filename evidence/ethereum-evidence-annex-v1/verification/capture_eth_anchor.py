#!/usr/bin/env python3
"""Capture Ethereum transaction/receipt/block JSON without upgrading proof status.

This helper intentionally uses only the Python standard library.
It records what an RPC endpoint returned plus hashes of the captured JSON.
Those captures are evidence inputs, not independent inclusion/finality proofs.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, urllib.request
from datetime import datetime, timezone

def rpc(url: str, method: str, params: list):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params},separators=(",",":")).encode()
    req=urllib.request.Request(url,data=body,headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        payload=json.loads(r.read())
    if payload.get("error"):
        raise RuntimeError(f"{method}: {payload['error']}")
    if payload.get("result") is None:
        raise RuntimeError(f"{method}: null result")
    return payload["result"]

def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()

def write_json(path: pathlib.Path, obj):
    data=canonical_bytes(obj)
    path.write_bytes(data)
    return {"path":path.name,"bytes":len(data),"sha256":hashlib.sha256(data).hexdigest()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--rpc",required=True)
    ap.add_argument("--tx",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    txh=args.tx.lower()
    if not (txh.startswith("0x") and len(txh)==66):
        raise SystemExit("invalid transaction hash")
    out=pathlib.Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    tx=rpc(args.rpc,"eth_getTransactionByHash",[txh])
    receipt=rpc(args.rpc,"eth_getTransactionReceipt",[txh])
    if tx.get("hash","").lower()!=txh or receipt.get("transactionHash","").lower()!=txh:
        raise SystemExit("RPC returned mismatched transaction hash")
    block_hash=tx.get("blockHash")
    if not block_hash or receipt.get("blockHash")!=block_hash:
        raise SystemExit("transaction/receipt blockHash mismatch")
    block=rpc(args.rpc,"eth_getBlockByHash",[block_hash,False])
    if block.get("hash")!=block_hash:
        raise SystemExit("RPC returned mismatched block hash")
    records=[
      write_json(out/"transaction.json",tx),
      write_json(out/"receipt.json",receipt),
      write_json(out/"block.json",block),
    ]
    manifest={
      "schema":"trinityaccord.ethereum-rpc-capture.v1",
      "tx_hash":txh,
      "chain_id":rpc(args.rpc,"eth_chainId",[]),
      "captured_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
      "block_number":tx.get("blockNumber"),
      "block_hash":block_hash,
      "block_timestamp":block.get("timestamp"),
      "records":records,
      "verification_status":{
        "rpc_capture":"PASS",
        "execution_inclusion":"UNVERIFIED",
        "consensus_finality":"UNVERIFIED"
      },
      "warning":"RPC capture is provider-returned evidence. It is not, by itself, an offline Merkle inclusion proof or PoS finality proof."
    }
    write_json(out/"capture-manifest.json",manifest)
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    main()
