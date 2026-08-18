#!/usr/bin/env python3
import concurrent.futures, json, os, pathlib, threading, time, urllib.error, urllib.request
import rlp
from eth_hash.auto import keccak
from trie import HexaryTrie

OUT = pathlib.Path(os.getenv('CHRONICLE_OUT', 'artifacts/chronicle-sidechain-scan'))
EVID = OUT / 'evidence-v2'

def endpoint_list(primary, fallbacks):
    values=[]
    for raw in (primary, fallbacks):
        for value in str(raw or '').replace('\n', ',').split(','):
            value=value.strip().rstrip('/')
            if value and value not in values: values.append(value)
    if not values: raise ValueError('at least one RPC endpoint is required')
    return values

RPC = {
    'polygon': endpoint_list(
        os.getenv('POLYGON_RPC_URL'),
        os.getenv('CHRONICLE_POLYGON_RPC_FALLBACK_URLS') or 'https://polygon.drpc.org,https://polygon-bor-rpc.publicnode.com',
    ),
    'base': endpoint_list(
        os.getenv('BASE_RPC_URL'),
        os.getenv('CHRONICLE_BASE_RPC_FALLBACK_URLS') or 'https://base.drpc.org,https://base-rpc.publicnode.com,https://mainnet.base.org',
    ),
}
CONCURRENCY = max(1, min(8, int(os.getenv('CHRONICLE_L2_CONCURRENCY', '4'))))
TIMEOUT = int(os.getenv('CHRONICLE_L2_HTTP_TIMEOUT_SECONDS', '45'))
RETRIES = int(os.getenv('CHRONICLE_L2_HTTP_RETRIES', '2'))
RPC_MIN_INTERVAL = max(0, int(os.getenv('CHRONICLE_L2_RPC_MIN_INTERVAL_MS', '100'))) / 1000
RPC_LOCKS = {chain: threading.Lock() for chain in RPC}
RPC_STATE_LOCK = threading.Lock()
RPC_PREFERRED = {chain: 0 for chain in RPC}
RPC_LAST_CALL = {chain: 0.0 for chain in RPC}
RPC_SUCCESSES = {chain: [0] * len(endpoints) for chain, endpoints in RPC.items()}
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
    if isinstance(v, bool): return 1 if v else 0
    return int(v, 16) if isinstance(v, str) and v.startswith('0x') else int(v)

