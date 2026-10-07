"""Build a review layer from the exact R153 graph. Source editions are immutable."""
from pathlib import Path
from collections import Counter
import json, hashlib, argparse, copy
from proof_entries import ENTRIES

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
REL=HERE.relative_to(ROOT).as_posix()
PARENT='39436f898f5f193fcb34d14838a1d53fc96bf1e5'
BASE_HASH='84b005b6ed7f25fc49da67e19e8e4e60e4a1b11263992fe7fb268681682f5b43'
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);args=ap.parse_args()
data=args.baseline.read_bytes();assert hashlib.sha256(data).hexdigest()==BASE_HASH
g=json.loads(data);assert g['revision']=='R153-v1.0'
ns={n['id']:n for n in g['nodes']};rs={r['id']:r for r in g['rules']}
remaining={r['id'] for r in g['rules'] if r['formal_contract_R153']['review_status'].startswith('INHERITED')}
assert set(ENTRIES)==remaining and len(remaining)==128
amendments=[]

def amend(node,field,value,reason):
    old=ns[node].get(field)
    if old==value:return
    amendments.append(dict(node=node,field=field,before=old,after=value,reason=reason))
    ns[node][field]=value

amend('A:TOY_EXP_WHOLE','statement',
      'For every pair of TOY_MATH settings separated by the whole transition image cardinality (2 versus 4, 2 versus 8, or 4 versus 8), ACTUAL_COMPLETE_TOY and C1-OI imply distinct complete experiential types for the corresponding actual whole tokens. This image-size route does not separate the two one-link settings (1,0) and (0,1).',
      'a27 compressed the pair restriction already present in the R153 whole-structure invariant; restore it in the experiential conclusion.')
amend('TA17:SET_LIMITS','statement',
      'Individual-only categorical labels cannot encode arbitrary successor sets. For a nonnegative membership relation across unique-continuation and fission scenarios, assume full unique continuation gives q(A,B)=1, adding an equally full co-successor preserves that value, and equally full copies are symmetric. Then two full successors have total membership at least 2, incompatible with unit-sum normalization. Equal singleton inclusion marginals need not identify mu; equal singleton inheritance need not identify Gamma. Duplication violates conserved-mass and universal supermodularity; secret sharing violates universal submodularity.',
      'Restore the explicit unique-full-continuation calibration in published TA17 Proposition 6; the prior map summary omitted it.')
amend('TA17:SET_LIMITS','scope',
      'Existence counterexamples under FUNCTIONAL_CONTRACT. The normalization clause compares singleton/full-continuation and two-full-successor scenarios under the same calibrated membership rule; includes nonnegativity, full-unique value 1, co-successor preservation and symmetry. It is not a no-go for categorical probabilities over mutually exclusive outcomes.',
      'Make the cross-scenario calibration domain explicit.')
amend('TA17:SET_LIMITS','domain',ns['TA17:SET_LIMITS']['scope'],'Keep domain and scope synchronized.')
amend('TA16:CAUSAL_LIMITS','statement',
      'For every nonnegative n-by-n W with n>=2, the positive-edge graph is strongly connected iff for every nontrivial bipartition pi and every vertex i there exists an integer k with 1<=k<=2(n-1) and (W^k-W_pi^k)_[i,i]>0, where W_pi deletes all crossing edges. Strong connectivity alone does not determine retained information; incompatible modes cannot jointly witness different maxima; recoding preserves the physical question when interventions are transported; every finite Boolean F has an exact wrapper Ftilde=EFD on valid codewords with DE=id.',
      'Expand the compressed all-cut/every-vertex/existential-walk quantifiers from TA16 Appendix G.1; theorem unchanged.')
amend('R137:CONTROL_MODEL','scope',
      'S,Z,O,A are finite nonempty sets, alpha:S->Z is onto and visible; m=|A|>=1. Concrete state is Markov-sufficient, with partial menus A(s), joint successor/output kernels and paired pointed state/clock. The memoryless decoder w(a|z,u) uses only visible z and request u with fresh conditional randomness. U(z) is nonempty; abstract history policies are legally specified on all projected histories, including nominally zero-probability ones, and cannot read decoder coins/concrete action labels. Every represented start is covered; physical adequacy is independent. This is one specified decoder class, not all causal interfaces.',
      'Explicitly retain the source nonempty action alphabet needed for the (m-1)-dimensional simplex/Helly bound.')

# Statements on inference edges are synchronized; historical R153 contracts remain provenance.
for r in g['rules']:
    if any(a.get('node')==r['conclusion'] and a['field']=='statement' for a in amendments):
        amendments.append(dict(rule=r['id'],field='statement',before=r.get('statement'),after=ns[r['conclusion']]['statement'],reason='Synchronize canonical rule conclusion with repaired node.'))
        r['statement']=ns[r['conclusion']]['statement']

cards=[]
for r in g['rules']:
    old=r['formal_contract_R153']
    contract={k:copy.deepcopy(v) for k,v in old.items() if k not in ['proof_location','review_status']}
    if r['id'] in ENTRIES:
        entry=ENTRIES[r['id']]
        contract.update(proof_location=f'{REL}/RULE_REVIEW.md#{r["id"].lower()}',
                        review_status=entry['disposition'],argument_file=f'{REL}/RULE_REVIEW.json',argument_id=r['id'])
        cards.append(dict(id=r['id'],all_of=r['all_of'],conclusion=r['conclusion'],
                          conclusion_statement=ns[r['conclusion']]['statement'],
                          premises=[dict(id=x,statement=ns[x]['statement'],scope=ns[x]['scope']) for x in r['all_of']],
                          source=r.get('source'),source_edition=old.get('source_edition'),
                          shared_bindings=old['bindings_required'],root_premise_routes=old['root_premise_routes'],
                          **entry))
    else:
        contract.update(proof_location=old['proof_location'],review_status=old['review_status'],
                        carried_from='R153 expanded argument, not reclassified as a new R154 proof')
    r['formal_contract_R154']=contract

