#!/usr/bin/env python3
"""Capture fail-closed Polygon PoS -> Ethereum RootChain checkpoint proofs.

Proof chain per unique Polygon origin block:
  verified Polygon block hash -> Bor checkpoint Merkle proof -> Ethereum RootChain
  NewHeaderBlock receipt -> Ethereum receiptsRoot -> Ethereum block header/hash.

RPC endpoints are discovery/witness sources only. Acceptance is local hash/trie equality.
All network attempts and cryptographic intermediate values are persisted to DEBUG.jsonl.
"""
import datetime
import hashlib
import json
import math
import os
import pathlib
import time
import urllib.error
import urllib.request

import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

SOURCE = pathlib.Path(os.getenv("CHRONICLE_SOURCE_DIR", "artifacts/chronicle-sidechain-scan"))
OUT = pathlib.Path(os.getenv("CHRONICLE_POLYGON_ETH_OUT", "artifacts/chronicle-polygon-ethereum-settlement"))
ROOTCHAIN = os.getenv("CHRONICLE_POLYGON_ROOTCHAIN", "0x86E4Dc95c7FBdBf52e33D563BbDB00823894C287").lower()
TIMEOUT = int(os.getenv("CHRONICLE_SETTLEMENT_HTTP_TIMEOUT_SECONDS", "45"))
RETRIES = int(os.getenv("CHRONICLE_SETTLEMENT_HTTP_RETRIES", "2"))
HEADER_STRIDE = 10_000


def endpoints(primary, fallbacks):
    out=[]
    for raw in (primary, fallbacks):
        for value in str(raw or "").replace("\n", ",").split(","):
            value=value.strip().rstrip("/")
            if value and value not in out:
                out.append(value)
    if not out:
        raise ValueError("no RPC endpoints configured")
    return out


RPC = {
    "ethereum": endpoints(os.getenv("ETH_RPC_URL"), os.getenv("CHRONICLE_ETH_RPC_FALLBACK_URLS") or "https://ethereum-rpc.publicnode.com,https://eth.drpc.org"),
    "polygon": endpoints(os.getenv("POLYGON_RPC_URL"), os.getenv("CHRONICLE_POLYGON_RPC_FALLBACK_URLS") or "https://polygon-bor-rpc.publicnode.com,https://polygon.drpc.org"),
}
PREFERRED={k:0 for k in RPC}
DEBUG = OUT / "DEBUG.jsonl"


