#!/usr/bin/env python3
"""Update only current research navigation/governance; retain exact history."""
from pathlib import Path
import json
import hashlib

BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'uct/research/uct-agent-consciousness-workspace'
REC='records/PUB20261009_Publication_Coverage'
PROBE='records/ONLINE_AC_20261009_Dynamic_Calibration'
VERSION='UCT-PUB-v1.0.0'
HISTORY=ROOT/REC/'history'

def load(name): return json.loads((ROOT/name).read_text())
def save(name,d): (ROOT/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')

def main():
    entry=load('PUBLICATION_COVERAGE.json')
    assert entry['coverage_version']==VERSION
    baseline=json.loads((HISTORY/'BASELINE_MANIFEST.json').read_text())
    common={'entry':'PUBLICATION_COVERAGE.json','version':VERSION,
            'update':REC+'/COVERAGE_UPDATE.json',
            'report':REC+'/PUBLICATION_COVERAGE_REPORT_ZH.md',
            'nondeductive':True}
    d=load('CURRENT_STATE.json')
    d['schema']='uct-current-state/1.4'
    d['publication_coverage']=common
    d['latest_activity']={'id':'PUB20261009','kind':'publication_census_residual_reassessment_and_pending_research',
                         'work_log':REC+'/WORK_LOG.md','handoff':REC+'/HANDOFF_ZH.md'}
    d['latest_research']['current_manuscript_decision']='HOLD_STANDALONE_PRESERVE_TECHNICAL_SUPPLEMENT_CANDIDATE'
    d['latest_research']['decision_record']=REC+'/RESIDUAL_RESEARCH_ASSESSMENT.md'
    d['publication_status']='CLAIM_LEVEL_CURRENT_COVERAGE_IN_PUBLICATION_COVERAGE_JSON'
    d['current_guide']='RESEARCH_MASTER_GUIDE.md v2.3'
    d['review_status_scope']='Completed scientific release UCT-MAP-v1.1.2 only; latest online result remains PENDING_MAP.'
    d['pending_note']='AC, IL and ONLINE-AC remain separate disabled pending modules; working-paper completion is not scientific-map promotion.'
    d['latest_pending_research']={'id':'ONLINE-AC-PROBE-20261009','result_version':'0.2.0',
                'status':'PENDING_MAP','source':PROBE+'/RESEARCH_CHECKPOINT.md',
                'enabled_as_established_premises':False,
                'paper_version':'ONLINE-AC-PAPER-v0.1.0','paper':PROBE+'/PAPER.md',
                'paper_status':'COMPLETE_SCOPED_WORKING_MANUSCRIPT_NOT_FORMALLY_PUBLISHED'}
    d['pending_checkpoints_not_promoted']=['AC20261009','IL20261009','ONLINE-AC-PROBE-20261009']
    save('CURRENT_STATE.json',d)

    d=load('UCT_FORMAL_GRAPH_MODULES.json')
    d['publication_coverage']=common
    d['publication_coverage_changes_scientific_graph']=False
    d['full_review_status_scope']='The completed compatibility review applies to UCT-MAP-v1.1.2 only, not to pending checkpoints.'
    d['pending_checkpoints']=[x for x in d['pending_checkpoints'] if x['id']!='ONLINE-AC-PROBE-20261009']
    module=ROOT/PROBE/'MAP_EXTENSION_PENDING.json'
    d['pending_checkpoints'].append({'id':'ONLINE-AC-PROBE-20261009',
         'result_version':'0.2.0','path':PROBE+'/MAP_EXTENSION_PENDING.json',
         'sha256':hashlib.sha256(module.read_bytes()).hexdigest(),
         'status':'PENDING_MAP','audit_status':'LOCAL_REVIEW_ONLY_FULL_MAP_INTEGRATION_NOT_COMPLETED',
         'enabled_as_established_premises':False,
         'handoff':PROBE+'/HANDOFF_ZH.md',
         'instruction':'Specific online calibration result; static AC is independently pending. Read the exact contract, proof and independent review before any semantic integration. Do not treat this entry as completed v1.1.3.'})
    save('UCT_FORMAL_GRAPH_MODULES.json',d)

    d=load('RESEARCH_REGISTRY.json')
    d['publication_coverage']=common
    d['registry_scope']='Recent navigation register; complete fixed-source inventories are in the current publication coverage ledger.'
    d['parent_registry']=REC+'/history/RESEARCH_REGISTRY.json'
    for x in d['results']:
        if 'historical_publication_label' not in x:
            x['historical_publication_label']=x.get('publication')
        x['publication']='SEE_CURRENT_CLAIM_LEVEL_COVERAGE'
        x['publication_coverage_version']=VERSION
        if x['research_id']=='TH20261009':
            x['publication_subclaims']={
               'TH_v0.1':'Published in RT/TH v1.0.0 body and formal module, DOI10.5281/zenodo.23251651; exact contract differences are recorded.',
               'RB_v0.2':'Cited by RT/TH, not deposited or republished there; inherited specializations and residual budget applications are assessed separately.'}
        if x['research_id']=='R188-CER-20261009':
            x['manuscript_decision']='HOLD_STANDALONE_TECHNICAL_SUPPLEMENT_CANDIDATE'
            x['decision_record']=REC+'/RESIDUAL_RESEARCH_ASSESSMENT.md'
    d['pending_checkpoints']=[x for x in d['pending_checkpoints'] if x['research_id']!='ONLINE-AC-PROBE-20261009']
    d['pending_checkpoints'].append({'research_id':'ONLINE-AC-PROBE-20261009',
         'source':PROBE+'/MAP_EXTENSION_PENDING.json','status':'PENDING_MAP',
         'enabled_as_established_premises':False,'publication_coverage_version':VERSION})
    save('RESEARCH_REGISTRY.json',d)

    d=load('RESEARCH_SESSION_LOG_INDEX.json')
    d['latest_activity']='PUB20261009'
    d['latest_work_log']=REC+'/WORK_LOG.md'
    d['latest_handoff']=REC+'/HANDOFF_ZH.md'
    d['latest_pending_research']='ONLINE-AC-PROBE-20261009'
    d['guide']='RESEARCH_MASTER_GUIDE.md v2.3 sections 0.3–0.6 and 8A'
    d['publication_coverage']=common
    d['pending_checkpoints']=['AC20261009','IL20261009','ONLINE-AC-PROBE-20261009']
    d['previous_index']=REC+'/history/RESEARCH_SESSION_LOG_INDEX.json'
    save('RESEARCH_SESSION_LOG_INDEX.json',d)

    d=load('FORMAL_MAP_REVIEW_POLICY.json')
    d['publication_coverage']['current_version']=VERSION
    d['publication_coverage']['current_update']=REC+'/COVERAGE_UPDATE.json'
    d['latest_governance_activity']='PUB20261009'
    d['latest_pending_research']='ONLINE-AC-PROBE-20261009'
    d['navigation_update']='Publication overlay synchronized; completed science graph remains v1.1.2. New online calibration is a pending research checkpoint.'
    for name in ['PUBLICATION_COVERAGE.json','CURRENT_STATE.json','RESEARCH_REGISTRY.json','RESEARCH_SESSION_LOG_INDEX.json']:
        if name not in d['governed_files']:d['governed_files'].append(name)
    save('FORMAL_MAP_REVIEW_POLICY.json',d)

    header=f'''# Current research decision — {VERSION} / PUB20261009

**Read [RESEARCH_MASTER_GUIDE.md](RESEARCH_MASTER_GUIDE.md) v2.3, [CURRENT_STATE.json](CURRENT_STATE.json), and [PUBLICATION_COVERAGE.json](PUBLICATION_COVERAGE.json) first.** The paper purpose is original, inspectable knowledge that future AI and researchers can cite and reuse, serving the UCT main line. Each log/map update must synchronize the same coverage version.

The verified publication census contains **28 research works, 39 research DOI deposits (38 work/version-label pairs), plus one separately counted editorial supplement**. Published body, formal supplement disclosure, cited working source, proof validity and originality are distinct. MGTD disclosed the v1.0.0 map; RT/TH published early TH and the route results. Old registry `NOT_PUBLISHED` labels are historical and cannot supersede current claim coverage.

**Current R188 decision: HOLD standalone; preserve the exact technical supplement candidate.** This reassesses the broad working manuscript's readiness after deducting newly verified published coverage. Its source-only weighted finite-error result and matched benchmark remain useful. The frozen manuscript, code and graph are unchanged. Read [the residual assessment]({REC}/RESIDUAL_RESEARCH_ASSESSMENT.md) and [the current report]({REC}/PUBLICATION_COVERAGE_REPORT_ZH.md).

Actual continuation produced [ONLINE-AC-PROBE-20261009]({PROBE}/RESEARCH_CHECKPOINT.md): an exact five-port two-probe sustainable controller, matched three-probe complete-identification baseline, and three-port7/8 benchmark, with proofs and independent checks. The focused [working paper]({PROBE}/PAPER.md), ONLINE-AC-PAPER-v0.1.0, is complete and not formally published. It is **PENDING_MAP**, like AC and IL; it is not an enabled scientific premise or a completed v1.1.3 release.

The completed science remains **UCT-MAP-v1.1.2**, 913 nodes, 424 active rules, 261 contexts and 10 suspended rules: 1,608 review records. Coverage metadata creates no new science version. QC10, IA-QC11, QC12, QC13 and actual/named-experience obligations remain open.

Latest [work log]({REC}/WORK_LOG.md), [Chinese handoff]({REC}/HANDOFF_ZH.md), [coverage update]({REC}/COVERAGE_UPDATE.json) and [save receipt](persistence/{VERSION}_RECEIPT.json). Keep the inventory's declared unknown scope; neither 71 unresolved map-body comparisons nor the 279 IDs absent from two formal attachments are counts of unpublished discoveries.

---

## Preserved earlier navigation (historical; current decisions above take precedence)

'''
    for name in ['HANDOFF.md','MASTER_INDEX.md','MEMORY.md','AGENTS.md']:
        old=(HISTORY/name).read_text()
        (ROOT/name).write_text(header+old)

    for name in ['UCT_FORMAL_MAP.md','UCT_FORMAL_AUDIT.md']:
        old=(HISTORY/name).read_text()
        (ROOT/name).write_text(old+f'''
## Publication coverage and latest pending research

Current non-deductive coverage: [{VERSION}](PUBLICATION_COVERAGE.json). [PUB20261009]({REC}/COVERAGE_UPDATE.json) inventories all 1,608 existing review IDs, reconciles formal published attachments, and assesses residual knowledge separately from validity. The frozen R188 working paper now has a [HOLD standalone readiness decision]({REC}/RESIDUAL_RESEARCH_ASSESSMENT.md).

[ONLINE-AC-PROBE-20261009]({PROBE}/RESEARCH_CHECKPOINT.md) is a locally reviewed pending checkpoint; AC/IL also remain pending. No new whole-map semantic release is claimed by this coverage update. Existing science bytes and all open obligations are unchanged.
''')
    old=(HISTORY/'VERSIONING_POLICY.md').read_text().replace('canonical guide v2.2 §§0,8A','canonical guide v2.3 §§0,8A')
    (ROOT/'VERSIONING_POLICY.md').write_text(old+f'''
## Publication coverage versions

[{VERSION}](PUBLICATION_COVERAGE.json) is the first immutable publication coverage release. It is independent of UCT-MAP-v1.1.2. Its ledger and shards bind exact work/deposit identities, formal disclosures, body comparison scope, residual assessments and source evidence. Advance the coverage version when claims/publication evidence/assessments change; retain the preceding snapshot. Metadata-only coverage, guide or citation changes do not increment the scientific-map version.

Every current log, handoff, registry and map entry must cite the same coverage version and a change record or an explicit checked no-change reason. Working research, formal publication, reserved DOI and preservation are different states. A same-label different DOI deposit remains a separate publication record of the same work. A new pending checkpoint is not a completed map release.
''')
    old=(HISTORY/'CHANGELOG.md').read_text()
    (ROOT/'CHANGELOG.md').write_text(f'''# {VERSION} — 2026-10-09 — publication/reuse coverage sequence 1

PUB20261009 fulfills the author's inventory → published coverage → net-increment assessment → breakthrough or manuscript → reassessment cycle. Guide v2.3 and machine policy v2.4 require synchronized publication coverage on every log/map update. Census: 28 research works, 39 research DOI deposits, plus one editorial DOI; 1,608 current review objects receive separate disclosure/role metadata. MGTD's old graph and RT/TH's early handoff disclosure narrow the residual. R188's earlier standalone-readiness judgment is superseded by HOLD, retaining its technical contribution and exact frozen files.

ONLINE-AC-PROBE-20261009 resultv0.2.0 is a new pending research checkpoint with a verified five-port two-probe closed controller and matched three-probe identification baseline; its focused working manuscript is complete, not formally published; it remains outside the completed science graph. This update is not v1.1.3 and does not repeat the earlier full-map proof audit. Sources, unknown scope, negative routes, score-label correction, receipts and exact pre-edit navigation are retained in [{REC}]({REC}/WORK_LOG.md).

---

'''+old)
    print('Current publication, guide, log and map pointers synchronized; frozen science untouched.')

if __name__=='__main__':main()