for n in g['nodes']:
    changed=[a for a in amendments if a.get('node')==n['id']]
    if changed:
        n['formal_contract_R154']=dict(statement=n['statement'],scope=n['scope'],
                                      amendments=f'{REL}/AMENDMENTS.json',
                                      prior_contract_is_historical=True,machine_proof=False)

g['revision']='R154-v1.0'
g['formalization_R154']=dict(parent_commit=PARENT,parent_graph_sha256=BASE_HASH,
    current_rule_layer='formal_contract_R154',
    concept_resolution='Canonical node statement/scope plus R153 typed contract; R154 amended fields override historical R153 copies. No blanket physical-grounding certification.',
    new_argument_cards=128,carried_expanded_reviews=60,all_registered_rules_have_argument_review=True,
    open_conditional_representation_schemas=[k for k,v in ENTRIES.items() if v['disposition']=='CONDITIONAL_REPRESENTATION_SCHEMA_OPEN'],
    proof_assistant_certified=False,global_semantic_consistency_certified=False,
    records=REL,joint_audit=f'{REL}/JOINT_AUDIT.md')

gaps=json.loads((ROOT/'records/R153_Complete_Formal_Map_20261007/GAP_LEDGER.json').read_text())
for gap in gaps:
    if gap['id']=='F153-15':
        gap['R154_progress']='The 128 inherited rule sketches now have individual argument/boundary cards, and the named joint-premise bundles were checked. Arbitrary global semantic consistency and proof-assistant certification remain unproved; this family stays OPEN.'
    if gap['id']=='F153-12':
        gap['R154_progress']='Nine rival mappings explicitly retained as CONDITIONAL_REPRESENTATION_SCHEMA_OPEN with per-theory imported commitments and residual obligations in RULE_REVIEW.'
gaps.extend([
    dict(id='F154-01',state='CORRECTED',title='Whole toy experiential conclusion omitted pair restriction',direct_nodes=['A:TOY_EXP_WHOLE'],resolution='Conclusion now restricted to pairs separated by transition-image size; one-link pair explicitly excluded from this argument.'),
    dict(id='F154-02',state='CORRECTED',title='Unique-full-continuation calibration omitted from normalization summary',direct_nodes=['TA17:SET_LIMITS'],resolution='Restored q(A,B)=1 in unique-full scenario and shared cross-scenario rule, as in the published proof.'),
    dict(id='F154-03',state='CLARIFIED',title='All-cut return quantifiers compressed',direct_nodes=['TA16:CAUSAL_LIMITS'],resolution='Every nontrivial cut, every vertex, exists k<=2(n-1), nonnegative W and n>=2 now explicit.'),
    dict(id='F154-04',state='CLARIFIED',title='Nonempty action alphabet for obstruction theorem',direct_nodes=['R137:CONTROL_MODEL'],resolution='Source S,Z,O,A nonempty and m>=1 now explicit in current scope.'),
])

def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
dump(ROOT/'UCT_FORMAL_GRAPH.json',g);dump(HERE/'RULE_REVIEW.json',cards)
dump(HERE/'AMENDMENTS.json',amendments);dump(HERE/'GAP_LEDGER.json',gaps)
lines=['# R154 — Individual argument review of the 128 formerly inherited rules','',
       'All listed premises are conjunctive. Alternative rules remain separate. Source-level empirical and experiential assumptions are not discharged by these manual mathematical arguments. The other 60 rules retain their expanded R153 reviews.','']
for c in cards:
    lines += [f'## {c["id"]}', '',f'**Disposition:** {c["disposition"]}. Machine proof: no.', '',
              f'**Source:** {c["source"]}; edition snapshot: `{c["source_edition"]}`.','',
              '**All simultaneous premises:**','']
    for p in c['premises']:lines += [f'- `{p["id"]}`: {p["statement"]} Scope: {p["scope"]}']
    lines += ['',f'**Conclusion — {c["conclusion"]}:** {c["conclusion_statement"]}','',
              '**Argument:** '+c['argument'],'','**Boundary / non-inference:** '+c['indispensable_boundary'],'',
              '**Shared bindings:** '+ '; '.join(c['shared_bindings'])+'.','']
(HERE/'RULE_REVIEW.md').write_text('\n'.join(lines)+'\n')
summary=dict(revision=g['revision'],parent_commit=PARENT,node_count=len(g['nodes']),rule_count=len(g['rules']),
             new_cards=len(cards),carried_expanded_reviews=60,dispositions=dict(Counter(c['disposition'] for c in cards)),
             amendments=len(amendments),changed_node_ids=sorted({a['node'] for a in amendments if 'node' in a}),
             open_families=sum(x['state']=='OPEN' for x in gaps),published_sources_modified=False)
dump(HERE/'BUILD_SUMMARY.json',summary)
print(json.dumps(summary,ensure_ascii=False))
