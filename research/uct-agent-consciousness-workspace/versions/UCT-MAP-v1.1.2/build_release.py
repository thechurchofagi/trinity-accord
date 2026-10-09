#!/usr/bin/env python3
"""Assemble exact reviewed inputs; this checker does not perform semantic review."""
from pathlib import Path
import argparse, copy, csv, hashlib, json

VERSION='UCT-MAP-v1.1.2'
AUDIT='R188-ALLMAP-COMPAT-20261009-v1'
MODULES=['R185','HOM','UI20261009','CM20261009','R187','R188']
RESEARCH_IDS=['R185','R186-HOM-20261009','UI20261009','CM20261009','R187-CMA-20261009','R188-CER-20261009']
REVIEWS=['BASELINE_PER_ID_SEMANTIC_REVIEW.json','R185_HOM_R187_PER_ID_REVIEW.json','UI_CM_REVIEW.json','R188_PER_ID_REVIEW.json']
COLLECTIONS={'nodes':'node','rules':'rule','context_links':'context'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def objsha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def build(root):
    baseline=root/'inputs/baseline/UCT_EFFECTIVE_GRAPH.json'
    old=read(baseline);graph=copy.deepcopy(old)
    patch=read(root/'audit/R173_EFFECTIVE_CORRECTION_PATCH.json')
    assert sha(baseline)==patch['expected_baseline_file_sha256']
    assert old['version']=='UCT-MAP-v1.1.1'
    old_items={x['id']:x for col in COLLECTIONS for x in old[col]}
    changes=[]
    for op in patch['operations']:
        target=next(x for x in graph[op['collection']] if x['id']==op['id'])
        assert objsha(target)==op['expected_record_sha256'],op['id']
        before=copy.deepcopy(target);target.update(op['set'])
        changes.append({'item_id':op['id'],'collection':op['collection'],'historical_record':before,'historical_record_sha256':objsha(before),'effective_record_sha256':objsha(target),'operation':op})
    added={col:[] for col in COLLECTIONS};module_manifest=[]
    for module,rid in zip(MODULES,RESEARCH_IDS):
        file=root/'normalized'/f'{module}.json';d=read(file)
        module_manifest.append({'research_id':rid,'normalized_member':str(file.relative_to(root)),'sha256':sha(file),'nodes':len(d['nodes']),'active_conditional_rules':len(d['rules']),'nondeductive_context_links':len(d['context_links']),'integration':'REVIEWED_CONDITIONAL_DECLARATIONS_NOT_PREMISE_TRUTH'})
        for col in COLLECTIONS:
            graph[col].extend(copy.deepcopy(d[col]));added[col].extend(x['id'] for x in d[col])
    graph.update({'version':VERSION,'parent_release':'UCT-MAP-v1.1.1','audit_id':AUDIT,'modules_added':RESEARCH_IDS,'pending_not_loaded':['AC20261009','IL20261009'],'current_module_registry':module_manifest,'effective_corrections':changes,'conditional_schema_availability':'Only active rules under all complete same-instance contracts. Node registration and source status do not discharge premises. This is not an autonomous theorem prover.','review_scope':'All 1608 effective item contracts received semantic compatibility decisions; original source proofs retained except specified rederivations. Not independent re-proof of all history, empirical validation, reviewer finding closure or global consistency proof.','actual_application_status':'OPEN','named_phenomenal_application_status':'OPEN','scientific_premise_promotion':False})
    graph.pop('added_module',None);graph.pop('module_added',None)
    maps={col:{x['id']:x for x in graph[col]} for col in COLLECTIONS}
    for col in COLLECTIONS:assert len(maps[col])==len(graph[col]),('duplicate',col)
    ids=set().union(*(set(v) for v in maps.values()));assert len(ids)==sum(len(v) for v in maps.values())
    nids=set(maps['nodes']);rids=set(maps['rules']);suspended=set(graph['suspended_historical_rule_ids'])
    assert not suspended&rids
    assert suspended==set(old['suspended_historical_rule_ids'])
    assert len(suspended)==10
    for rule in graph['rules']:
        assert set(rule['all_of'])<=nids,rule['id']
        assert rule['conclusion'] in nids,rule['id']
        assert rule.get('same_instance_required') is True,rule['id']
    assert all(maps['rules'][rid]['conclusion'] in set(added['nodes']) for rid in added['rules'])
    references=[];known_modules=set(RESEARCH_IDS+['CORE20261008','EI20261008','R183','OO20261008','RU20261008','R184','RC20261008','IE20261008','TH20261009','RB20261009','OL20261009'])
    for ctx in graph['context_links']:
        assert ctx.get('deductive') is False,ctx['id']
        for side,alias,typkey,oldkey in [('from','source','source_type','from_type'),('to','target','target_type','to_type')]:
            value=ctx.get(side,ctx.get(alias));typ=ctx.get(typkey,ctx.get(oldkey,'node'))
            if value in ids:continue
            if typ in ['module','module_reference']:assert value in known_modules,(ctx['id'],value)
            elif typ in ['source_reference','external_reference']:assert value is not None,(ctx['id'],side)
            else:raise AssertionError(('unresolved context',ctx['id'],side,value,typ))
            references.append({'context_id':ctx['id'],'side':side,'reference':value,'type':typ,'deductive':False})
    changedids={x['item_id'] for x in changes}
    for iid,record in old_items.items():
        effective=next(m[iid] for m in maps.values() if iid in m)
        assert iid in changedids or effective==record,('unintended old change',iid)
    review_rows=[]
    for review_name in REVIEWS:
        review=read(root/'audit'/review_name)
        for row in review['items']:
            iid=row.get('item_id',row.get('id'));typ=row.get('item_type',row.get('record_type'))
            if typ=='context_link':typ='context'
            output={'item_id':iid,'item_type':typ,'source_review':'audit/'+review_name,'semantic_review':row,'actual_premise_discharged_by_review':False}
            if typ=='suspended_historical_rule':
                assert iid in suspended
                output.update({'review_outcome':'RETAIN_SUSPENDED_NONEXECUTABLE','active_inference_permitted':False})
            else:
                col=next(k for k,v in COLLECTIONS.items() if v==typ);record=maps[col][iid]
                expected=row.get('normalized_record_sha256',row.get('baseline_record_sha256'))
                assert expected is not None,(iid,'no hash')
                if iid in changedids:
                    assert objsha(old_items[iid])==expected
                    output['applied_effective_correction']=next(c for c in changes if c['item_id']==iid)
                    output['review_outcome']='EFFECTIVE_SCOPE_CORRECTION_APPLIED_HISTORY_PRESERVED'
                else:
                    assert objsha(record)==expected,('review hash mismatch',iid,objsha(record),expected)
                    output['review_outcome']=row.get('review_outcome',row.get('review_verdict'))
                output['effective_record_sha256']=objsha(record)
            review_rows.append(output)
    coverage_ids=[r['item_id'] for r in review_rows]
    assert len(coverage_ids)==len(set(coverage_ids))
    assert set(coverage_ids)==ids|suspended
    counts={'nodes':len(graph['nodes']),'active_conditional_rules':len(graph['rules']),'suspended_historical_rules':len(suspended),'nondeductive_context_links':len(graph['context_links']),'total_review_items':len(review_rows)}
    assert counts=={'nodes':913,'active_conditional_rules':424,'suspended_historical_rules':10,'nondeductive_context_links':261,'total_review_items':1608},counts
    ledger={'schema':'uct-effective-semantic-review-ledger/1.0','release':VERSION,'audit_id':AUDIT,'counts':counts,'method':'Full effective-contract reading and substantive family/per-item review are preserved in the input audit documents. This program only verifies assembly and exact record coverage; executing it does not conduct semantic review.','source_proof_scope':'Prior proofs retained, specified affected arguments rederived. No independent re-proof of every historical theorem or empirical validation.','reviewer_controlled_open_statuses_changed':False,'actual_or_named_phenomenal_premises_discharged':False,'items':review_rows}
    write(root/'UCT_EFFECTIVE_GRAPH.json',graph);write(root/'REVIEW_LEDGER.json',ledger)
    with (root/'REVIEW_LEDGER.csv').open('w',newline='') as f:
        fields=['item_id','item_type','review_outcome','source_review','effective_record_sha256'];writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        writer.writerows({k:r.get(k,'') for k in fields} for r in review_rows)
    lines=['# Complete effective formal map — '+VERSION,'','This is a complete readable serialization of every effective record. Scientific clauses and historical source metadata are preserved. Rules are conditional, contexts do not infer, and ten historical rules remain suspended. Per-item decisions are in REVIEW_LEDGER.json. Full compatibility review is not empirical validation or independent re-proof of all source arguments.','']
    for col,typ in COLLECTIONS.items():
        lines+=['## '+col,'']
        for item in graph[col]:lines+=['### '+item['id'],'','```json',json.dumps(item,ensure_ascii=False,indent=2),'```','']
    lines+=['## Suspended historical rule IDs','','```json',json.dumps(graph['suspended_historical_rule_ids'],indent=2),'```','']
    (root/'UCT_FORMAL_MAP_COMPLETE.md').write_text('\n'.join(lines))
    receipt={'schema':'uct-release-build-receipt/1.0','release':VERSION,'audit_id':AUDIT,'status':'ALL_ASSEMBLY_CHECKS_PASSED','counts':counts,'baseline_file_sha256':sha(baseline),'effective_graph_sha256':sha(root/'UCT_EFFECTIVE_GRAPH.json'),'review_ledger_sha256':sha(root/'REVIEW_LEDGER.json'),'complete_readable_map_sha256':sha(root/'UCT_FORMAL_MAP_COMPLETE.md'),'modules':module_manifest,'added_item_ids':added,'changed_item_ids':sorted(changedids),'suspended_rule_ids_preserved':sorted(suspended),'nonnode_context_references':references,'pending_not_integrated':['AC20261009','IL20261009'],'checks':['Exact baseline and correction guards','Every new record matches its reviewed normalized hash','Unique item IDs and exact1608-item review coverage','Every active rule premise/head resolves to a node','Same-instance rule guards present; all47new rule heads are new nodes','Every context resolves by its declared reference type and is non-deductive','All10historical rule suspensions retained','Every prior record except two explicitly corrected records is unchanged'],'semantic_review_performed_by_this_program':False}
    write(root/'BUILD_RECEIPT.json',receipt)
    print(json.dumps({k:receipt[k] for k in ['release','status','counts','effective_graph_sha256','review_ledger_sha256']},ensure_ascii=False))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent);args=parser.parse_args();build(args.root)
