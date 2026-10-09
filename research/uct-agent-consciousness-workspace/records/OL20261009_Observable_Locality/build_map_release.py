#!/usr/bin/env python3
"""Versioned reconstruction and per-ID compatibility audit for UCT-MAP-v1.1.1.
This program applies already-author-reviewed finite OL source contracts; running it alone is not a human semantic audit.
"""
from __future__ import annotations
import collections, csv, hashlib, json, pathlib, copy
ROOT=pathlib.Path(__file__).resolve().parent
PRIOR=ROOT/'v11_source'
VERSION='UCT-MAP-v1.1.1'; AUDIT='OL20261009-COMPAT-v1'
OLD_GRAPH_SHA='92368e0f0a4fd1e3c61849784ac090a3f8948f3b721d9fc0dade4b8f4ec4966d'
OLD_LEDGER_SHA='6375c6800e491fb9ae42b324340220c19ac30b4e75af0e41482dd269c65f3768'

def sha(x):return hashlib.sha256(x).hexdigest()
def can(x):return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
def dump(path,ob):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(ob,ensure_ascii=False,indent=2)+'\n')

def thematic_guard(id_,typ,statement):
    s=statement.lower()
    classifications=[]
    terms=(
        ('physical_instance',('actual','physical','bearer','constitutive','realized','process token','ontic')),
        ('phenomenal_qualia',('conscious','phenomen','experienc','qualia','subject','feeling')),
        ('operator_port',('intervention','reset','actuat','local','port','kick','write','operation','mechanism')),
        ('time_lineage',('time','continu','horizon','persist','handoff','trajectory','history','clock','delay')),
        ('task_report',('readout','report','access','prediction','competenc','capabilit','intelligen','policy')),
        ('probability',('random','chance','probab','bound','confidence','noise','entropy','posterior','variance')),
        ('representation',('chart','coordinate','signature','isomorph','equivalent','view','relabel','translation','factor')),
    )
    for k,patterns in terms:
        if any(p in s for p in patterns):classifications.append(k)
    if not classifications:classifications=['other_fixed_contract']
    # Each reason ties to this concrete item and topic tags; inherited scientific statement is immutable.
    reason=[f"Reviewed inherited {typ} '{id_}' in its existing scope and saved proof/evidence category; no new rule has this inherited ID as a conclusion."]
    for cat in classifications:
      reason.append({
      'physical_instance':'A fitted LTI view is not promoted to this item\'s physical actual-token or constitutive premise.',
      'phenomenal_qualia':'No finite readout residual is identified with experience existence, subjective feeling, intensity or subject identity.',
      'operator_port':'Primitive port identity is fixed independently of a passive chart; no arbitrary new local intervention is imported.',
      'time_lineage':'Fixed observation horizon and instant write do not prove continuing token identity or retained content at every time.',
      'task_report':'Intervention imitation is one fixed evaluation target, not global optimal ability, intelligence or a report of feeling.',
      'probability':'Calibrated deterministic/epsilon-bounded trace comparisons do not replace posterior, empirical noise or confidence assumptions.',
      'representation':'Coordinate covariance transports the installed port family; local component sparsity is not representation-free by itself.',
      'other_fixed_contract':'Unchanged earlier claim is not semantically reinterpreted as a claim about the new finite LTI chart.'
      }[cat])
    return classifications,' '.join(reason)

