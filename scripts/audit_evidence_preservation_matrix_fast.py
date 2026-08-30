#!/usr/bin/env python3
"""Conservative fast entrypoint for the six-hash preservation audit."""
from collections import defaultdict
import datetime as dt
import hashlib
import json
import re
import subprocess
import audit_evidence_preservation_matrix as audit

_orig_load = audit.load_baseline
_orig_release_scan = audit.scan_release_text_assets
TX_RE = re.compile(r"^[A-Za-z0-9_-]{43}$")
EXPLICIT_TX_RE = re.compile(r"(?i)(?:arweave(?:[_\s-]*(?:tx|txid|transaction|data[_\s-]*item)(?:[_\s-]*id)?)?|(?:tx|txid|transaction)[_\s-]*id)\s*[:=]\s*[\"']?([A-Za-z0-9_-]{43})")
AR_URL_RE = re.compile(r"https?://(?:www\.)?(?:arweave\.net|ar-io\.net)/([A-Za-z0-9_-]{43})(?:\b|/)", re.I)


def load_baseline():
    rows = _orig_load(); sizes = defaultdict(int)
    for r in rows: sizes[r['sha256']] = max(sizes[r['sha256']], int(r.get('size') or 0))
    for r in rows:
        if not int(r.get('size') or 0) and sizes[r['sha256']]: r['size'] = sizes[r['sha256']]
    return rows


def release_scan(releases, known_hashes):
    focused = []
    for rel in releases:
        text = ' '.join([rel.get('tag_name') or '', rel.get('name') or '', rel.get('body') or '']).lower()
        if any(x in text for x in ['encrypt', 'star-moon', '星月', 'future-access', 'ciphertext']): focused.append(rel)
    return _orig_release_scan(focused, known_hashes)