def intb(v):
    n = h2i(v)
    return b'' if n == 0 else n.to_bytes((n.bit_length()+7)//8, 'big')

class RpcFailure(RuntimeError):
    def __init__(self, message, retry_after=0):
        super().__init__(message)
        self.retry_after = retry_after

def rpc_once(chain, endpoint_index, method, params):
    payload = json.dumps({'jsonrpc':'2.0','id':1,'method':method,'params':params}).encode()
    elapsed = time.monotonic() - RPC_LAST_CALL[chain]
    if elapsed < RPC_MIN_INTERVAL: time.sleep(RPC_MIN_INTERVAL - elapsed)
    RPC_LAST_CALL[chain] = time.monotonic()
    req = urllib.request.Request(RPC[chain][endpoint_index], data=payload, headers={'content-type':'application/json','user-agent':'trinity-accord-sidechain-l2/2.2'})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            data = json.loads(res.read())
    except urllib.error.HTTPError as e:
        retry_after=0
        try:
            retry_after=float(e.headers.get('retry-after') or 0)
        except (TypeError, ValueError):
            pass
        raise RpcFailure(f'HTTP Error {e.code}: {e.reason}', retry_after) from e
    except Exception as e:
        raise RpcFailure(str(e)) from e
    if not isinstance(data, dict): raise RpcFailure('non-object JSON-RPC response')
    if data.get('error'): raise RpcFailure(f"{method}: {data['error']}")
    return data.get('result')

def rpc(chain, method, params, retries=None):
    rounds = (RETRIES if retries is None else max(0, retries)) + 1
    last = None
    with RPC_LOCKS[chain]:
        for attempt in range(rounds):
            with RPC_STATE_LOCK: preferred=RPC_PREFERRED[chain]
            order=list(range(preferred, len(RPC[chain])))+list(range(0, preferred))
            errors=[]; retry_after=0
            for endpoint_index in order:
                try:
                    result=rpc_once(chain, endpoint_index, method, params)
                    with RPC_STATE_LOCK:
                        previous=RPC_PREFERRED[chain]
                        RPC_PREFERRED[chain]=endpoint_index
                        RPC_SUCCESSES[chain][endpoint_index]+=1
                    if endpoint_index != previous:
                        print(f'[L2 RPC ROUTE] {chain} endpoint={endpoint_index+1}/{len(RPC[chain])} method={method}', flush=True)
                    return result
                except RpcFailure as e:
                    last=e; retry_after=max(retry_after, e.retry_after)
                    errors.append(f'endpoint={endpoint_index+1}/{len(RPC[chain])} {e}')
            print(f'[L2 RETRY] {chain} {method} attempt={attempt+1}/{rounds} error={"; ".join(errors)}', flush=True)
            if attempt < rounds - 1:
                time.sleep(max(retry_after, min(.5 * (2 ** attempt), 30)))
    raise RuntimeError(str(last))

def access_list(v):
    out=[]
    for item in v or []:
        if isinstance(item, dict): out.append([h2b(item['address']), [h2b(x) for x in item.get('storageKeys',[])]])
        else: out.append([h2b(item[0]), [h2b(x) for x in item[1]]])
    return out

def authorization_list(v):
    out=[]
    for item in v or []:
        if isinstance(item, dict):
            out.append([
                intb(item.get('chainId', item.get('chain_id'))), h2b(item['address']), intb(item['nonce']),
                intb(item.get('yParity', item.get('y_parity'))), intb(item['r']), intb(item['s']),
            ])
        else:
            out.append([intb(item[0]), h2b(item[1]), intb(item[2]), intb(item[3]), intb(item[4]), intb(item[5])])
    return out

def encode_tx(tx):
    typ=h2i(tx.get('type','0x0'))
    common_input=h2b(tx.get('input') or tx.get('data') or '0x')
    # OP Stack post-exec transactions (0x7d) expose `input` as the already-RLP-encoded
    # post-exec payload. Their canonical EIP-2718 form is simply 0x7d || payload.
    if typ == 0x7d:
        return bytes([typ]) + common_input
    to=h2b(tx.get('to'), allow_none=True)
    # OP Stack deposited transaction, per the OP Stack consensus spec:
    # sourceHash, from, to, mint, value, gas, isSystemTx, data.
    if typ == 0x7e:
        fields=[
            h2b(tx['sourceHash']), h2b(tx['from']), to,
            intb(tx.get('mint') or 0), intb(tx.get('value') or 0), intb(tx['gas']),
            intb(tx.get('isSystemTx') or 0), common_input,
        ]
        return bytes([typ]) + rlp.encode(fields)
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
    elif typ == 4:
        auths=authorization_list(tx.get('authorizationList', tx.get('authorization_list')))
        if not auths: raise ValueError('type 4 transaction missing authorizationList')
        fields=[intb(tx['chainId']),intb(tx['nonce']),intb(tx['maxPriorityFeePerGas']),intb(tx['maxFeePerGas']),intb(tx['gas']),to,intb(tx['value']),common_input,access_list(tx.get('accessList')),auths,intb(y),intb(tx['r']),intb(tx['s'])]
    else:
        raise ValueError(f'unsupported tx type {typ}')
    return bytes([typ])+rlp.encode(fields)

def encode_log(log):
    return [h2b(log['address']), [h2b(t) for t in log.get('topics',[])], h2b(log.get('data','0x'))]

def encode_receipt(rec):
    status = rec.get('status')
    root = rec.get('root')
    first = intb(status) if status is not None else h2b(root)
    fields=[first, intb(rec['cumulativeGasUsed']), h2b(rec['logsBloom']), [encode_log(x) for x in rec.get('logs',[])]]
    typ=h2i(rec.get('type','0x0'))
    # Post-Canyon OP Stack deposit receipts commit two optional consensus fields.
    # RPC JSON names the second field `depositReceiptVersion`.
    if typ == 0x7e:
        if rec.get('depositNonce') is not None:
            fields.append(intb(rec['depositNonce']))
        if rec.get('depositReceiptVersion') is not None:
            fields.append(intb(rec['depositReceiptVersion']))
    payload=rlp.encode(fields)
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
        recs=rpc(chain,'eth_getBlockReceipts',[block['hash']],retries=0)
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
        et=encode_tx(tx); er=encode_receipt(rec)
        encoded_hash='0x'+keccak(et).hex()
        if encoded_hash.lower()!=tx['hash'].lower():
            raise ValueError(f"tx encoding mismatch index={i} type={tx.get('type')} computed={encoded_hash} rpc={tx['hash']}")
        key=rlp.encode(i); tx_trie[key]=et; rec_trie[key]=er; tx_encoded.append(et); rec_encoded.append(er)
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
    summary={'schema':'trinity-accord/chronicle-sidechain-l2-capture-summary/v2','generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'records_expected':len(records),'records_pass':len(results),'unique_blocks':len(groups),'blocks_failed':len(errors),'rpc_routes':{chain:{'endpoint_count':len(RPC[chain]),'successful_requests_by_endpoint':RPC_SUCCESSES[chain]} for chain in sorted(RPC)},'errors':errors,'pass':len(results)==len(records) and not errors}
    jwrite(EVID/'L2-CAPTURE-SUMMARY.json',summary)
    print(f"[L2 COMPLETE] records_pass={len(results)}/{len(records)} blocks_failed={len(errors)}", flush=True)
    if not summary['pass']: raise SystemExit(1)
if __name__=='__main__': main()
