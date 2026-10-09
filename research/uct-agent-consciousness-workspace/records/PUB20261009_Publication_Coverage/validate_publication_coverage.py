#!/usr/bin/env python3
"""Check publication/research artifact consistency, never scientific truth.

This meaningful release check validates exact corpus counts, all stable IDs,
source-member hashes, disabled pending claims, immutable scientific baselines,
and final proof/manuscript/receipt correspondence. It does not rerun research
searches, assert global originality, or substitute for a full-map semantic audit.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
import argparse
import hashlib
import json
import tarfile

CHECKS=[]
def check(name, condition, evidence=None):
    if not condition: raise AssertionError(name)
    CHECKS.append({'check':name,'status':'PASS','evidence':evidence})
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parent.parent/'uct/research/uct-agent-consciousness-workspace')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();root=args.root.resolve()
    version='UCT-PUB-v1.0.0'
    out=root/'publication'/version
    rec=root/'records/PUB20261009_Publication_Coverage'
    probe=root/'records/ONLINE_AC_20261009_Dynamic_Calibration'
    entry=read(root/'PUBLICATION_COVERAGE.json')
    ledger=read(out/'COVERAGE_LEDGER.json')
    check('current coverage version and nonscientific layer',entry['coverage_version']==ledger['coverage_version']==version and entry['nondeductive'])
    def verify_anchor(a):
        p=root/a['path']
        return p.is_file() and p.stat().st_size==a['bytes'] and sha(p)==a['sha256']
    check('entry binds exact ledger bytes',verify_anchor(entry['ledger']))
    check('all ledger document and item-shard hashes match',all(verify_anchor(a) for a in list(ledger['documents'].values())+ledger['item_shards']),{'documents':len(ledger['documents']),'shards':len(ledger['item_shards'])})
    idx=read(out/'CLAIM_ID_INDEX.json')['index']
    items=[]
    for shard in ledger['item_shards']:
        d=read(root/shard['path']);items+=d['items']
        check('shard '+Path(shard['path']).name,d['coverage_version']==version and len(d['items'])==shard['items'])
    ids=[i['item_id'] for i in items]
    check('all1608 review IDs unique and indexed',len(ids)==len(set(ids))==len(idx)==1608 and set(ids)==set(idx))
    check('index status and item status agree',all(idx[i['item_id']]['coverage_status']==i['coverage_status'] for i in items))
    counts=dict(Counter(i['coverage_status'] for i in items))
    check('exact publication-role counts',counts==ledger['current_item_coverage_counts']=={'covered_exact':382,'covered_partial':2,'inherited':14,'unverified':71,'not_applicable':1139},counts)
    recn=read(out/'COVERAGE_RECONCILIATION.json')
    check('12 semantic reconciliations preserve71 unknowns',len(recn['explicit_semantic_overrides'])==12 and len(recn['remaining_unverified_ids'])==71 and set(recn['remaining_unverified_ids'])=={i['item_id'] for i in items if i['coverage_status']=='unverified'})
    check('unknown and publication do not imply originality or truth',ledger['unknown_means_unpublished'] is False and ledger['unpublished_means_original'] is False and ledger['publication_means_validated'] is False)

    works=read(out/'PUBLISHED_WORKS_AND_VERSIONS.json')['works']
    research=[w for w in works if w['work_id']!='EDITORIAL20260919']
    rv=[v for w in research for v in w['versions']]
    ev=[v for w in works if w['work_id']=='EDITORIAL20260919' for v in w['versions']]
    check('28research works and39 distinct research DOI records',len(research)==28 and len(rv)==len({v['doi'] for v in rv})==39)
    check('38work/version pairs; duplicateUCTI v1.1 retained',len({(v['work_id'],v['version_label']) for v in rv})==38 and len([v for v in rv if v['work_id']=='TA-TR-2026-20' and v['version_label'].removeprefix('v')=='1.1'])==2)
    check('editorial separate and no reserved-only counted records',len(ev)==1 and len({v['doi'] for v in rv+ev})==40 and all(v['reserved_only'] is False for v in rv+ev))

    sm=read(out/'SOURCE_CAPSULE_MANIFEST.json')
    check('source capsule exact hash',verify_anchor(sm['capsule']))
    members=sm['members']
    with tarfile.open(root/sm['capsule']['path'],'r:xz') as tar:
        names=tar.getnames()
        check('225 unique safe source members',len(names)==len(set(names))==len(members)==225 and all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in names))
        lookup={m['member']:m for m in members}
        check('capsule member manifest exact coverage',set(names)==set(lookup))
        for name in names:
            content=tar.extractfile(name).read();m=lookup[name]
            if len(content)!=m['bytes'] or hashlib.sha256(content).hexdigest()!=m['sha256']:
                raise AssertionError('capsule member bytes differ: '+name)
        check('all225 source member hashes match',True)
        old=json.loads(tar.extractfile('publication_audit_work/map_result_inventory.json').read())
        check('current ID set equals frozen independent inventory',set(ids)=={i['item_id'] for i in old['map_items']})
        check('private transfer request excluded','publication_audit_work/early_master_download_input.json' not in names)

    history=read(rec/'history/BASELINE_MANIFEST.json')
    check('14 exact pre-edit files retained',len(history['files'])==14 and all((rec/'history'/x['path']).stat().st_size==x['bytes'] and sha(rec/'history'/x['path'])==x['sha256'] for x in history['files']))
    for name in ['HANDOFF.md','MASTER_INDEX.md','MEMORY.md','AGENTS.md']:
        check('historical suffix retained: '+name,(root/name).read_bytes().endswith((rec/'history'/name).read_bytes()) and version in (root/name).read_text().split('Preserved earlier navigation')[0])
    for name in ['CURRENT_STATE.json','UCT_FORMAL_GRAPH_MODULES.json','RESEARCH_REGISTRY.json','RESEARCH_SESSION_LOG_INDEX.json']:
        check('current metadata version: '+name,read(root/name)['publication_coverage']['version']==version)
    check('guide purpose and fixed cycle present',all(s in (root/'RESEARCH_MASTER_GUIDE.md').read_text() for s in ['版本 2.3','未来 AI','0.3','0.4','0.5','0.6','每次写日志或更新地图']))
    policy=read(root/'FORMAL_MAP_REVIEW_POLICY.json')
    check('machine policy current coverage',policy['publication_coverage']['current_version']==version)

    frozen=root/'versions/UCT-MAP-v1.1.2'
    check('completed graph unchanged',sha(frozen/'UCT_EFFECTIVE_GRAPH.json')=='0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612')
    check('completed semantic ledger unchanged',sha(frozen/'REVIEW_LEDGER.json')=='0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687')
    g=read(frozen/'UCT_EFFECTIVE_GRAPH.json')
    check('completed graph counts unchanged',[len(g[k]) for k in ['nodes','rules','context_links','suspended_historical_rule_ids']]==[913,424,261,10])
    state=read(root/'CURRENT_STATE.json');module=read(probe/'MAP_EXTENSION_PENDING.json')
    check('new scientific module remains disabled',state['release_id']=='UCT-MAP-v1.1.2' and module['status']=='PENDING_MAP' and module['enabled_as_established_premises'] is False and module['full_map_semantic_rechecks_completed_this_increment']==0)
    pending=[x for x in read(root/'UCT_FORMAL_GRAPH_MODULES.json')['pending_checkpoints'] if x['id']=='ONLINE-AC-PROBE-20261009']
    check('unique pending module pointer/hash/version',len(pending)==1 and pending[0]['sha256']==sha(probe/'MAP_EXTENSION_PENDING.json') and pending[0]['result_version']=='0.2.0' and pending[0]['enabled_as_established_premises'] is False)
    claims=read(probe/'CLAIM_REUSE_LEDGER.json')['claims']
    check('12 candidate records without ID collisions or enabled premises',len(claims)==len({c['claim_id'] for c in claims})==12 and not ({c['claim_id'] for c in claims}&set(ids)) and all(c['enabled_as_established_premise'] is False for c in claims))
    check('old research note bytes preserved',sha(probe/'versions/ONLINE-AC-RESULT-v0.1.0/RESEARCH_CHECKPOINT.md')=='e4cc302bae8b722eb109605dfdebafd2f9d13902e42bb5841ccab04880c16b5c')
    check('final scientific manuscript is reviewed exact version',sha(probe/'PAPER.md')=='713c99e59d2abf6278a2f036dbb49514fafd89ee7f781be8bf5bc91bf1827b65' and '<!-- CANONICAL_TABLES -->' not in (probe/'PAPER.md').read_text())
    n5=probe/'next_probe_n5';c=read(n5/'CERTIFICATE_INDEPENDENT_VALIDATION.json');t=read(n5/'CANONICAL_TRANSPORT_INDEPENDENT_VALIDATION.json')
    check('independent closed certificate bindings and counts',c['certificate_sha256']==sha(n5/'CLOSED_CONTROLLER.json') and c['independent_verifier_sha256']==sha(n5/'verify_closed_controller_independent.py') and c['counts']['controller_states']==240 and c['counts']['persistent_plant_cases']==126720 and c['discrepancies']==[])
    tc=t['transport_family_check']
    check('independent two-template transport bindings and counts',t['source_certificate_sha256']==sha(n5/'CLOSED_CONTROLLER.json') and t['source_canonical_templates_sha256']==sha(n5/'CANONICAL_TEMPLATES.json') and t['independent_script_sha256']==sha(n5/'canonical_transport_independent.py') and tc['family_size']==480 and tc['counts']['old_drift_worlds']==9240 and tc['counts']['terminal_leaves']==7680 and tc['reachable_from_identity']['count']==260 and t['discrepancies']==[])
    check('final independent review exact version',sha(n5/'ONLINE_AC_N5_INDEPENDENT_REVIEW.md')=='66c70cb94e4041cd3871f91aef25274a57c7192ca457a6a6bf516d9b991e4e3e' and sha(probe/'PAPER.md') in (n5/'ONLINE_AC_N5_INDEPENDENT_REVIEW.md').read_text())
    qa=read(probe/'PDF_QA_RECEIPT.json')
    check('PDF layout receipt binds current11-page output',qa['status']=='PASS_RENDER_AND_CONTENT_QA' and qa['pages']==11 and qa['pdf_sha256']==sha(probe/'Correct_Control_Without_Complete_Recalibration_v0.1.0.pdf') and qa['manuscript_sha256']==sha(probe/'PAPER.md'))
    rm=read(probe/'RESEARCH_MANIFEST.json')
    check('all research manifest members hash-match',all((probe/a['path']).is_file() and (probe/a['path']).stat().st_size==a['bytes'] and sha(probe/a['path'])==a['sha256'] for a in rm['members']),len(rm['members']))
    decision=read(out/'MANUSCRIPT_DECISION.json')
    check('distinct R188 HOLD and completed unpublished new paper',decision['r188']=='HOLD_STANDALONE_PRESERVE_TECHNICAL_SUPPLEMENT_CANDIDATE' and decision['new_paper']['decision']=='COMPLETE_SCOPED_WORKING_MANUSCRIPT' and decision['new_paper']['new_publication_count']==0 and decision['new_paper']['map_status']=='PENDING_MAP')
    update=read(rec/'COVERAGE_UPDATE.json')
    check('log/coverage/map update synchronized',update['new_coverage_version']==version and update['newly_published_claim_ids']==[] and update['map_semantics_changed'] is False and update['whole_map_audit_if_required']['enabled_as_established_premises'] is False and version in (rec/'WORK_LOG.md').read_text() and version in (rec/'HANDOFF_ZH.md').read_text())
    result={'validation_id':'PUB20261009-FINAL-CONSISTENCY','status':'PASS',
        'coverage_version':version,'checks_passed':len(CHECKS),'checks':CHECKS,
        'scientific_map':'UCT-MAP-v1.1.2','new_scientific_module':'PENDING_MAP',
        'scope':'Exact artifact/corpus/ID/hash and declared-status consistency. Not a new scientific proof, literature-priority clearance, empirical validation, or full-map semantic integration.',
        'validator_sha256':sha(Path(__file__))}
    output=args.output or rec/'VALIDATION_REPORT.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='checks'},ensure_ascii=False))

if __name__=='__main__': main()
