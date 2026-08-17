#!/usr/bin/env python3
import concurrent.futures, json, os, pathlib, time, urllib.request
import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

OUT = pathlib.Path(os.getenv('CHRONICLE_OUT', 'artifacts/chronicle-sidechain-scan'))
EVID = OUT / 'evidence-v2'
RPC = {
    'polygon': os.getenv('POLYGON_RPC_URL') or 'https://polygon.drpc.org',
    'base': os.getenv('BASE_RPC_URL') or 'https://mainnet.base.org',
}
CONCURRENCY = max(1, min(8, int(os.getenv('CHRONICLE_L2_CONCURRENCY', '4'))))
TIMEOUT = int(os.getenv('CHRONICLE_L2_HTTP_TIMEOUT_SECONDS', '45'))
RETRIES = int(os.getenv('CHRONICLE_L2_HTTP_RETRIES', '2'))
TRANSFER = '0x' + keccak(b'Transfer(address,address,uint256)').hex()
SINGLE = '0x' + keccak(b'TransferSingle(address,address,address,uint256,uint256)').hex()
BATCH = '0x' + keccak(b'TransferBatch(address,address,address,uint256[],uint256[])').hex()

def jwrite(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')

def h2b(v, allow_none=False):
    if v is None and allow_none: return b''
    if v is None: raise ValueError('missing hex field')
    s = str(v); s = s[2:] if s.startswith('0x') else s
    if len(s) % 2: s = '0' + s
    return bytes.fromhex(s)

def h2i(v):
    if v is None: return 0
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v)