def stable_json(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def debug(event, **fields):
    OUT.mkdir(parents=True, exist_ok=True)
    row={"ts":datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"),"event":event,**fields}
    with DEBUG.open("a", encoding="utf-8") as f:
        f.write(stable_json(row)+"\n")
    print("[POLYGON->ETH] "+event+" "+" ".join(f"{k}={v}" for k,v in fields.items()), flush=True)


def rpc(network, method, params):
    last=None
    for attempt in range(RETRIES+1):
        preferred=PREFERRED[network]
        order=list(range(preferred,len(RPC[network])))+list(range(0,preferred))
        for idx in order:
            payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            started=time.monotonic()
            req=urllib.request.Request(RPC[network][idx], data=payload, headers={"content-type":"application/json","user-agent":"trinity-accord-polygon-eth-proof/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                    raw=res.read(); data=json.loads(raw)
                if not isinstance(data,dict) or data.get("error"):
                    raise RuntimeError(f"JSON-RPC error {data.get('error') if isinstance(data,dict) else 'non-object'}")
                result=data.get("result")
                PREFERRED[network]=idx
                debug("rpc_ok", network=network, method=method, endpoint=idx+1, attempt=attempt+1, elapsed_ms=round((time.monotonic()-started)*1000), result_sha256=hashlib.sha256(stable_json(result).encode()).hexdigest())
                return result
            except Exception as e:
                last=e
                debug("rpc_error", network=network, method=method, endpoint=idx+1, attempt=attempt+1, elapsed_ms=round((time.monotonic()-started)*1000), error=repr(e))
        if attempt < RETRIES:
            time.sleep(min(2**attempt,5))
    raise RuntimeError(f"{network} {method} failed: {last}")


def h2i(v):
    if v is None: return 0
    return int(v,16) if isinstance(v,str) and v.startswith("0x") else int(v)


def h2b(v):
    if v is None: return b""
    s=str(v); s=s[2:] if s.startswith("0x") else s
    if len(s)%2: s="0"+s
    return bytes.fromhex(s)


def intb(v):
    n=h2i(v)
    return b"" if n==0 else n.to_bytes((n.bit_length()+7)//8,"big")


def word(n): return int(n).to_bytes(32,"big")

def selector(sig): return keccak(sig.encode())[:4]

CURRENT_SELECTOR=selector("currentHeaderBlock()")
HEADER_SELECTOR=selector("headerBlocks(uint256)")
NEW_HEADER_TOPIC="0x"+keccak(b"NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)").hex()


def eth_call(data, block="latest"):
    return rpc("ethereum","eth_call",[{"to":ROOTCHAIN,"data":"0x"+data.hex()},block])


def current_header_id():
    raw=h2b(eth_call(CURRENT_SELECTOR))
    if len(raw)<32: raise ValueError("currentHeaderBlock malformed response")
    value=int.from_bytes(raw[-32:],"big")
    if value<=0 or value%HEADER_STRIDE: raise ValueError(f"invalid current header id {value}")
    debug("rootchain_current_header", header_block_id=value)
    return value


def header_info(header_id):
    raw=h2b(eth_call(HEADER_SELECTOR+word(header_id)))
    if len(raw)<160: raise ValueError(f"headerBlocks({header_id}) short ABI response bytes={len(raw)}")
    slots=[raw[i:i+32] for i in range(0,160,32)]
    info={
        "header_block_id":header_id,
        "root":"0x"+slots[0].hex(),
        "start":int.from_bytes(slots[1],"big"),
        "end":int.from_bytes(slots[2],"big"),
        "created_at":int.from_bytes(slots[3],"big"),
        "proposer":"0x"+slots[4][-20:].hex(),
    }
    debug("rootchain_header", **info)
    return info


def find_header(target_block, current_id):
    lo,hi=1,current_id//HEADER_STRIDE
    steps=[]
    while lo<=hi:
        mid=(lo+hi)//2; hid=mid*HEADER_STRIDE; info=header_info(hid)
        steps.append({"lo":lo,"hi":hi,"mid":mid,"header_block_id":hid,"start":info["start"],"end":info["end"]})
        if info["start"]<=target_block<=info["end"]:
            debug("checkpoint_found", target_block=target_block, header_block_id=hid, search_steps=len(steps))
            return info,steps
        if target_block < info["start"]:
            hi=mid-1
        else:
            lo=mid+1
    raise ValueError(f"no RootChain checkpoint contains Polygon block {target_block}")


def zero_hash(height):
    value=b"\x00"*32
    for _ in range(height): value=keccak(value+value)
    return value


def merkle_root_power_of_two(leaves):
    if not leaves or len(leaves)&(len(leaves)-1): raise ValueError("expected power-of-two leaves")
    layer=list(leaves)
    while len(layer)>1:
        layer=[keccak(layer[i]+layer[i+1]) for i in range(0,len(layer),2)]
    return layer[0]


def bor_root(start,end):
    result=rpc("polygon","bor_getRootHash",[int(start),int(end)])
    root=h2b(result)
    if len(root)!=32: raise ValueError(f"bor_getRootHash({start},{end}) returned {len(root)} bytes")
    debug("bor_subtree_root", start=start, end=end, root="0x"+root.hex())
    return root


def polygon_block_proof(block_number,start,end):
    if not(start<=block_number<=end): raise ValueError("block outside checkpoint")
    count=end-start+1
    depth=math.ceil(math.log2(count)) if count>1 else 0
    target_index=block_number-start
    left_bound=0; right_bound=end-start; reversed_proof=[]
    for depth_index in range(depth):
        n_leaves=2**(depth-depth_index)
        pivot=left_bound+n_leaves//2-1
        if target_index>pivot:
            sibling=bor_root(start+left_bound,start+pivot)
            reversed_proof.append(sibling)
            debug("proof_sibling", block_number=block_number, depth=depth_index, side="left", sibling="0x"+sibling.hex(), range_start=start+left_bound, range_end=start+pivot)
            left_bound=pivot+1
        else:
            new_right=min(right_bound,pivot)
            expected_height=depth-(depth_index+1)
            if right_bound<=pivot:
                sibling=zero_hash(expected_height)
                debug("proof_sibling", block_number=block_number, depth=depth_index, side="right_zero", sibling="0x"+sibling.hex(), zero_height=expected_height)
            else:
                subtree_height=math.ceil(math.log2(right_bound-pivot))
                height_diff=expected_height-subtree_height
                remaining=bor_root(start+pivot+1,start+right_bound)
                fill=zero_hash(subtree_height)
                leaves=[fill for _ in range(2**height_diff)]
                leaves[0]=remaining
                sibling=merkle_root_power_of_two(leaves)
                debug("proof_sibling", block_number=block_number, depth=depth_index, side="right_padded", sibling="0x"+sibling.hex(), range_start=start+pivot+1, range_end=start+right_bound, subtree_height=subtree_height, height_diff=height_diff)
            reversed_proof.append(sibling)
            right_bound=new_right
    proof=list(reversed(reversed_proof))
    return proof


def verify_merkle(leaf,index,proof):
    value=leaf; i=index
    for sibling in proof:
        value=keccak(value+sibling) if i%2==0 else keccak(sibling+value)
        i//=2
    return value


def block_by_number(network, number, full=False):
    b=rpc(network,"eth_getBlockByNumber",[hex(number),bool(full)])
    if not b: raise ValueError(f"{network} block {number} missing")
    return b


def find_eth_block_near_timestamp(ts):
    latest_num=h2i(rpc("ethereum","eth_blockNumber",[]))
    lo,hi=0,latest_num; steps=0
    while lo<hi:
        mid=(lo+hi)//2; block=block_by_number("ethereum",mid,False); mts=h2i(block["timestamp"]); steps+=1
        debug("eth_timestamp_search", target_timestamp=ts, lo=lo, hi=hi, mid=mid, mid_timestamp=mts)
        if mts<ts: lo=mid+1
        else: hi=mid
    debug("eth_timestamp_candidate", target_timestamp=ts, block_number=lo, steps=steps)
    return lo


def find_checkpoint_log(info):
    candidate=find_eth_block_near_timestamp(info["created_at"])
    from_block=max(0,candidate-4); to_block=candidate+4
    id_topic="0x"+word(info["header_block_id"]).hex()
    logs=rpc("ethereum","eth_getLogs",[{"address":ROOTCHAIN,"fromBlock":hex(from_block),"toBlock":hex(to_block),"topics":[NEW_HEADER_TOPIC,None,id_topic]}])
    debug("checkpoint_log_candidates", header_block_id=info["header_block_id"], from_block=from_block, to_block=to_block, count=len(logs or []))
    valid=[]
    for log in logs or []:
        topics=log.get("topics") or []; data=h2b(log.get("data","0x"))
        if len(topics)!=4 or len(data)<96: continue
        start=int.from_bytes(data[0:32],"big"); end=int.from_bytes(data[32:64],"big"); root="0x"+data[64:96].hex()
        if start==info["start"] and end==info["end"] and root.lower()==info["root"].lower():
            valid.append(log)
    if len(valid)!=1: raise ValueError(f"checkpoint event exact-match count={len(valid)} for header {info['header_block_id']}")
    log=valid[0]
    block=block_by_number("ethereum",h2i(log["blockNumber"]),True)
    if h2i(block["timestamp"])!=info["created_at"]: raise ValueError("RootChain createdAt != Ethereum block timestamp")
    debug("checkpoint_log_exact", header_block_id=info["header_block_id"], ethereum_block=h2i(log["blockNumber"]), tx_hash=log["transactionHash"], log_index=h2i(log["logIndex"]))
    return log,block


def encode_log(log): return [h2b(log["address"]),[h2b(t) for t in log.get("topics",[])],h2b(log.get("data","0x"))]


def encode_receipt(rec):
    first=intb(rec["status"]) if rec.get("status") is not None else h2b(rec["root"])
    fields=[first,intb(rec["cumulativeGasUsed"]),h2b(rec["logsBloom"]),[encode_log(x) for x in rec.get("logs",[])]]
    typ=h2i(rec.get("type","0x0")); payload=rlp.encode(fields)
    return bytes([typ])+payload if typ else payload


def header_fields(block):
    fields=[h2b(block["parentHash"]),h2b(block["sha3Uncles"]),h2b(block["miner"]),h2b(block["stateRoot"]),h2b(block["transactionsRoot"]),h2b(block["receiptsRoot"]),h2b(block["logsBloom"]),intb(block["difficulty"]),intb(block["number"]),intb(block["gasLimit"]),intb(block["gasUsed"]),intb(block["timestamp"]),h2b(block["extraData"]),h2b(block["mixHash"]),h2b(block["nonce"])]
    for name,kind in [("baseFeePerGas","int"),("withdrawalsRoot","hex"),("blobGasUsed","int"),("excessBlobGas","int"),("parentBeaconBlockRoot","hex"),("requestsHash","hex")]:
        if block.get(name) is not None: fields.append(intb(block[name]) if kind=="int" else h2b(block[name]))
    return fields


def block_receipts(block):
    try:
        recs=rpc("ethereum","eth_getBlockReceipts",[block["hash"]])
        if isinstance(recs,list) and len(recs)==len(block["transactions"]):
            debug("receipt_source", ethereum_block=h2i(block["number"]), source="eth_getBlockReceipts", count=len(recs))
            return recs
    except Exception as e:
        debug("receipt_batch_unavailable", ethereum_block=h2i(block["number"]), error=repr(e))
    recs=[]
    for i,tx in enumerate(block["transactions"]):
        tx_hash=tx["hash"] if isinstance(tx,dict) else tx
        recs.append(rpc("ethereum","eth_getTransactionReceipt",[tx_hash]))
        debug("receipt_fetched", ethereum_block=h2i(block["number"]), tx_index=i, tx_hash=tx_hash)
    return recs


def checkpoint_receipt_proof(log, block):
    header_rlp=rlp.encode(header_fields(block)); computed_hash="0x"+keccak(header_rlp).hex()
    if computed_hash.lower()!=block["hash"].lower(): raise ValueError(f"Ethereum header hash mismatch computed={computed_hash} rpc={block['hash']}")
    receipts=block_receipts(block); trie=HexaryTrie(db={}); encoded=[]
    for i,rec in enumerate(receipts):
        er=encode_receipt(rec); encoded.append(er); trie[rlp.encode(i)]=er
    if trie.root_hash!=h2b(block["receiptsRoot"]): raise ValueError("Ethereum receipts trie root mismatch")
    target=h2i(log["transactionIndex"]); rec=receipts[target]
    if str(rec.get("transactionHash","")).lower()!=str(log["transactionHash"]).lower(): raise ValueError("checkpoint log/receipt transaction hash mismatch")
    matching=[x for x in rec.get("logs",[]) if h2i(x.get("logIndex"))==h2i(log["logIndex"]) and str(x.get("address","")).lower()==ROOTCHAIN]
    if len(matching)!=1: raise ValueError(f"checkpoint receipt log match count={len(matching)}")
    key=rlp.encode(target); proof=trie.get_proof(key)
    if HexaryTrie.get_from_proof(trie.root_hash,key,proof)!=encoded[target]: raise ValueError("local receipt proof self-check failed")
    proof_rlp=["0x"+rlp.encode(node).hex() for node in proof]
    debug("ethereum_receipt_proof", ethereum_block=h2i(block["number"]), block_hash=block["hash"], receipt_index=target, proof_nodes=len(proof_rlp), receipts_root=block["receiptsRoot"], header_rlp_sha256=hashlib.sha256(header_rlp).hexdigest())
    return {
        "ethereum_block_number":h2i(block["number"]),"ethereum_block_hash":block["hash"],"ethereum_block_timestamp":h2i(block["timestamp"]),
        "block_header_rlp":"0x"+header_rlp.hex(),"receipts_root":block["receiptsRoot"],"receipt_index":target,
        "receipt_rlp":"0x"+encoded[target].hex(),"mpt_key_rlp":"0x"+key.hex(),"receipt_proof_nodes_rlp":proof_rlp,
        "checkpoint_tx_hash":log["transactionHash"],"checkpoint_log_index":h2i(log["logIndex"]),
    }


def polygon_checkpoint_leaf(rec):
    """Recompute the exact Bor checkpoint leaf from an already verified L2 witness.

    Bor's GetRootHash does *not* use blockHash as a Merkle leaf.  It uses
    keccak256(bytes32(number) || bytes32(timestamp) || txRoot || receiptRoot).
    The witness block header is re-hashed here again so neither RPC nor metadata
    can silently substitute any of those four leaf fields.
    """
    origin=rec.get("origin") or {}
    chain=rec.get("chain") or {}
    bn=int(origin["block_number"]); expected_hash=str(origin["block_hash"]).lower()
    witness_file=SOURCE/"evidence-v2"/"l2"/str(chain["name"])/str(rec["contract"])/str(rec["token_id"])/"witness.json"
    w=json.loads(witness_file.read_text())
    header_rlp=h2b(w["block_header_rlp"]); fields=rlp.decode(header_rlp)
    if len(fields)<12: raise ValueError(f"Polygon header has too few RLP fields block={bn} fields={len(fields)}")
    local_hash="0x"+keccak(header_rlp).hex()
    if local_hash.lower()!=expected_hash: raise ValueError(f"Polygon witness block hash mismatch block={bn} computed={local_hash} expected={expected_hash}")
    if str(w.get("block_hash","")).lower()!=expected_hash: raise ValueError(f"Polygon witness declared block hash mismatch block={bn}")
    header_number=int.from_bytes(fields[8],"big") if fields[8] else 0
    header_timestamp=int.from_bytes(fields[11],"big") if fields[11] else 0
    tx_root=bytes(fields[4]); receipt_root=bytes(fields[5])
    if header_number!=bn: raise ValueError(f"Polygon header number mismatch expected={bn} actual={header_number}")
    if header_timestamp!=int(origin["timestamp_unix"]): raise ValueError(f"Polygon header timestamp mismatch block={bn} expected={origin['timestamp_unix']} actual={header_timestamp}")
    if tx_root!=h2b(w["transactions_root"]): raise ValueError(f"Polygon transaction root mismatch block={bn}")
    if receipt_root!=h2b(w["receipts_root"]): raise ValueError(f"Polygon receipt root mismatch block={bn}")
    preimage=word(header_number)+word(header_timestamp)+tx_root+receipt_root
    leaf=keccak(preimage)
    meta={
        "witness_file":str(witness_file.relative_to(SOURCE)),
        "block_header_sha256":hashlib.sha256(header_rlp).hexdigest(),
        "header_number":header_number,
        "header_timestamp":header_timestamp,
        "transactions_root":"0x"+tx_root.hex(),
        "receipts_root":"0x"+receipt_root.hex(),
        "checkpoint_leaf":"0x"+leaf.hex(),
        "checkpoint_leaf_preimage_sha256":hashlib.sha256(preimage).hexdigest(),
    }
    debug("polygon_checkpoint_leaf", polygon_block=bn, block_hash=expected_hash, **meta)
    return leaf,meta


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if DEBUG.exists(): DEBUG.unlink()
    idx_path=SOURCE/"evidence-v2"/"SIDECHAIN-NFT-IDENTITY-INDEX.json"
    idx=json.loads(idx_path.read_text())
    targets={}; records_by_asset={}
    for rec in idx.get("records",[]):
        chain_id=int(rec.get("chain",{}).get("chain_id",0))
        if chain_id!=137: continue
        records_by_asset[rec["asset_id"]]=rec
        origin=rec.get("origin") or {}; bn=int(origin["block_number"]); bh=str(origin["block_hash"]).lower()
        key=(bn,bh); targets.setdefault(key,[]).append(rec["asset_id"])
    if not targets: raise SystemExit("no Polygon records found")
    debug("start", source=str(SOURCE), polygon_records=sum(len(x) for x in targets.values()), unique_polygon_blocks=len(targets), rootchain=ROOTCHAIN)
    current=current_header_id(); checkpoint_cache={}; block_results=[]
    for (bn,bh),assets in sorted(targets.items()):
        info,search=find_header(bn,current)
        checkpoint_cache[info["header_block_id"]]=info
        proof=polygon_block_proof(bn,info["start"],info["end"])
        source_rec=records_by_asset[sorted(assets)[0]]
        leaf,leaf_meta=polygon_checkpoint_leaf(source_rec)
        computed=verify_merkle(leaf,bn-info["start"],proof)
        if "0x"+computed.hex()!=info["root"].lower():
            debug("polygon_membership_mismatch", polygon_block=bn, block_hash=bh, checkpoint_leaf="0x"+leaf.hex(), computed_root="0x"+computed.hex(), expected_root=info["root"], proof_index=bn-info["start"], proof_nodes=len(proof))
            raise ValueError(f"Polygon checkpoint leaf membership mismatch block={bn} computed=0x{computed.hex()} expected={info['root']}")
        block_results.append({"polygon_block_number":bn,"polygon_block_hash":bh,"asset_ids":sorted(assets),"header_block_id":info["header_block_id"],"checkpoint_start":info["start"],"checkpoint_end":info["end"],"checkpoint_root":info["root"],"checkpoint_created_at":info["created_at"],"checkpoint_proposer":info["proposer"],"proof_siblings":["0x"+x.hex() for x in proof],"proof_index":bn-info["start"],"computed_root":"0x"+computed.hex(),"checkpoint_leaf":leaf_meta,"binary_search":search,"pass":True})
        debug("polygon_membership_pass", polygon_block=bn, block_hash=bh, checkpoint_leaf="0x"+leaf.hex(), header_block_id=info["header_block_id"], proof_nodes=len(proof), checkpoint_root=info["root"])
    checkpoint_results=[]
    for hid,info in sorted(checkpoint_cache.items()):
        log,eth_block=find_checkpoint_log(info); rp=checkpoint_receipt_proof(log,eth_block)
        checkpoint_results.append({**info,**rp,"event_topic0":NEW_HEADER_TOPIC,"event_data":log["data"],"event_topics":log["topics"],"pass":True})
        debug("checkpoint_ethereum_pass", header_block_id=hid, ethereum_block=rp["ethereum_block_number"], ethereum_block_hash=rp["ethereum_block_hash"])
    finalized=rpc("ethereum","eth_getBlockByNumber",["finalized",False])
    finalized_summary=None
    if finalized:
        final_header=rlp.encode(header_fields(finalized)); final_hash="0x"+keccak(final_header).hex()
        if final_hash.lower()!=finalized["hash"].lower(): raise ValueError("Ethereum finalized boundary header hash mismatch")
        finalized_summary={"block_number":h2i(finalized["number"]),"block_hash":finalized["hash"],"timestamp":h2i(finalized["timestamp"]),"block_header_rlp":"0x"+final_header.hex(),"header_sha256":hashlib.sha256(final_header).hexdigest()}
        unfinal=[x for x in checkpoint_results if x["ethereum_block_number"]>finalized_summary["block_number"]]
        if unfinal: raise ValueError(f"{len(unfinal)} checkpoint Ethereum blocks newer than RPC finalized boundary")
        debug("ethereum_finalized_boundary", **{k:v for k,v in finalized_summary.items() if k!="block_header_rlp"})
    report={
        "schema":"trinity-accord/chronicle-polygon-ethereum-settlement/v1",
        "generated_at":datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"),
        "source_identity_index_sha256":hashlib.sha256(idx_path.read_bytes()).hexdigest(),
        "rootchain_proxy":ROOTCHAIN,
        "rootchain_event":"NewHeaderBlock(address,uint256,uint256,uint256,uint256,bytes32)",
        "polygon_records":sum(len(x) for x in targets.values()),"unique_polygon_blocks":len(block_results),"unique_checkpoints":len(checkpoint_results),
        "polygon_block_membership_pass":all(x["pass"] for x in block_results),"ethereum_checkpoint_receipt_inclusion_pass":all(x["pass"] for x in checkpoint_results),
        "ethereum_rpc_finalized_boundary":finalized_summary,
        "proof_model":"The Bor checkpoint leaf keccak(bytes32(blockNumber)||bytes32(timestamp)||transactionsRoot||receiptsRoot)) is locally recomputed from an already block-hash-verified L2 witness and Merkle-verified to the RootChain checkpoint root; the exact NewHeaderBlock event receipt is locally MPT-verified to an Ethereum receiptsRoot and the Ethereum block header is locally re-hashed. The finalized tag is an RPC boundary, not an independent Beacon consensus proof.",
        "blocks":block_results,"checkpoints":checkpoint_results,
        "pass":bool(block_results) and bool(checkpoint_results) and finalized_summary is not None,
        "boundary":"Non-amending supplementary evidence. This proves Polygon checkpoint inclusion in Ethereum execution history; independent Beacon ancestry/finality can be added as a separate layer."
    }
    (OUT/"POLYGON-ETHEREUM-SETTLEMENT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    summary={k:report[k] for k in ["schema","polygon_records","unique_polygon_blocks","unique_checkpoints","polygon_block_membership_pass","ethereum_checkpoint_receipt_inclusion_pass","pass","boundary"]}
    (OUT/"SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    manifest=[]
    for f in sorted(OUT.iterdir()):
        if f.is_file() and f.name not in {"MANIFEST.sha256","MANIFEST.sha256.json"}:
            b=f.read_bytes(); manifest.append({"path":f.name,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
    (OUT/"MANIFEST.sha256.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    (OUT/"MANIFEST.sha256").write_text("".join(f"{x['sha256']}  {x['path']}\n" for x in manifest))
    debug("complete", pass_=report["pass"], polygon_records=report["polygon_records"], unique_polygon_blocks=len(block_results), unique_checkpoints=len(checkpoint_results))
    if not report["pass"]: raise SystemExit(1)


if __name__=="__main__": main()