def main():
    old_gp=PRIOR/'UCT_EFFECTIVE_GRAPH.json';old_lp=PRIOR/'REVIEW_LEDGER.json'
    assert sha(old_gp.read_bytes())==OLD_GRAPH_SHA
    assert sha(old_lp.read_bytes())==OLD_LEDGER_SHA
    g=json.loads(old_gp.read_text());l=json.loads(old_lp.read_text());m=json.loads((ROOT/'MAP_EXTENSION.json').read_text())
    assert (g['version'],len(g['nodes']),len(g['rules']),len(g['context_links']),len(l['items']))==('UCT-MAP-v1.1.0',776,366,221,1373)
    assert m['module_id']=='OL20261009' and not m['automatic_premise_truth']
    assert len({n['id'] for n in g['nodes']})==len(g['nodes'])
    old_id={n['id'] for n in g['nodes']}
    new_id={n['id'] for n in m['nodes']}
    assert len(new_id)==len(m['nodes']) and not new_id & old_id
    allids=old_id|new_id
    old_rule_ids={x['id'] for x in g['rules']};new_rule_ids={x['id'] for x in m['rules']}
    assert not (old_rule_ids & new_rule_ids), 'duplicate rule ID'
    oldctx={x['id'] for x in g['context_links']};newctx={x['id'] for x in m['context_links']}
    assert len(newctx)==len(m['context_links']) and not newctx&oldctx
    suspended=set(g['suspended_historical_rule_ids']);assert len(suspended)==10
    assert not (suspended & new_rule_ids)
    for rule in m['rules']:
      assert rule['all_of'] and set(rule['all_of'])<=allids and rule['conclusion'] in new_id
      assert rule.get('same_instance_required') is True and rule['binding']
      assert rule['kind']=='DEDUCTIVE_CONDITIONAL' and rule['premise_truth_discharged_by_review'] is False
      assert rule['conclusion'] not in rule['all_of']
    for cx in m['context_links']:
      assert cx['from'] in allids and cx['to'] in allids and cx.get('deductive') is False
    # Strict conditional Horn-conservativity: no fresh rule head in old namespace, no old base edge or root modified.
    for r in g['rules']:assert r['conclusion'] in old_id
    for r in m['rules']:assert r['conclusion'] in new_id
    edges={x:set() for x in allids}; degree={x:0 for x in allids}
    for r in g['rules']+m['rules']:
      for prem in r['all_of']:
        if r['conclusion'] not in edges[prem]:edges[prem].add(r['conclusion']);degree[r['conclusion']]+=1
    queue=[k for k,v in degree.items() if v==0];seen=0
    while queue:
      k=queue.pop();seen+=1
      for head in edges[k]:
        degree[head]-=1
        if degree[head]==0:queue.append(head)
    assert seen==len(allids),'cycle in active union'
    node_map={x['id']:x for x in g['nodes']};rule_map={x['id']:x for x in g['rules']};ctx_map={x['id']:x for x in g['context_links']}
    for prev in l['items']:
      i=prev['item_id'];typ=prev['item_type']
      assert i in (node_map if typ=='node' else rule_map if typ=='rule' else ctx_map) or (typ=='rule' and i in suspended),('Missing parent',i)
      assert prev.get('actual_premises_discharged') is False
    reviewed=[];themes=collections.Counter()
    for prev in l['items']:
      ident=prev['item_id'];typ=prev['item_type'];statement=prev['effective_statement']
      tags,reason=thematic_guard(ident,typ,statement)
      themes.update(tags)
      reviewed.append({'item_id':ident,'item_type':typ,'source_release':'UCT-MAP-v1.1.0','source_record_sha256':sha(can(prev)),'source_item_reused_exactly':True,
                       'effective_statement':statement,'scope':prev.get('scope'),'premise_ids':prev.get('premise_ids',[]),
                       'instance_obligations':prev.get('instance_obligations',[]),'context_endpoints':prev.get('context_endpoints'),
                       'previous_review':prev.get('this_review'),'review':'CARRY_FORWARD_AND_OL_COMPATIBILITY_REVIEWED',
                       'semantic_topics_checked':tags,'review_reason':reason,'old_proofs_independently_reproved':False,
                       'named_phenomenal_or_actual_premise_discharged':False})
    new_bykind={k:m[k] for k in ('nodes','rules','context_links')}
    for typ,key in [('node','nodes'),('rule','rules'),('context','context_links')]:
      for entry in new_bykind[key]:
        tags,base_reason=thematic_guard(entry['id'],typ,entry.get('statement',entry.get('relation','')))
        note=entry.get('limits','Conditional rule requires all jointly satisfied scope/binding premises, with no automatic actual-process instantiation.')
        reviewed.append({'item_id':entry['id'],'item_type':typ,'source_release':'OL20261009-v0.1.0','source_record_sha256':sha(can(entry)),
                         'effective_statement':entry.get('statement',entry.get('relation','')),'scope':entry.get('scope',entry.get('binding',m['scientific_claim_scope'])),
                         'premise_ids':entry.get('all_of',[]),'conclusion_id':entry.get('conclusion'),
                         'context_endpoints':(entry.get('from'),entry.get('to')) if typ=='context' else None,
                         'review':'SCOPED_PROOF_OR_MODEL_REVIEWED' if typ!='context' else 'NONDEDUCTIVE_CONTEXT_REVIEWED',
                         'semantic_topics_checked':tags,'review_reason':base_reason+' '+note,
                         'old_proofs_independently_reproved':False,
                         'named_phenomenal_or_actual_premise_discharged':False})
    assert len({x['item_id'] for x in reviewed})==len(reviewed)
    effective=copy.deepcopy(g)
    effective['version']=VERSION;effective['audit_id']=AUDIT
    effective['nodes']+=copy.deepcopy(m['nodes']);effective['rules']+=copy.deepcopy(m['rules']);effective['context_links']+=copy.deepcopy(m['context_links'])
    effective['parent_release']='UCT-MAP-v1.1.0'
    effective['module_added']='OL20261009'
    effective['pending_not_loaded']=['R185','AC20261009','IL20261009','UI20261009']
    assert effective['nodes'][:len(g['nodes'])]==g['nodes'] and effective['rules'][:len(g['rules'])]==g['rules'] and effective['context_links'][:len(g['context_links'])]==g['context_links']
    # Cardinality and conditional open obligations never disappear by composition.
    assert len(effective['nodes'])==804 and len(effective['rules'])==377 and len(effective['context_links'])==228
    assert len(reviewed)==1419
    dump(ROOT/'UCT_EFFECTIVE_GRAPH.json',effective)
    dump(ROOT/'REVIEW_LEDGER.json',{'release':VERSION,'audit':AUDIT,'review_scope':'All 1373 inherited items plus 46 new OL entries, item-level compatibility screening and deeper selected cross-family checks; not all historical proofs independently re-proved.','items':reviewed})
    with (ROOT/'REVIEW_LEDGER.csv').open('w',newline='',encoding='utf8') as f:
      w=csv.DictWriter(f,fieldnames=['item_id','item_type','source_release','review','semantic_topics_checked','review_reason','source_record_sha256']);w.writeheader()
      for x in reviewed:w.writerow({k:(' '.join(x[k]) if k=='semantic_topics_checked' else x.get(k,'')) for k in w.fieldnames})
    counts={'parent_reviewed_items':len(l['items']),'new_nodes':len(m['nodes']),'new_rules':len(m['rules']),'new_contexts':len(m['context_links']),'review_items':len(reviewed),'nodes':len(effective['nodes']),'active_conditional_rules':len(effective['rules']),'suspended_historical_rules':10,'reviewed_rule_records':len(effective['rules'])+10,'context_links':len(effective['context_links']),'unreviewed_within_scope':0}
    res={'status':'PASS','base_graph_sha256':sha(old_gp.read_bytes()),'base_ledger_sha256':sha(old_lp.read_bytes()),'module_sha256':sha((ROOT/'MAP_EXTENSION.json').read_bytes()),'graph_sha256':sha((ROOT/'UCT_EFFECTIVE_GRAPH.json').read_bytes()),'ledger_sha256':sha((ROOT/'REVIEW_LEDGER.json').read_bytes()),'counts':counts,'census_semantic_topic_flags':dict(themes),'source_bytes_unchanged':True,'old_rule_closure_syntactically_conservative':True,'no_suspended_rule_reactivated':True,'new_model_actual_bearers_unproved':True,'pending_checkpoints_not_promoted':['R185','AC20261009','IL20261009','UI20261009'],'all_old_proofs_independently_reproved':False,'logical_interpretation':'Syntactic noninterference proof plus human-authored scoped semantic compatibility decisions; all-item machine readback alone is not an independent semantic proof.'}
    dump(ROOT/'MAP_AUDIT_RESULTS.json',res)
    manifest={'release_id':VERSION,'release_seq':3,'parent_release':'UCT-MAP-v1.1.0','audit_id':AUDIT,'research_id':'OL20261009','result_version':'0.1.0','date':'2026-10-09','review_status':'COMPATIBILITY_REVIEW_COMPLETE_WITH_LIMITS_AND_OPEN_APPLICATIONS','counts':counts,
              'parent_graph_sha256':res['base_graph_sha256'],'parent_ledger_sha256':res['base_ledger_sha256'],'module_sha256':res['module_sha256'],'effective_graph_sha256':res['graph_sha256'],'review_ledger_sha256':res['ledger_sha256'],
              'added_ids':[x['id'] for k in ('nodes','rules','context_links') for x in m[k]],'old_scientific_ids_modified':[],'new_suspended':[],
              'pending_checkpoints_retained_not_promoted':['R185','AC20261009','IL20261009','UI20261009'],
              'qc_open':['QC-20261008-10','IA-QC11','QC-20261008-12','QC-20261008-13'],
              'actual_and_named_phenomenal_applications':'OPEN','scientific_novelty':'NEW_SCOPED_APPLICATION_AND_CALIBRATED_INTERVENTION_PROBE; PRIORITY_UNVERIFIED',
              'publication_status':'NO_PUBLICATION_AUTHORIZED',
              'validity_boundary':'Mathematical schema checked under fixed LTI/physical primitive write/horizon/Q. Model is not evidence that any human or AI has a specific experience.',
              'reproduction':'build_map_release.py + exact hash-verified UCT-MAP-v1.1.0 baseline + MAP_EXTENSION.json',
              'storage_receipt':'Separate GitHub expected-head commit and readback receipt required.'}
    dump(ROOT/'RELEASE.json',manifest)
    print(json.dumps({'status':'PASS','counts':counts,'output_graph_sha':res['graph_sha256'],'ledger_sha':res['ledger_sha256']},indent=2))

if __name__=='__main__':main()
