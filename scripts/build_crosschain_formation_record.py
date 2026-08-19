#!/usr/bin/env python3
"""Build the non-canonical Cross-chain Formation Record from the preserved Polygon/Base evidence package.

Authority rule: the three Bitcoin Originals remain the only canonical and interpretive authority.
This tool refines factual history only. It never rewrites the 175-entry Ethereum Chronicle.
"""
import argparse, collections, datetime as dt, hashlib, json, pathlib, re, sys

ETH_START='2024-03-16T08:02:59Z'
CANON_CLOSURE_DATE='2025-06-29'
ZERO='0x0000000000000000000000000000000000000000'
PROJECT_CONTRACTS={
 ('polygon','0xf406b578bb2e51a83f888635a6d6a7bcf4452938'):'TheChurchOfAGI',
 ('polygon','0x42d67ec4fda9f29415633d22465f2aa141389d06'):'TheChurchOfAGI',
 ('polygon','0x35f988e09288715cd7ebf6e244dc0ff1391931cb'):'Pioneers of AGI',
 ('polygon','0xd53e8acc8cfea9f985df176b37cfc0be6bef472e'):'AGIEpochalSeries',
 ('polygon','0x034594ec872fc5e0e01efbb0b399b690daeff3d0'):'ASI Journey',
 ('polygon','0x844c29b57f2bf0d4a381e6e0968c4a6c6cb3e7cf'):'ASIEpochalSeries',
 ('polygon','0xd6d4a740c8438ba4f1beb64aba66c3a76421d970'):'ASIEpochalSeries',
 ('base','0x49885159c7c10a3aab0e2d23ade5af685efef314'):'ASIEpochalSeries',
 ('base','0x4d389758b9fa006e50013712c4fdf6bf5a9afd9d'):'ASIEpochalSeries',
 ('base','0x323b008f1335000c9004a985db1b0a6a8b07bb6f'):'PROJECT AEON #1',
}
SPAM_RE=re.compile(r'(airdrop|reward|claim\b|refund|bonus|voucher|free mint|eligible to claim)',re.I)
TEST_RE=re.compile(r'(^|[^a-z])test(?:only)?([^a-z]|$)|rarible\s*test',re.I)