def intb(v):
    n = h2i(v)
    return b'' if n == 0 else n.to_bytes((n.bit_length()+7)//8, 'big')

def rpc(chain, method, params):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(RPC[chain], data=payload, headers={'content-type':'application/json','user-agent':'trinity-accord-sidechain-l2/2.0'})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
                data = json.loads(res.read())
            if data.get('error'): raise RuntimeError(f"{method}: {data['error']}")
            return data.get('result')
        except Exception as e:
            last = e
            print(f'[L2 RETRY] {chain} {method} attempt={attempt+1}/{RETRIES+1} error={e}', flush=True)
            if attempt < RETRIES: time.sleep(.5 * (2 ** attempt))
    raise RuntimeError(str(last))

def access_list(v):
    out=[]
    for item in v or []:
        if isinstance(item, dict): out.append([h2b(item['address']), [h2b(x) for x in item.get('storageKeys',[])]])
        else: out.append([h2b(item[0]), [h2b(x) for x in item[1]]])
    return out

def encode_tx(tx):
    typ=h2i(tx.get('type','0x0'))
    to=h2b(tx.get('to'), allow_none=True)
    common_input=h2b(tx.get('input') or tx.get('data') or '0x')
    if typ == 0:
        fields=[intb(tx['nonce']), intb(tx['gasPrice']), intb(tx['gas']), to, intb(tx['value']), common_input, intb(tx['v']), intb(tx['r']), intb(tx['s'])]
        return rlp.encode(fields)
    y=tx.get('yParity', tx.get('v'))
    if typ == 1:
        fields=[intb(tx['chainId']),intb(tx['nonce']),intb(tx['gasPrice']),intb(tx['gas']),to,intb(tx['value']),common_input,access_list(tx.get('accessList')),intb(y),intb(tx['r']),intb(tx['s'])]
    elif typ == 2:
        fields=[intb(tx['chainId']),intb(tx['nonce']),intb(tx['maxPriorityFeePerGas']),intb(tx['maxFeePerGas']),intb(tx['gas']),to,intb(tx['value']),common_input,access_list(tx.get('accessList')),intb(y),intb(tx['r']),intb(tx['s'])]
    elif typ == 3:
        fields=[intb(tx['chainId']),intb(tx['nonce']),intb(tx['maxPriorityFeePerGas']),intb(tx['maxFeePerGas']),intb(tx['gas']),to,intb(tx['value']),common_input,access_list(tx.get('accessList')),intb(tx['maxFeePerBlobGas']),[h2b(x) for x in tx.get('blobVersionedHashes',[])],intb(y),intb(tx['r']),intb(tx['s'])]
    else:
        raise ValueError(f'unsupported tx type {typ}')
    return bytes([typ])+rlp.encode(fields)

def encode_log(log):
    return [h2b(log['address']), [h2b(t) for t in log.get('topics',[])], h2b(log.get('data','0x'))]

def encode_receipt(rec):
    status = rec.get('status')
    root = rec.get('root')
    first = intb(status) if status is not None else h2b(root)
    payload=rlp.encode([first, intb(rec['cumulativeGasUsed']), h2b(rec['logsBloom']), [encode_log(x) for x in rec.get('logs',[])]])
    typ=h2i(rec.get('type','0x0'))
    return (bytes([typ])+payload) if typ else payload

def header_fields(block):
    fields=[h2b(block['parentHash']),h2b(block['sha3Uncles']),h2b(block['miner']),h2b(block['stateRoot']),h2b(block['transactionsRoot']),h2b(block['receiptsRoot']),h2b(block['logsBloom']),intb(block['difficulty']),intb(block['number']),intb(block['gasLimit']),intb(block['gasUsed']),intb(block['timestamp']),h2b(block['extraData']),h2b(block['mixHash']),h2b(block['nonce'])]
    for name, kind in [('baseFeePerGas','int'),('withdrawalsRoot','hex'),('blobGasUsed','int'),('excessBlobGas','int'),('parentBeaconBlockRoot','hex'),('requestsHash','hex')]:
        if block.get(name) is not None: fields.append(intb(block[name]) if kind=='int' else h2b(block[name]))
    return fields

def log_index(log): return h2i(log.get('logIndex'))
def topic_addr(topic): return '0x'+topic[-40:].lower()
def token_ids_from_log(log):
    topics=[x.lower() for x in log.get('topics',[])]; data=h2b(log.get('data','0x'))
    if not topics: return []
    if topics[0]==TRANSFER.lower() and len(topics)>=4: return [h2i(topics[3])]
    if topics[0]==SINGLE.lower() and len(data)>=64: return [int.from_bytes(data[:32],'big')]
    if topics[0]==BATCH.lower() and len(data)>=64:
        off=int.from_bytes(data[:32],'big')
        if off+32>len(data): return []
        n=int.from_bytes(data[off:off+32],'big'); start=off+32
        if start+32*n>len(data): return []
        return [int.from_bytes(data[start+32*i:start+32*(i+1)],'big') for i in range(n)]
    return []

def match_origin_log(record, receipt):
    origin=record['origin']; expected_idx=origin.get('log_index'); token=int(record['token_id']); contract=record['contract'].lower()
    candidates=[]
    for log in receipt.get('logs',[]):
        if str(log.get('address','')).lower()!=contract: continue
        if expected_idx is not None and log_index(log)!=int(expected_idx): continue
        ids=token_ids_from_log(log)
        if token in ids: candidates.append(log)
    if not candidates and expected_idx is not None:
        for log in receipt.get('logs',[]):
            if str(log.get('address','')).lower()==contract and log_index(log)==int(expected_idx): candidates.append(log)
    if len(candidates)!=1: raise ValueError(f'origin log match count={len(candidates)} expected_log_index={expected_idx}')
    log=candidates[0]; topics=[x.lower() for x in log.get('topics',[])]
    observed_from=observed_to=None
    if topics and topics[0]==TRANSFER.lower() and len(topics)>=3: observed_from,observed_to=topic_addr(topics[1]),topic_addr(topics[2])
    elif topics and topics[0] in (SINGLE.lower(),BATCH.lower()) and len(topics)>=4: observed_from,observed_to=topic_addr(topics[2]),topic_addr(topics[3])
    return {'log_index':log_index(log),'address':log['address'].lower(),'topic0':topics[0] if topics else None,'token_ids':[str(x) for x in token_ids_from_log(log)],'from':observed_from,'to':observed_to}

def get_receipts(chain, block):
    try:
        recs=rpc(chain,'eth_getBlockReceipts',[block['hash']])
        if isinstance(recs,list) and len(recs)==len(block['transactions']): return recs, 'eth_getBlockReceipts'
    except Exception as e:
        print(f"[L2 INFO] {chain} block={h2i(block['number'])} batch receipts unavailable: {e}", flush=True)
    recs=[]
    for tx in block['transactions']:
        recs.append(rpc(chain,'eth_getTransactionReceipt',[tx['hash']]))
    return recs, 'per_transaction_receipts'

def capture_group(item):
    (chain, block_hash), records=item
    block=rpc(chain,'eth_getBlockByHash',[block_hash,True])
    if not block: raise ValueError('block not found')
    encoded_header=rlp.encode(header_fields(block)); computed='0x'+keccak(encoded_header).hex()
    if computed.lower()!=block['hash'].lower(): raise ValueError(f"block header hash mismatch computed={computed} rpc={block['hash']}")
    receipts, receipt_source=get_receipts(chain,block)
    tx_trie=HexaryTrie(db={}); rec_trie=HexaryTrie(db={})
    tx_encoded=[]; rec_encoded=[]
    for i,(tx,rec) in enumerate(zip(block['transactions'],receipts)):
        et=encode_tx(tx); er=encode_receipt(rec); key=rlp.encode(i); tx_trie[key]=et; rec_trie[key]=er; tx_encoded.append(et); rec_encoded.append(er)
    if ('0x'+tx_trie.root_hash.hex()).lower()!=block['transactionsRoot'].lower(): raise ValueError('transactionsRoot mismatch')
    if ('0x'+rec_trie.root_hash.hex()).lower()!=block['receiptsRoot'].lower(): raise ValueError('receiptsRoot mismatch')
    outputs=[]
    tx_by_hash={tx['hash'].lower():(i,tx) for i,tx in enumerate(block['transactions'])}
    rec_by_hash={r['transactionHash'].lower():r for r in receipts}
    for record in records:
        txh=record['origin']['transaction_hash'].lower(); pair=tx_by_hash.get(txh)
        if not pair: raise ValueError(f'origin tx absent {txh}')
        idx,tx=pair; rec=rec_by_hash.get(txh)
        if not rec: raise ValueError(f'receipt absent {txh}')
        key=rlp.encode(idx); tx_proof=[rlp.encode(n).hex() for n in tx_trie.get_proof(key)]; rec_proof=[rlp.encode(n).hex() for n in rec_trie.get_proof(key)]
        if HexaryTrie.get_from_proof(tx_trie.root_hash,key,[rlp.decode(bytes.fromhex(x)) for x in tx_proof])!=tx_encoded[idx]: raise ValueError('tx proof self-check failed')
        if HexaryTrie.get_from_proof(rec_trie.root_hash,key,[rlp.decode(bytes.fromhex(x)) for x in rec_proof])!=rec_encoded[idx]: raise ValueError('receipt proof self-check failed')
        ts=h2i(block['timestamp']); declared=int(record['origin'].get('timestamp_unix') or 0)
        if declared and ts!=declared: raise ValueError(f'timestamp mismatch declared={declared} header={ts}')
        matched=match_origin_log(record,rec)
        outputs.append((record, {
            'schema':'trinity-accord/chronicle-sidechain-l2-execution-witness/v2','chain':chain,'chain_id':record['chain']['chain_id'],'asset_id':record['asset_id'],
            'origin_transaction_hash':record['origin']['transaction_hash'],'transaction_index':idx,'block_hash':block['hash'],'block_number':h2i(block['number']),
            'block_timestamp_unix':ts,'block_timestamp':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(ts)),'timestamp_matches_origin': (not declared) or ts==declared,
            'block_header_rlp':'0x'+encoded_header.hex(),'block_header_hash_computed':computed,
            'transactions_root':block['transactionsRoot'],'receipts_root':block['receiptsRoot'],'transaction_rlp':'0x'+tx_encoded[idx].hex(),'receipt_rlp':'0x'+rec_encoded[idx].hex(),
            'mpt_key_rlp':'0x'+key.hex(),'transaction_proof_nodes_rlp':['0x'+x for x in tx_proof],'receipt_proof_nodes_rlp':['0x'+x for x in rec_proof],
            'origin_log':matched,'receipt_status':h2i(rec.get('status','0x1')),'receipt_source':receipt_source,'pass':True
        }))
    return outputs