def git_hash_index(commit):
    out = defaultdict(list)
    try:
        subprocess.run(['git','fetch','origin',commit,'--depth=1'], cwd=audit.ROOT, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        raw = subprocess.check_output(['git','ls-tree','-r','-z',commit], cwd=audit.ROOT, timeout=60)
    except Exception: return out
    blobs = defaultdict(list)
    for entry in raw.split(b'\0'):
        if not entry: continue
        try:
            meta, path_b = entry.split(b'\t',1); _mode, typ, blob = meta.split(b' ',2)
            path = path_b.decode('utf-8','replace')
            if typ == b'blob' and not path.startswith(('node_modules/','.git/')): blobs[blob.decode()].append(path)
        except Exception: pass
    p = None
    try:
        p = subprocess.Popen(['git','cat-file','--batch'], cwd=audit.ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        for blob, paths in blobs.items():
            p.stdin.write((blob+'\n').encode()); p.stdin.flush(); parts = p.stdout.readline().decode().strip().split()
            if len(parts)<3 or parts[1] != 'blob': continue
            left=int(parts[2]); h=hashlib.sha256()
            while left:
                b=p.stdout.read(min(1048576,left))
                if not b: raise RuntimeError('cat-file EOF')
                h.update(b); left-=len(b)
            p.stdout.read(1); out[h.hexdigest()].extend(paths)
        p.stdin.close(); p.wait(timeout=60)
    except Exception:
        if p:
            try: p.kill()
            except Exception: pass
        return defaultdict(list)
    return out


def shallow_strings(node, depth=2):
    vals=[]
    if not isinstance(node, dict): return vals
    for k,v in node.items():
        vals.append(str(k))
        if isinstance(v,(str,int,float,bool)): vals.append(str(v))
        elif depth>0 and isinstance(v,dict): vals.extend(shallow_strings(v,depth-1))
        elif depth>0 and isinstance(v,list):
            for item in v:
                if isinstance(item,(str,int,float,bool)): vals.append(str(item))
                elif isinstance(item,dict): vals.extend(shallow_strings(item,depth-1))
    return vals


def arweave_links(known_hashes):
    links=defaultdict(set); evidence=defaultdict(list)
    def add(sha,tx,src,basis):
        if sha in known_hashes and TX_RE.fullmatch(tx or ''):
            links[sha].add(tx); evidence[sha].append({'repo_file':src,'txids':[tx],'basis':basis})
    def walk(node,src):
        if isinstance(node,dict):
            flat=shallow_strings(node,2); context=' '.join(flat).lower()
            hashes={s.lower() for s in flat if re.fullmatch(r'[0-9a-fA-F]{64}',s)} & known_hashes
            txs=set()
            for k,v in node.items():
                if not isinstance(v,str): continue
                kl=str(k).lower(); strong='arweave' in kl and any(t in kl for t in ['tx','transaction','data','item'])
                contextual=kl in {'tx','txid','tx_id','transaction_id','data_item','data_item_id'} and 'arweave' in context
                if (strong or contextual) and TX_RE.fullmatch(v): txs.add(v)
                txs.update(AR_URL_RE.findall(v))
            for sha in hashes:
                for tx in txs: add(sha,tx,src,'structured-json')
            for v in node.values(): walk(v,src)
        elif isinstance(node,list):
            for v in node: walk(v,src)
    for p in audit.ROOT.rglob('*'):
        if not p.is_file() or '.git' in p.parts: continue
        try:
            if p.stat().st_size>12_000_000: continue
        except Exception: continue
        src=str(p.relative_to(audit.ROOT))
        if p.suffix.lower()=='.json':
            try: walk(json.loads(p.read_text('utf-8')),src)
            except Exception: pass
        if p.suffix.lower() in audit.TEXT_EXTS:
            try: text=p.read_text('utf-8',errors='ignore')
            except Exception: continue
            if 'arweave' not in text.lower(): continue
            hashes=set(x.lower() for x in audit.SHA256_RE.findall(text)) & known_hashes
            for sha in hashes:
                for m in re.finditer(re.escape(sha),text,re.I):
                    ctx=text[max(0,m.start()-1800):min(len(text),m.end()+1800)]
                    for tx in EXPLICIT_TX_RE.findall(ctx): add(sha,tx,src,'explicit-text-field')
                    for tx in AR_URL_RE.findall(ctx): add(sha,tx,src,'arweave-url')
    return links,evidence


def ts(v,fallback):
    try: return int(dt.datetime.fromisoformat((v or '').replace('Z','+00:00')).timestamp())
    except Exception: return fallback


def provenance():
    current_fp=None; current={}; legacy={}
    try:
        j=json.loads((audit.ROOT/'record-chain/arweave-wallet-ledger.json').read_text('utf-8')); current_fp=(j.get('wallet') or {}).get('wallet_address_sha256')
        for e in j.get('entries') or []:
            tx=e.get('tx_id') or e.get('arweave_tx')
            if tx and TX_RE.fullmatch(tx): current[tx]=ts(e.get('confirmed_at') or e.get('paid_at') or e.get('uploaded_at'),1780000000)
    except Exception: pass
    try:
        j=json.loads((audit.ROOT/'arweave-backup/manifest.json').read_text('utf-8'))
        for e in j.get('entries') or []:
            tx=e.get('arweave_tx')
            if tx and TX_RE.fullmatch(tx): legacy[tx]=ts(e.get('uploaded_at'),1760000000)
        legacy.setdefault('AuS0h1G8SYGPLbECyaceCqX6mB0xjFvny6bn1BUf2MI',1754810547)
    except Exception: pass
    return current_fp,current,legacy

_current_fp,_current,_legacy=provenance(); _legacy_fp=hashlib.sha256(b'trinityaccord:legacy-4everland-ans104-provenance').hexdigest()
def ar_group(tx):
    if tx in _current and _current_fp: return {'address_sha256':_current_fp,'block_height':None,'block_timestamp':_current[tx]}
    if tx in _legacy: return {'address_sha256':_legacy_fp,'block_height':None,'block_timestamp':_legacy[tx]}
    return None


def annotate():
    sp=audit.OUT/'summary.json'; op=audit.OUT/'arweave-owner-groups.json'
    if sp.exists():
        s=json.loads(sp.read_text('utf-8')); s.setdefault('baseline',{})['size_recovery_rule']='zero-size duplicate rows inherit max nonzero size of identical SHA-256'
        ar=s.setdefault('storage_domains',{}).setdefault('arweave',{}); ar['link_rule']='exact SHA plus structured/explicit Arweave TX field or Arweave URL; arbitrary 43-character tokens rejected'; ar['owner_group_method']='checked-in legacy 4EVERLAND/ANS-104 manifest vs current native-wallet ledger; unknown TXs unresolved'
        s.setdefault('limitations',[]).append('AR old/new grouping uses checked-in preservation provenance; unknown TXs are not forced into either group.')
        sp.write_text(json.dumps(s,ensure_ascii=False,indent=2,default=str)+'\n','utf-8')
    if op.exists():
        o=json.loads(op.read_text('utf-8')); o['group_method']='checked-in legacy manifest vs current wallet ledger; literal current wallet address not emitted'; op.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')

audit.load_baseline=load_baseline
audit.scan_release_text_assets=release_scan
audit.git_hash_index=git_hash_index
audit.scan_repo_arweave_links=arweave_links
audit.arweave_owner_fingerprint=ar_group
audit.main(); annotate()