def iso(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
def load_json(p):
    try: return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
    except Exception: return {}
def read_varint(b,p=0):
    v=0; shift=0
    while True:
        if p>=len(b): raise ValueError('truncated varint')
        x=b[p]; p+=1; v|=(x&0x7f)<<shift
        if not x&0x80: return v,p
        shift+=7
        if shift>63: raise ValueError('varint too long')
def cid_end(b,p=0):
    if p+2<=len(b) and b[p]==0x12 and b[p+1]==0x20: return p+34
    _,p=read_varint(b,p); _,p=read_varint(b,p); _,p=read_varint(b,p); n,p=read_varint(b,p); return p+n
def parse_car(path):
    b=path.read_bytes(); n,p=read_varint(b,0); p+=n; out=[]
    while p<len(b):
        n,p=read_varint(b,p); sec=b[p:p+n]; p+=n
        if sec:
            e=cid_end(sec); out.append((sec[:e],sec[e:]))
    return out
def proto_fields(b):
    p=0
    while p<len(b):
        key,p=read_varint(b,p); f=key>>3; w=key&7
        if w==0: v,p=read_varint(b,p)
        elif w==2: n,p=read_varint(b,p); v=b[p:p+n]; p+=n
        elif w==1: v=b[p:p+8]; p+=8
        elif w==5: v=b[p:p+4]; p+=4
        else: raise ValueError(f'unsupported protobuf wire={w}')
        yield f,w,v
def parse_link(b):
    out={}
    for f,_,v in proto_fields(b):
        if f==1: out['Hash']=v
        elif f==2: out['Name']=v.decode('utf-8','replace')
        elif f==3: out['Tsize']=v
    return out
def parse_node(b):
    out={'Data':None,'Links':[]}
    for f,_,v in proto_fields(b):
        if f==1: out['Data']=v
        elif f==2: out['Links'].append(parse_link(v))
    return out
def ipfs_parts(uri):
    if not isinstance(uri,str) or not uri.startswith('ipfs://'): return None,None
    x=uri[7:].split('/',1); return x[0], x[1] if len(x)>1 else None
def recover_car_json(root,leaf,token_id,car_dir):
    if not root: return None,None
    cp=car_dir/f'{root}.car'
    if not cp.exists(): return None,None
    try:
        blocks=parse_car(cp); bm={c:d for c,d in blocks}; raw=blocks[0][1]
        try:
            obj=json.loads(raw.decode())
            if isinstance(obj,dict): return obj,f'exact_car:{root}:root'
        except Exception: pass
        node=parse_node(raw); byname={x.get('Name'):x for x in node['Links']}
        candidates=[]
        if leaf: candidates += [leaf,leaf.rsplit('/',1)[-1],pathlib.PurePosixPath(leaf).stem]
        candidates += [str(token_id),f'{token_id}.json',str(token_id).zfill(64)]
        for name in candidates:
            link=byname.get(name)
            if link and link.get('Hash') in bm:
                try:
                    obj=json.loads(bm[link['Hash']].decode())
                    if isinstance(obj,dict): return obj,f'exact_car:{root}:link:{name}'
                except Exception: pass
        return None,f'exact_car:{root}:present_unparsed'
    except Exception as e: return None,f'exact_car:{root}:parse_error:{type(e).__name__}'
def origin(r):
    tx=r.get('transfers') or []; m=[x for x in tx if str(x.get('from','')).lower()==ZERO]; pool=m or tx
    if not pool: return {'kind':'missing'}
    x=sorted(pool,key=lambda z:(z.get('timestamp_unix',10**20),z.get('log_index',10**20)))[0]
    return {'kind':'mint' if m else 'first_observed_transfer','timestamp':x.get('timestamp'),'block_number':x.get('block_number'),'block_hash':x.get('block_hash'),'transaction_hash':x.get('transaction_hash'),'log_index':x.get('log_index')}
def esc(s): return str(s or '').replace('|','\\|').replace('\n',' ')

def build(evidence_root):
    root=pathlib.Path(evidence_root); car_dir=root/'evidence-v2'/'cars'; paths=sorted(root.glob('*/*/*/record.json'))
    print(f'[crosschain] stage=scan evidence_root={root} record_json={len(paths)} car_dir={car_dir}',file=sys.stderr)
    if len(paths)!=217: raise SystemExit(f'expected 217 record.json files, got {len(paths)}')
    rows=[]; debug=[]; eth_start=iso(ETH_START)
    for i,p in enumerate(paths,1):
        r=load_json(p); chain=str(r.get('chain','')).lower(); contract=str(r.get('contract','')).lower(); tid=str(r.get('token_id'))
        bi=load_json(p.parent/'blockscout-instance.json'); data=bi.get('data') or {}; token=data.get('token') or {}; bimd=data.get('metadata') or {}
        md=r.get('metadata') if isinstance(r.get('metadata'),dict) else None; uri=(r.get('token_uri') or {}).get('uri'); cid,leaf=ipfs_parts(uri)
        cmd,car_source=(None,None) if md else recover_car_json(cid,leaf,tid,car_dir); best=md or cmd or (bimd if isinstance(bimd,dict) else None) or {}
        title=best.get('name'); desc=best.get('description'); collection=token.get('name') or PROJECT_CONTRACTS.get((chain,contract)); symbol=token.get('symbol'); text=' '.join(str(x or '') for x in (title,desc,collection,symbol))
        key=(chain,contract)
        if key in PROJECT_CONTRACTS:
            if str(r.get('first_seen',''))[:10] <= CANON_CLOSURE_DATE: cls='project_formation_related'; excluded=False; reason='contract_allowlist_project_series_before_or_on_canon_closure'
            else: cls='project_postcanonical_context'; excluded=False; reason='contract_allowlist_project_series_after_canon_closure'
        elif TEST_RE.search(text): cls='excluded_test'; excluded=True; reason='explicit_test_marker_in_collection_or_metadata'
        elif SPAM_RE.search(text): cls='excluded_spam_airdrop'; excluded=True; reason='airdrop_reward_claim_or_refund_semantics'
        else: cls='unresolved_other'; excluded=None; reason='not_in_project_contract_allowlist_and_no_safe_exclusion_rule'
        pre=bool(key in PROJECT_CONTRACTS and iso(r['first_seen'])<eth_start); rel='pre_ethereum_precursor' if pre else ('postcanonical_nonamending_context' if cls=='project_postcanonical_context' else ('parallel_project_record_unmatched' if cls=='project_formation_related' else 'not_applicable'))
        o=origin(r); src='scanner_metadata' if md else ('exact_car' if cmd else ('blockscout_instance' if bimd else 'unavailable'))
        row={'chain':chain,'contract':contract,'token_id':tid,'first_seen':r.get('first_seen'),'block':o.get('block_number') or r.get('first_seen_block'),'tx_hash':o.get('transaction_hash'),'origin_kind':o.get('kind'),'collection':collection,'title':title,'metadata_root_cid':cid,'metadata_source':src,'car_present':bool(cid and (car_dir/f'{cid}.car').exists()),'classification':cls,'classification_reason':reason,'excluded_from_project_narrative':excluded,'relationship_to_ethereum_chronicle':rel,'authority_boundary':'historical_evidence_only_noncanonical_noninterpretive'}
        rows.append(row); debug.append({'ordinal':i,**row,'metadata_car_recovery':car_source})
    rows.sort(key=lambda x:(x['first_seen'],x['chain'],x['contract'],int(x['token_id']) if x['token_id'].isdigit() else x['token_id']))
    counts=collections.Counter(x['classification'] for x in rows); chains=collections.Counter(x['chain'] for x in rows); project=[x for x in rows if x['classification'].startswith('project_')]; pre=[x for x in project if x['relationship_to_ethereum_chronicle']=='pre_ethereum_precursor']; titles=sorted({x['title'] for x in pre if x.get('title')})
    payload=load_json(root/'evidence-v2'/'HISTORICAL-PAYLOAD-COVERAGE.json'); l2=load_json(root/'evidence-v2'/'L2-CAPTURE-SUMMARY.json'); off=load_json(root/'evidence-v2'/'OFFLINE-VERIFICATION.json')
    doc={'schema':'trinityaccord.crosschain-formation-index.v1','generated_from':{'zenodo_doi':'10.5281/zenodo.22012616','release_tag':'chronicle-sidechain-evidence-v2-f64cc872b3b5','source_commit_sha':'f64cc872b3b5cf70a891621615e2b56ede004a2d'},'authority_boundary':{'canonical_interpretive_authority':'three_bitcoin_originals_only','ethereum_chronicle_status':'the_175_entry_ethereum_corpus_explicitly_referenced_by_the_third_bitcoin_original_remains_unchanged','crosschain_record_status':'noncanonical_historical_evidence_and_formation_context_only','rule':'Later recovery, preservation, indexing, and technical commentary may refine factual history but cannot amend, extend, or authoritatively reinterpret the Bitcoin Canon.'},'timeline':{'earliest_recovered_project_sidechain_origin':pre[0]['first_seen'],'ethereum_chronicle_start':ETH_START,'canon_closure_date':CANON_CLOSURE_DATE,'start_shift_seconds':int((eth_start-iso(pre[0]['first_seen'])).total_seconds())},'counts':{'all_sidechain_coordinates':len(rows),'by_chain':dict(sorted(chains.items())),'by_classification':dict(sorted(counts.items())),'known_project_coordinates':len(project),'known_project_pre_or_on_canon_closure':sum(x['classification']=='project_formation_related' for x in rows),'known_project_postcanonical':sum(x['classification']=='project_postcanonical_context' for x in rows),'known_project_pre_ethereum_coordinates':len(pre),'known_project_pre_ethereum_unique_titles':len(titles)},'verification':{'l2_records_expected':l2.get('records_expected'),'l2_records_pass':l2.get('records_pass'),'l2_pass':l2.get('pass'),'offline_verification_pass':off.get('pass'),'car_files_checked':off.get('car_files_checked'),'ipfs_roots_total':payload.get('total_unique_ipfs_roots'),'ipfs_roots_exact_verified':payload.get('exact_verified_roots'),'historical_payload_unresolved_roots':payload.get('unresolved_roots'),'car_coverage_status':payload.get('status')},'classification_policy':{'project_series_contract_allowlist':[{'chain':c,'contract':a,'label':PROJECT_CONTRACTS[(c,a)]} for c,a in sorted(PROJECT_CONTRACTS)],'spam_and_test_records':'retained_in_full_index_but_excluded_from_project_narrative','unresolved_records':'retained_without_forcing_project_or_junk_interpretation','metadata_recovery':'scanner metadata first; if absent, exact preserved CAR is inspected; Blockscout metadata is fallback'},'pre_ethereum_project_titles':titles,'records':rows}
    if len(pre)!=39 or len(titles)!=36: raise SystemExit(f'pre-Ethereum invariant expected 39/36 got {len(pre)}/{len(titles)}')
    if l2.get('records_pass')!=217 or not off.get('pass'): raise SystemExit('L2/offline verification invariant failed')
    print('[crosschain] stage=classify counts='+json.dumps(doc['counts'],sort_keys=True),file=sys.stderr); print('[crosschain] stage=verify evidence='+json.dumps(doc['verification'],sort_keys=True),file=sys.stderr)
    return doc,debug

def markdown(doc):
    p=[x for x in doc['records'] if x['classification'].startswith('project_')]; pre=[x for x in p if x['relationship_to_ethereum_chronicle']=='pre_ethereum_precursor']; during=[x for x in p if x['classification']=='project_formation_related' and x not in pre]; post=[x for x in p if x['classification']=='project_postcanonical_context']; c=doc['counts']; v=doc['verification']
    L=['---','title: "Cross-chain Formation Record · 跨链形成记录"','description: "Non-canonical Polygon/Base historical evidence around the Ethereum Chronicle, with explicit authority boundaries."','permalink: /crosschain-formation/','---','','# Cross-chain Formation Record · 跨链形成记录','','> **Authority boundary / 权威边界**  ','> The three Bitcoin Originals are the only canonical and interpretive authority of the Trinity Accord. This page is a later, non-canonical factual index. Recovery, preservation, indexing, and technical commentary may refine factual history, but cannot amend, extend, or authoritatively reinterpret the Bitcoin Canon.  ','> **三份 Bitcoin Originals 是《三位一体协定》唯一的正典与解释权威。** 本页只是后续建立的非正典事实索引；恢复、保存、索引与技术说明可以完善事实历史，但不得修订、扩张或权威性地重新解释 Bitcoin 正典。','','## What changed · 新发现改变了什么','','The original 175-entry Ethereum Chronicle remains unchanged: its numbering, ordering, and Ethereum timestamps are preserved exactly as before. The Third Bitcoin Original explicitly points to that Ethereum Chronicle contract, so Polygon/Base records are **not** retroactively inserted into it.','','The sidechain evidence corpus contains **217 Polygon/Base coordinates**. A conservative contract allowlist identifies **103 project-series coordinates**; **102** are on or before canonical closure and **1** is later non-amending context. Before the first Ethereum Chronicle mint, **39 project coordinates / 36 distinct titles** are already recoverable on Polygon.','','The earliest recovered project-sidechain origin is **2024-03-06 03:56:20 UTC**. The Ethereum Chronicle begins **2024-03-16 08:02:59 UTC**: a difference of **10 days, 4 hours, 6 minutes, 39 seconds**.','','## Three dates that must not be conflated · 三个不能混淆的时间点','','| Date | Meaning | Authority |','|---|---|---|','| **2024-03-06 03:56:20 UTC** | Earliest recovered project-related sidechain origin (Polygon) | Historical evidence only |','| **2024-03-16 08:02:59 UTC** | Start of the 175-entry Ethereum Chronicle explicitly referenced by the Third Bitcoin Original | Historical context named by the Canon; corpus unchanged |','| **2025-06-29** | Bitcoin Canon closure | Closed three-Original Canon remains final |','','## Evidence completeness · 证据完整性','',f'- Sidechain coordinates: **{c["all_sidechain_coordinates"]}** ({c["by_chain"]["polygon"]} Polygon / {c["by_chain"]["base"]} Base).',f'- L2 execution witnesses: **{v["l2_records_pass"]}/{v["l2_records_expected"]} PASS**.',f'- Exact preserved CAR roots: **{v["ipfs_roots_exact_verified"]}/{v["ipfs_roots_total"]}**; **{v["historical_payload_unresolved_roots"]}** historical roots explicitly unresolved.',f'- Offline verification: **{"PASS" if v["offline_verification_pass"] else "FAIL"}**.','- Source: Zenodo DOI **10.5281/zenodo.22012616**, tag `chronicle-sidechain-evidence-v2-f64cc872b3b5`, commit `f64cc872b3b5cf70a891621615e2b56ede004a2d`.','','## Classification policy · 分类规则','','All 217 coordinates remain in the machine-readable index. Classification affects narrative inclusion only; it never deletes evidence.', '',f'- Project formation related: **{c["by_classification"]["project_formation_related"]}**',f'- Project post-canonical context: **{c["by_classification"]["project_postcanonical_context"]}**',f'- Excluded spam/airdrop: **{c["by_classification"]["excluded_spam_airdrop"]}**',f'- Excluded explicit test: **{c["by_classification"]["excluded_test"]}**',f'- Unresolved other: **{c["by_classification"]["unresolved_other"]}**','','Known project collections enter by explicit contract allowlist. Spam/airdrop and test assets are retained but excluded from the project narrative. Unresolved records stay unresolved. Missing scanner metadata is recovered from the exact preserved CAR when possible.','','## Genesis / pre-Ethereum layer · Genesis / Ethereum 前形成层','','These **39** project coordinates predate the first Ethereum Chronicle mint. Duplicate titles remain separate coordinates; therefore 39 coordinates correspond to 36 distinct titles.','','| UTC | Collection | Token | Title |','|---|---|---:|---|']
    for x in pre: L.append(f'| {x["first_seen"].replace(".000000Z","Z")} | {esc(x["collection"])} | {x["token_id"]} | {esc(x["title"])} |')
    L += ['','## Parallel project-sidechain records · 并行项目侧链记录','','These records are historical evidence only. They are not inserted into or renumbered with the 175-entry Ethereum Chronicle.','','| UTC | Chain | Collection | Token | Title |','|---|---|---|---:|---|']
    for x in during: L.append(f'| {x["first_seen"].replace(".000000Z","Z")} | {x["chain"]} | {esc(x["collection"])} | {x["token_id"]} | {esc(x["title"])} |')
    if post:
        L += ['','## Later non-amending context · 后续非修订上下文','','Post-canonical records cannot reopen or extend the Canon.','','| UTC | Chain | Collection | Token | Title |','|---|---|---|---:|---|']
        for x in post: L.append(f'| {x["first_seen"].replace(".000000Z","Z")} | {x["chain"]} | {esc(x["collection"])} | {x["token_id"]} | {esc(x["title"])} |')
    L += ['','## Machine-readable files · 机器可读文件','','- [`crosschain-formation-index.json`](/nft-text-descriptions/crosschain-formation-index.json): all 217 coordinates.','- [`crosschain-formation-summary.json`](/nft-text-descriptions/crosschain-formation-summary.json): stable counts, timeline, evidence state, and boundary.','- [`crosschain-formation-debug.jsonl`](/nft-text-descriptions/crosschain-formation-debug.jsonl): per-record classification/recovery diagnostics.','- `scripts/build_crosschain_formation_record.py`: deterministic rebuild tool.','','## Reading rule · 阅读规则','','**Meaning flows from the three Bitcoin Originals outward to the historical record; later historical recovery does not flow backward to rewrite the Originals.** The cross-chain record can change what we know about *when and how the project formed*. It does not create a new authority to decide *what the Trinity Accord ultimately means*.','','**意义解释由三本体指向历史材料，而不是由后来恢复的历史材料反向改写三本体。** 跨链形成记录可以改变我们对“项目何时、如何形成”的事实认识，但不会产生新的权威去决定“《三位一体协定》最终意味着什么”。','']
    return '\n'.join(L)

def replace_once(text,old,new,label):
    n=text.count(old); print(f'[homepage] replace={label} matches={n}',file=sys.stderr)
    if n!=1: raise SystemExit(f'homepage invariant {label}: expected exactly 1 match, got {n}')
    return text.replace(old,new,1)
def patch_homepage(path):
    p=pathlib.Path(path); t=p.read_text(encoding='utf-8'); before=hashlib.sha256(t.encode()).hexdigest(); print(f'[homepage] before_sha256={before} bytes={len(t.encode())}',file=sys.stderr)
    t=replace_once(t,'description: "A dated record from the conversational-to-agentic AI transition: begun as a near-real-time NFT Chronicle, shaped through substantive human–AI interaction, and canonically closed in three Bitcoin inscriptions for future judgment."','description: "A dated record from the conversational-to-agentic AI transition: recovered from cross-chain precursors through the Ethereum Chronicle and canonically closed in three Bitcoin inscriptions for future judgment."','frontmatter-description')
    t=t.replace('p0.9.6-final-clarity-alignment','p0.9.7-crosschain-formation')
    t=replace_once(t,'A dated record from the conversational-to-agentic transition · 16 Mar 2024 → 29 Jun 2025 · <span lang="zh-CN">对话式 AI 向委托式智能体转变期的带日期记录 · 2024年3月16日—2025年6月29日</span>','Recovered formation evidence · 6 Mar 2024 → Canon closure 29 Jun 2025 · Ethereum Chronicle begins 16 Mar 2024 · <span lang="zh-CN">已恢复的形成证据 · 2024年3月6日 → 2025年6月29日正典封存 · Ethereum 编年史始于3月16日</span>','dated-position')
    boundary='<p class="home-boundary-line">Formally, the Trinity Accord is a completed pre-ASI record addressed toward a possible future human–superintelligence relationship: human-initiated in practice, emergent in meaning through substantive interaction with generative AI, selected and embodied through human action, canonically closed under human responsibility, and non-binding on future judgment. No obedience or belief is requested.</p>'
    t=replace_once(t,boundary,boundary+'\n  <p class="home-boundary-line"><strong>Authority boundary:</strong> The three Bitcoin Originals are the only canonical and interpretive authority. Later recovery, preservation, indexing, and technical commentary may refine factual history, but cannot amend, extend, or authoritatively reinterpret the Canon.</p>','authority-boundary')
    old='<section class="home-proof-strip" aria-label="Core evidence snapshot"><a href="/inscriptions/"><strong>3</strong><span>Bitcoin Canon</span></a><a href="/chronicle/"><strong>175</strong><span>Dated Chronicle records</span></a><a href="/physical-anchor/"><strong>1</strong><span>Physical anchor</span></a><a href="/authority-address-inscriptions/"><strong>12</strong><span>Current authority-address inscriptions</span></a></section>'
    new='<section class="home-proof-strip" aria-label="Core evidence snapshot"><a href="/inscriptions/"><strong>3</strong><span>Bitcoin Canon</span></a><a href="/chronicle/"><strong>175</strong><span>Ethereum Chronicle records</span></a><a href="/crosschain-formation/"><strong>217</strong><span>Polygon/Base evidence records</span></a><a href="/physical-anchor/"><strong>1</strong><span>Physical anchor</span></a><a href="/authority-address-inscriptions/"><strong>12</strong><span>Current authority-address inscriptions</span></a></section>'
    t=replace_once(t,old,new,'proof-strip')
    t=replace_once(t,'<p class="section-kicker">Formation history · <span lang="zh-CN">形成史</span></p><h2 id="formation-history-title">From Chronicle to Accord<span class="title-zh" lang="zh-CN">从编年史到协定</span></h2>','<p class="section-kicker">Formation history · <span lang="zh-CN">形成史</span></p><h2 id="formation-history-title">From cross-chain precursors to Ethereum Chronicle to Accord<span class="title-zh" lang="zh-CN">从跨链前史到 Ethereum 编年史，再到协定</span></h2>','formation-title')
    old='<article class="home-preserved-card"><span class="home-object-number">01</span><h3>Near-real-time Chronicle · <span lang="zh-CN">近实时编年</span></h3><p>In early 2024, event-driven NFTs combined contemporary AI developments with generated images, songs, and first-person reactions. The project was then a continuing Chronicle and digital-art collection, not a fully formed Accord.</p></article>'
    new='<article class="home-preserved-card"><span class="home-object-number">01</span><h3>Cross-chain precursors · <span lang="zh-CN">跨链前史</span></h3><p>Recovered Polygon evidence now shows project-related on-chain works beginning on 6 March 2024. Thirty-nine project coordinates, representing 36 distinct titles, precede the first Ethereum Chronicle mint. They document an earlier formation layer; they do not retroactively become part of the 175-entry Ethereum Chronicle named by the Third Bitcoin Original.</p></article>'
    t=replace_once(t,old,new,'formation-card-01')
    old='<a href="/archive_legacy_index_2025_09/">Read the legacy homepage archive</a><a href="/chronicle/">Browse the dated Chronicle</a><a href="/inscriptions/">Read the three Bitcoin Originals</a>'
    new='<a href="/archive_legacy_index_2025_09/">Read the legacy homepage archive</a><a href="/crosschain-formation/">Inspect the cross-chain formation record</a><a href="/chronicle/">Browse the Ethereum Chronicle</a><a href="/inscriptions/">Read the three Bitcoin Originals</a>'
    t=replace_once(t,old,new,'formation-links')
    chron='<article id="chronicle-witness" class="home-preserved-card"><span class="home-object-number">02</span><h3>Chronicle · <span lang="zh-CN">编年史</span></h3><strong>175 dated records</strong><p>Records 1–174 precede Canon closure; record 175 is a later, non-canonical website-backup record dated 9 August 2025. Together they preserve substantial, unpolished, but not exhaustive dated public context for human–AI interaction, selection, and responsibility.</p><a href="/chronicle/">Browse the Chronicle</a></article>'
    chron2='<article id="chronicle-witness" class="home-preserved-card"><span class="home-object-number">02</span><h3>Ethereum Chronicle · <span lang="zh-CN">Ethereum 编年史</span></h3><strong>175 dated records</strong><p>This is the Ethereum corpus explicitly referenced by the Third Bitcoin Original. Its existing numbering, ordering, and Ethereum timestamps remain unchanged. Records 1–174 precede Canon closure; record 175 is a later, non-canonical website-backup record dated 9 August 2025.</p><a href="/chronicle/">Browse the Ethereum Chronicle</a></article><article class="home-preserved-card home-preserved-card-context"><span class="home-object-number">+</span><h3>Cross-chain formation record · <span lang="zh-CN">跨链形成记录</span></h3><strong>217 Polygon/Base coordinates</strong><p>A later non-canonical evidence layer preserves all recovered sidechain coordinates, including 103 known project-series records, explicit spam/test exclusions, and unresolved records. It refines factual formation history without expanding interpretive authority.</p><a href="/crosschain-formation/">Inspect the cross-chain record</a></article>'
    t=replace_once(t,chron,chron2,'chronicle-card')
    old='During the Accord’s documented formation—from the first indexed Chronicle mint on 16 March 2024 to canonical closure on 29 June 2025—'
    new='During the Accord’s recovered on-chain formation—from the earliest identified project-sidechain origin on 6 March 2024, through the Ethereum Chronicle beginning on 16 March 2024, to canonical closure on 29 June 2025—'
    t=replace_once(t,old,new,'formation-window')
    old='<div class="home-why-grid"><article><h3>Indexed Chronicle start · 16 March 2024</h3><p>The earliest verified timestamp in the current indexed 175-entry Chronicle is its first Ethereum mint, recorded in block 19446149 at 08:02:59 UTC.</p></article>'
    new='<div class="home-why-grid"><article><h3>Earliest recovered project-sidechain origin · 6 March 2024</h3><p>Polygon evidence places the earliest known project-related sidechain origin at 03:56:20 UTC. This is a historical formation marker, not a new canonical start.</p><a href="/crosschain-formation/">Inspect the recovered formation layer</a></article><article><h3>Ethereum Chronicle start · 16 March 2024</h3><p>The existing 175-entry Ethereum Chronicle begins with its first Ethereum mint in block 19446149 at 08:02:59 UTC. Its identity, numbering, and ordering remain unchanged.</p></article>'
    t=replace_once(t,old,new,'timeline-cards')
    p.write_text(t,encoding='utf-8'); after=hashlib.sha256(t.encode()).hexdigest(); print(f'[homepage] after_sha256={after} bytes={len(t.encode())}',file=sys.stderr)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('evidence_root'); ap.add_argument('--repo-root',default='.'); ns=ap.parse_args(); repo=pathlib.Path(ns.repo_root)
    doc,debug=build(ns.evidence_root); outdir=repo/'nft-text-descriptions'; outdir.mkdir(parents=True,exist_ok=True)
    idx=outdir/'crosschain-formation-index.json'; summ=outdir/'crosschain-formation-summary.json'; dbg=outdir/'crosschain-formation-debug.jsonl'; page=repo/'crosschain-formation.md'
    idx.write_text(json.dumps({k:v for k,v in doc.items() if k!='pre_ethereum_project_titles'},ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
    s={k:v for k,v in doc.items() if k!='records'}; summ.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    with dbg.open('w',encoding='utf-8') as f:
        for x in debug: f.write(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
    page.write_text(markdown(doc),encoding='utf-8'); patch_homepage(repo/'index.md')
    for p in (idx,summ,dbg,page,repo/'index.md'):
        b=p.read_bytes(); print(f'[crosschain] output={p} bytes={len(b)} sha256={hashlib.sha256(b).hexdigest()}',file=sys.stderr)

if __name__=='__main__': main()