def main():
    index=json.loads((EVID/'SIDECHAIN-NFT-IDENTITY-INDEX.json').read_text())
    records=index['records']; missing=[r['asset_id'] for r in records if not r.get('origin') or not r['origin'].get('transaction_hash') or not r['origin'].get('block_hash')]
    if missing: raise SystemExit(f'missing origin coordinates for {len(missing)} records')
    groups={}
    for r in records: groups.setdefault((r['chain']['name'],r['origin']['block_hash']),[]).append(r)
    print(f'[L2 START] records={len(records)} unique_blocks={len(groups)} concurrency={CONCURRENCY}', flush=True)
    results=[]; errors=[]; done=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futs={ex.submit(capture_group,item):item[0] for item in groups.items()}
        for fut in concurrent.futures.as_completed(futs):
            chain,bh=futs[fut]
            try:
                rows=fut.result(); results.extend(rows); status=f'ok records={len(rows)}'
            except Exception as e:
                errors.append({'chain':chain,'block_hash':bh,'error':str(e)}); status=f'ERROR {e}'
            done+=1; print(f'[L2 PROGRESS] blocks={done}/{len(groups)} chain={chain} block={bh} {status}', flush=True)
    witness_dir=EVID/'l2'
    for record,w in results:
        p=witness_dir/record['chain']['name']/record['contract']/record['token_id']/'witness.json'; jwrite(p,w)
    summary={'schema':'trinity-accord/chronicle-sidechain-l2-capture-summary/v2','generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'records_expected':len(records),'records_pass':len(results),'unique_blocks':len(groups),'blocks_failed':len(errors),'errors':errors,'pass':len(results)==len(records) and not errors}
    jwrite(EVID/'L2-CAPTURE-SUMMARY.json',summary)
    print(f"[L2 COMPLETE] records_pass={len(results)}/{len(records)} blocks_failed={len(errors)}", flush=True)
    if not summary['pass']: raise SystemExit(1)
if __name__=='__main__': main()
