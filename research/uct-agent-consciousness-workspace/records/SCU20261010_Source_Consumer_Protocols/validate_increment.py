#!/usr/bin/env python3
"""Mechanical integrity checks; never a semantic or empirical certification.

Run in the repository. Optional --completed-graph and --completed-ledger verify
the exact restored base bytes. Reproduction is separately handled by
reproduce_all.py. This validator does not change source or candidate files.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
GRAPH_SHA='0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612'
LEDGER_SHA='0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687'

def h(data): return hashlib.sha256(data).hexdigest()
def read(p): return json.loads(p.read_text())
def record_hash(d):
    return h(json.dumps(d,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--completed-graph',type=Path)
    parser.add_argument('--completed-ledger',type=Path)
    args=parser.parse_args()
    checks=[]
    def check(name,condition,detail=None):
        if not condition: raise AssertionError(name)
        checks.append({'check':name,'passed':True,'detail':detail})

    manifest=read(BASE/'review/FINAL_AUDIT_MANIFEST.json')
    for f in manifest['recommended_files']+manifest['optional_audit_serialization_tooling']:
        p=BASE/'review'/f['path']; b=p.read_bytes()
        check('auditor file hash: '+f['path'],len(b)==f['bytes'] and h(b)==f['sha256'])
    logical=gzip.decompress((BASE/'review/PER_ITEM_SEMANTIC_REVIEW.json.gz').read_bytes())
    check('compressed ledger exact logical bytes',len(logical)==manifest['compressed_ledger']['logical_bytes'] and h(logical)==manifest['compressed_ledger']['logical_sha256'])
    ledger=json.loads(logical);items=ledger['items'];base_ids={x['item_id'] for x in items}
    base_node_ids={x['item_id'] for x in items if x['item_type']=='node'}
    check('base item uniqueness/count',len(items)==len(base_ids)==1608 and len(base_node_ids)==913)
    check('statement unread set empty',ledger['statement_level_unread_ids']==[])
    unread=read(BASE/'review/EXACT_UNREAD_SCOPE.json')
    check('deeper audit not promoted',unread['status']=='AUDIT_INCOMPLETE' and len(unread['unreviewed_full_raw_contract_ids'])==901)
    check('frozen base provenance',ledger['base_graph_sha256']==GRAPH_SHA and ledger['frozen_release_ledger_sha256']==LEDGER_SHA)
    if args.completed_graph: check('actual restored completed graph bytes',h(args.completed_graph.read_bytes())==GRAPH_SHA)
    if args.completed_ledger: check('actual restored completed ledger bytes',h(args.completed_ledger.read_bytes())==LEDGER_SHA)

    candidate=read(BASE/'MAP_EXTENSION.json')
    counts={k:len(candidate[k]) for k in ('nodes','rules','context_links')}
    check('SCU candidate counts',counts=={'nodes':23,'rules':8,'context_links':16},counts)
    all_candidates=candidate['nodes']+candidate['rules']+candidate['context_links']
    ids=[x['id'] for x in all_candidates]
    check('SCU unique IDs and no base overwrite',len(ids)==len(set(ids)) and not (set(ids)&base_ids))
    check('SCU disabled',candidate['enabled_as_established_premise'] is False and all(x['enabled_as_established_premise'] is False for x in all_candidates))
    new_node_ids={x['id'] for x in candidate['nodes']};known_nodes=base_node_ids|new_node_ids
    for rule in candidate['rules']:
        check('SCU references/binding: '+rule['id'],all(x in known_nodes for x in rule['all_of']+[rule['conclusion']]) and rule['same_instance_required'] is True and bool(rule['binding']))
    for ctx in candidate['context_links']:
        check('SCU nondeductive references: '+ctx['id'],ctx['from'] in known_nodes and ctx['to'] in known_nodes and ctx['deductive'] is False)

    index=read(BASE/'corrections/EFFECTIVE_CORRECTION_INDEX.json');overrides=0;new_nodes=0;new_rules=0
    for entry in index['overlays']:
        p=BASE/'corrections'/entry['path'];check('correction index hash: '+entry['path'],h(p.read_bytes())==entry['sha256'])
        d=read(p);old_records={}
        for src in d['sources']:
            original=ROOT/src['path'];check('historical source preserved: '+src['path'],h(original.read_bytes())==src['sha256'])
            if original.name=='MAP_EXTENSION.json':
                smap=read(original)
                for k in ('nodes','rules','context_links'):
                    old_records.update({x['id']:x for x in smap[k]})
        check('overlay disabled: '+d['overlay_id'],d['enabled_as_established_premise'] is False and d['completed_map_changed'] is False and d['actual_premises_discharged'] is False)
        for override in d['effective_overrides']:
            tid=override['target_id'];check('original record hash: '+tid,tid in old_records and record_hash(old_records[tid])==override['expected_original_record_sha256'])
            check('override not completed record: '+tid,tid not in base_ids)
            overrides+=1
        new_nodes+=len(d['nodes']);new_rules+=len(d['rules'])
    check('correction counts', (overrides,new_nodes,new_rules)==(8,6,2),{'overrides':overrides,'nodes':new_nodes,'rules':new_rules})

    state=read(ROOT/'CURRENT_STATE.json');graph=read(ROOT/'UCT_FORMAL_GRAPH_MODULES.json');reg=read(ROOT/'RESEARCH_REGISTRY.json');session=read(ROOT/'RESEARCH_SESSION_LOG_INDEX.json');pub=read(ROOT/'PUBLICATION_COVERAGE.json')
    check('completed status/counts preserved',state['release_id']=='UCT-MAP-v1.1.2' and state['complete_map_sha256']==GRAPH_SHA and state['review_ledger_sha256']==LEDGER_SHA and state['counts']=={'nodes':913,'active_conditional_rules':424,'suspended_historical_rules':10,'nondeductive_context_links':261,'total_review_items':1608})
    expected=set(state['pending_checkpoints_not_promoted'])
    check('pending navigation consistent',len(expected)==21 and expected=={x['id'] for x in graph['pending_checkpoints']}=={x['research_id'] for x in reg['pending_checkpoints']}==set(session['pending_checkpoints']))
    check('all pending remain disabled',all(x['enabled_as_established_premises'] is False for x in graph['pending_checkpoints']+reg['pending_checkpoints']))
    for row in graph['pending_checkpoints']:
        p=ROOT/row['path'];check('pending map exists: '+row['id'],p.is_file())
        if 'sha256' in row:check('pending map hash: '+row['id'],h(p.read_bytes())==row['sha256'])
    check('current coverage consistent',pub['coverage_version']==state['publication_coverage']['version']==graph['publication_coverage']['version']==reg['publication_coverage']['version']==session['publication_coverage']['version']=='UCT-PUB-v1.0.18')
    check('QC obligations unchanged',state['qc_open']==['QC-20261008-10','IA-QC11','QC-20261008-12','QC-20261008-13'] and state['actual_premise_discharge'] is False)
    qa=read(BASE/'PDF_QA_RECEIPT.json')
    check('final PDF/source reviewed hashes',h((BASE/'Matched_Behavior_and_Source_Use_v1.0.0.pdf').read_bytes())==qa['pdf_sha256'] and h((BASE/'Matched_Behavior_and_Source_Use_v1.0.0.md').read_bytes())==qa['markdown_sha256'])
    for f in ('HANDOFF.md','MEMORY.md','MASTER_INDEX.md'):
        check('complete earlier navigation preserved: '+f,(ROOT/f).read_bytes().endswith((BASE/'history/root_at_7dd9564c'/f).read_bytes()))
    result={'schema':'uct-scu-mechanical-integrity/1','status':'PASS_MECHANICAL_INTEGRITY_ONLY','checks':checks,'check_count':len(checks),'semantic_certification':False,'actual_premise_discharge':False,'new_completed_map_release':False,'separate_semantic_review':'MAP_AUDIT.md'}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
