"""Build a source-preserving, exhaustive contract ledger; not a proof checker."""
from pathlib import Path
import copy, hashlib, json, re
from collections import Counter, defaultdict
from functools import lru_cache

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REL = HERE.relative_to(ROOT).as_posix()
def dump(p,x):
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
BASE=HERE/'baseline-graph.json'
if not BASE.exists(): BASE.write_bytes((ROOT/'UCT_FORMAL_GRAPH.json').read_bytes())
old=json.loads(BASE.read_text()); g=copy.deepcopy(old)
N={n['id']:n for n in g['nodes']}; R={r['id']:r for r in g['rules']}
definitions=json.loads((HERE/'definition_repairs.json').read_text())
# Restore the exact R126 initial observation, found by backreading both notes.
definitions['R126:MODEL']=definitions['R126:MODEL'].replace(
    'starts from the output partition (or an explicitly fixed finer initial partition P0)',
    'starts from ker(o), o(s)=(p(s),r(s)), or an explicitly declared finer initial partition P0')
assert set(definitions)=={n['id'] for n in old['nodes'] if not n.get('statement')}
changes=[]
def amend(node,key,value,reason):
    prior=N[node].get(key)
    if prior!=value:
        changes.append({'node':node,'field':key,'before':prior,'after':value,'reason':reason})
        N[node][key]=value
for id,statement in definitions.items():
    amend(id,'statement',statement,'R153 explicit definition/premise restoration; see source and FORMAL_FOUNDATION.')
amend('R126:P4','statement',
      'Put o(s)=(p(s),r(s)) and start with ker(o), or a declared finer initial partition P0 with b0 blocks. Split by all successor classes for the SAME finite total operations. At most |S|-b0 strict stages occur; the terminal equivalence is the unique coarsest stable refinement of that initial partition, preserving both p and r.',
      'F153-03: source R126 section 6 retains initial p AND r; output-only abbreviation can erase a required p distinction.')
amend('R127:FUTURE_EQ','statement',
      'With o(s)=(p(s),r(s)), s~t iff o(F_w(s))=o(F_w(t)) for every finite word w over the SAME operation alphabet, including the empty word. This is exactly the terminal stable refinement starting from ker(o).',
      'F153-03: R127 section 3 explicitly uses joint observation o=(p,r).')
amend('C:P1','statement',
      'For all realized complete types s,t under fixed J and C1-OI, J(s)!=J(t) implies e(s)!=e(t). For every s, the complete-type fiber {s} is contained in the J-fiber of s. There EXISTS a strict inclusion iff J is noninjective; strict inclusion at a particular s requires that particular fiber to contain another type.',
      'F153-04: make the existential quantifier in strict refinement explicit; noninjectivity does not make every fiber nontrivial.')
amend('R134:PROBE_DUAL','statement',
      'Forced-probe robust success equals min_(0<=q<=1) F(q), F(q)=sum_y max(q*a_y,(1-q)*b_y). Evaluate endpoints and breakpoints q=b_y/(a_y+b_y) ONLY for y with a_y+b_y>0. Rows with both masses zero contribute identically zero and supply no breakpoint.',
      'F153-05: avoid 0/0 for impossible or zero-survival transcripts; the value theorem is unchanged.')
amend('A:TOY_WHOLE_DIFF','statement',
      'In TOY_MATH at fixed input, whole transition image sizes for (alpha,beta)=(0,0),(1,0),(0,1),(1,1) are 2,4,4,8. Different image sizes imply nonisomorphism. The equal-image single-link pair is NOT separated by this invariant; any further distinction requires fixed constituent ports or another invariant. Pair retention counts are 1; 2 then 1; 2 then 1; 4 at every positive horizon, respectively.',
      'F153-06: distinguish three invariant regimes from an unsupported claim that all four settings are pairwise separated by image size.')
amend('C:PRICE_TRANSMISSION','scope',
      'Finite reproductive attribution, W>=0 and mean W>0. Selection reweighting determines parent contributions; descendant means Cprime may change. Faithful copying Cprime=C is only the selection-only special case. The formula is exact accounting, not a closed dynamical model.',
      'F153-07: factor the common reweighting setup from the faithful-copy specialization.')
amend('C:LOCAL_FIBER','scope',
      'C^1 or smoother map between finite-dimensional smooth charts; rank r constant on a NEIGHBORHOOD. Local fibers have dimension n-r there. Neither a singular pointwise rank nor an arbitrary complete-type space supplies this chart.',
      'F153-08: explicitly sufficient regularity for use of the constant-rank theorem; no claim to refute weaker variants.')

source_files={s['paper']:s['snapshot_workspace_path'] for s in old['source_versions']}
source_files.update({
 'R126':'records/R126_Theory_First_Projection_and_Causal_State_20261006/R126_Theory_Note.md',
 'R127':'records/R127_Capability_Necessity_and_Actual_Support_20261006/R127_Theory_Note.md',
 'N128':'records/R128_Unified_Formal_Map_Audit_20261006/THEORY_EXTENSION.md',
 'R131':'records/R131_Theorem_Synthesis_and_Archive_20261006/R131_Probe_Completeness_Theorem.md',
 'R132':'records/R132_Common_Realization_and_Partial_Closure_20261007/R132_Common_Realization_Theorems.md',
 'R133':'records/R133_Observable_Common_Control_20261007/R133_Observable_Common_Control.md',
 'R134':'records/R134_Quantitative_Control_and_Probe_Cost_20261007/R134_Quantitative_Control.md',
 'R135':'records/R135_Capability_Preservation_and_Abstraction_20261007/R135_Capability_Preservation.md',
 'R136':'records/R136_Causal_Translation_and_Query_Order_20261007/R136_Causal_Translation.md',
 'R137':'records/R137_Executable_Feedback_Interfaces_20261007/R137_Executable_Feedback.md',
 'R145':'records/R145_Intervention_Transport_and_Identification_20261007/Intervention_Transport_and_Organization_v0_2.md',
 'R146':'records/R146_Experience_Intelligence_and_Self_20261007/Experience_Intelligence_and_Self_v0_1.md',
 'R147':'records/R147_Self_Reference_Rewiring_20261007/SELF_REFERENCE_REWIRING.md',
 'R149':'records/R149_Nine_Source_Integration_20261007/COMPATIBILITY_AND_SELF_TARGETS.md'})
# N128's actual source filename is resolved from the existing map source label.
if not (ROOT/source_files['N128']).exists():
    candidates=list((ROOT/'records/R128_Unified_Formal_Map_Audit_20261006').glob('*.md'))
    candidates=[p for p in candidates if 'THEORY' in p.name.upper() or 'JOINT' in p.name.upper()]
    if len(candidates)!=1: raise RuntimeError(('Resolve N128 source explicitly',candidates))
    source_files['N128']=candidates[0].relative_to(ROOT).as_posix()
for p in source_files.values(): assert (ROOT/p).is_file(),p

domain={
 'A':'Typed actual occurrences at specified intervals/boundaries and common complete K for ontic claims; finite models/views and externally declared bridge targets remain separate sorts. Pure symmetry/topology/quotient claims use their explicit abstract domains, not an unstated actual realization.',
 'B':'One pinned source-theory subclaim, fixed finite physical view, typed expression interpretations, fixed bridge and source-faithful residuals. Toy graphs/dynamics and archived numerical outputs are different objects from biological theory validation.',
 'C':'One fixed realized complete-type set and capability contract for type claims; separately specified finite probability/selection/decision models or local smooth charts for mathematical claims. Parameters and laws cannot migrate between these submodels.',
 'D':'Declared current bearer Q, other O and task G are different variables. Finite path/payoff/design models, synthetic evidence, retrospective evidence and actual-type interpretation have distinct statuses; only the last uses the explicit actual/constitutive bridge.',
 'R126':'Finite nonempty sufficient state set, fixed finite total deterministic operation alphabet, p:S->p(S), output r, joint initial observation o=(p,r), fixed time/ports; metric targets only where declared. Projection transport separately uses complete-type bijection.',
 'R127':'Fixed delayed-query task, cut and side-information domain, SAME supported b,q and downstream kernel for cut-TV claims; actual support/relation interpretation requires separately grounded event/constitutive premises. Quantifiers range only over the named admitted protocols.',
 'N128':'Finite common sufficient state domain and fixed total operations/Markov kernels; p(S) is the realized joint image. Marginal laws, joint laws and domain restrictions must remain distinct.',
 'R131':'Finite outcome alphabet, normalization plus fixed expectation probes, full probability simplex for universal identification, fixed kernels/time/ports for closure; rank over the real numbers and exact probe values unless an error bound is separately supplied.',
 'R132':'Finite task/slot matching OR the explicitly distinct finite partial controlled-kernel model. Matching assumes no additional constraints; closure preserves menus and JOINT next-summary/output laws for every represented state and common legal history policy.',
 'R133':'Finite persistent hidden model/state family, finite horizon, common observable policy and legal actions. Probability-one success uses support and a closed goal/success flag; one-shot message problems have separate fixed action/observation contracts.',
 'R134':'Finite persistent model/state coordinates and one common randomized observable policy; private coins independent of nature, fixed finite horizon. Success-profile vectors precede minimax. Probe survival and transcript probabilities are joint fixed data; supports with zero mass remain harmless.',
 'R135':'Nonempty compact convex profile sets in the same finite-dimensional [0,1]^n, common tasks/resources/observation protocol; finite controlled abstraction uses uniform joint rows, same total legal actions and a pulled-back payoff. Partial-legality countermodels have their own domain.',
 'R136':'Finite static experiment or finite no-feedback stream with one parameter-independent causal kernel; preserve deadline, legal actions, randomization and query budget. Offline translation is a different admissible class.',
 'R137':'Finite sufficient controlled model, onto visible state, explicitly legal menus, joint next-state/output laws, common memoryless action decoder and fresh conditional randomization. All represented starts and legal controller extensions at all histories; horizon H finite.',
 'R145':'Finite binary implementation family, fixed mechanism k, labeled ports and one-tick preparation/intervention/readout timing. Logical quotient versus represented implementation versus actual token are separate objects. Constitutive realization is a separate premise.',
 'R146':'Actual bearer and grounded attachment, selected self-target laws, installed model and separate abstract decoder class; conceptual Self_I and experiential mineness remain distinct targets. Finite symmetry/cell countermodels do not establish those semantic bridges.',
 'R147':'Two n-element role sorts with n>=2, bijections beta/sigma/tau, all independent bit command vectors, synchronous one-tick model; fixed-beta physical rewiring versus full coordinate renaming. Isolated-record comparison is a separate declared restriction.',
 'TA15':'Typed target and regime contract; set-map factorization on realized images, relation composition at one SAME intermediate, and metric/probability error bounds on a common comparison. Opposing existence-model nonidentification is not simultaneous assertion of both existences.',
 'TA16':'Historical RRH-E is a separate conjectural package; finite graph/information/coding examples use the explicitly stated cuts, alphabets, intervention transport, modes and encoded states. Historical conjecture is not a new basal C1 axiom.',
 'TA17':'Finite interventional variables with H(U)>0; internal attribution, functional quotient, inheritance, successor-set law and motivational stake are different objects. Transported recodings preserve experimental semantics; marginal posterior data are not a joint set law.',
 'TA18':'Selected participation germ, trajectory descriptor and bridge Phi are separately typed. Joint-response retention, pair separation and isomorphism covariance are independent premises. The source bridge is not silently identified with complete C1.',
 'TA19':'Compatible group actions and candidate fibers; separate finite-covering/unique-path-lifting and finite labeled-metric-landscape setups. Numerical supplement is an archived report. Main Markdown source coverage ends at section 5.',
 'R149':'Nonempty configuration Omega, SAME actual bearer/time assignments and complete K, k/e type maps and arbitrary descriptor r on that domain. Optional type invariance r=bk must be supplied; selected f and complete e are distinct recovery targets.'}

incoming=defaultdict(list)
for r in g['rules']: incoming[r['conclusion']].append(r)
@lru_cache(None)
def routes(id):
    if not incoming[id]: return (frozenset([id]),)
    alternatives=[]
    for r in incoming[id]:
        terms=[frozenset()]
        for p in r['all_of']:
            terms=[a|b for a in terms for b in routes(p)]
        alternatives.extend(terms)
    # Deduplicate only. Never absorb a stronger route: preserve provenance.
    return tuple(dict.fromkeys(alternatives))

def descendants(ids):
    reached=set(ids)
    while True:
        new=reached|{r['conclusion'] for r in g['rules'] if reached.intersection(r['all_of'])}
        if new==reached:return sorted(reached)
        reached=new

gap=[]
def issue(id,state,title,seed,why,discharge,kind='OPEN_OBLIGATION'):
    gap.append({'id':id,'state':state,'kind':kind,'title':title,'direct_nodes':seed,
                'potentially_affected_nodes':descendants(seed),'reason':why,'required_discharge':discharge})
issue('F153-01','CORRECTED','107 nodes lacked an inline statement',list(definitions),
      'The old labels were not complete definitions or premise statements.',
      '107 explicit source-linked statement repairs; original values preserved in baseline and AMENDMENTS.','MAP_DEFECT')
issue('F153-02','CORRECTED','223 nodes lacked an inline scope',
      [n['id'] for n in old['nodes'] if not n.get('scope')],
      'A theorem could be read without its finite-model or actual-token domain.',
      'Each card now includes its own scope, family domain and expanded separate conjunctive premise routes. This does not certify substitutions.','MAP_DEFECT')
issue('F153-03','CORRECTED','R126/R127 initial observation lost p in abbreviation',
      ['R126:MODEL','R126:P4','R127:FUTURE_EQ'],
      'Source uses o=(p,r). Output r alone can merge a required current-p distinction.',
      'Restore ker(p,r) and future o; verify two-state identity/constant-r counterexample.','SOURCE_FIDELITY')
issue('F153-04','CORRECTED','Strict fiber inclusion needs an existential/location quantifier',['C:P1'],
      'Noninjective J need not have every fiber nonsingleton.',
      'State existence of a strict fiber; local strictness requires a collision in that fiber.','QUANTIFIER_REPAIR')
issue('F153-05','CORRECTED','Undefined zero-mass probe breakpoint',['R134:PROBE_DUAL'],
      'The expression b/(a+b) is undefined at a=b=0.',
      'Ignore zero-contribution rows when listing breakpoints; preserve endpoints.','DOMAIN_REPAIR')
issue('F153-06','CORRECTED','Four toy settings have only three image-size regimes',['A:TOY_WHOLE_DIFF'],
      'The two one-link settings both have image size four; this invariant alone does not separate them.',
      'Explicit 2,4,4,8 statement, with separate fixed-port qualification.','SCOPE_REPAIR')
issue('F153-07','CORRECTED','Faithful-copy specialization was bundled into shared selection premise',
      ['C:SELECTION','C:DESCENDANT_ATTRIBUTION','C:PRICE_TRANSMISSION'],
      'A broad reading imposes faithful copying on the transmission extension as well.',
      'Shared reweighting setup separated from selection-only Cprime=C; algebraic transmission identity retained.','PREMISE_REPAIR')
issue('F153-08','CLARIFIED','Smooth local-fiber theorem regularity',['C:CONST_RANK'],
      'Bare differentiable-map wording did not explicitly state a sufficient smoothness/neighborhood contract.',
      'Use C^1 or smoother and locally constant rank; do not declare all weaker variants false.','SCOPE_REPAIR')
issue('F153-09','OPEN','Actual-token admission and boundary grounding',['A:TOKEN_CRITERIA','A:ACTUAL_TOKEN','R127:EVENT_SUPPORT'],
      'Source criteria are meaningful constraints, not an effective necessary-and-sufficient physical admission algorithm.',
      'For an application, supply a precise physical domain and evidence meeting each criterion. No new basal experience gate.')
issue('F153-10','OPEN','Finite view does not certify constitutive completeness',
      ['A:D_ONTIC','A:ACTUAL_COMPLETE_TOY','D:ACTUAL_CHANGE','R145:ACTUAL_BRIDGE','R147:ACTUAL_BRIDGE'],
      'Exact finite dynamics and observed invariants may omit actual constitutive distinctions.',
      'Supply independently grounded actual realization and an argument that every admitted complete isomorphism preserves the represented invariant; distinguish macro targets.')
issue('F153-11','OPEN','Specific felt-self and conceptual-I semantics',
      ['A:SELF_WITNESS','R146:DEFINITION_CONTRACT','R146:SELF_CONTRACT','R149:SELF_TARGET'],
      'q(e), Self_I and internal attribution do not construct the same target or establish phenomenological meaning.',
      'Specify the selected self-experiential/semantic target and a justified constitutive bridge within experience. Preserve wrong self-models and nonverbal mineness.')
issue('F153-12','OPEN','Operational bridge, geometry and measurement validation',
      ['A:GEOMETRY','A:BRIDGE_FWD','A:BRIDGE_REV','A:MEAS','B:BAC','B:TFR'],
      'These supplied choices are not validated by composing definitions or constructing an isomorphic abstract object.',
      'Declare target-specific independently justified bridge/metric/error rules; retain falsifiability and frozen versions.')
issue('F153-13','OPEN','Archived numerical claims are not reproduced here',
      ['B:MODEL19','B:MODEL20','B:GRID19','B:GRID20','TA19:NUMERICS','D:E1','D:E2','D:E3','D:A1'],
      'Evidence records retain their source status; exact runtime/readout details and empirical validity are separate from this map audit.',
      'Recover exact versioned parameter/protocol/code records and reproduce only if needed for a claim. Do not infer empirical consciousness or validate a whole target theory.')
issue('F153-14','OPEN','TA19 source coverage incomplete beyond recovered Markdown',
      ['TA19:GROUP_SETUP','TA19:COVER','TA19:TOPOLOGY','TA19:NUMERICS'],
      'Pinned main Markdown ends at section 5; supplement is separately available. Main PDF was not inspected in this round.',
      'Compare published PDF/source packaging and add exact recovered anchors before claiming coverage of all source sections.')
issue('F153-15','OPEN','Global semantic consistency and substitutions are not certified',list(N),
      'A context-indexed hypergraph and finite countermodels do not decide all mathematical/physical/semantic conjunctions. Different scenarios cannot be indiscriminately conjoined.',
      'For each proposed application supply a compatible instantiated premise bundle; validate target/time/signature/law bindings and higher-order interactions. No global-semantic-pass flag.')
issue('F153-16','OPEN','Ordinary mathematical proofs are not proof-assistant certification',list(N),
      'All cards are mathematical prose and formula strings. Historical manual review labels do not mean a kernel checked a proof term.',
      'Encode typed statements, imported theorem libraries and proof terms with explicit axiom dependencies; semantic/physical assumptions will still remain assumptions.')
issue('F153-17','OPEN','C1 experiential interpretation remains an axiom',['A:C1'],
      'Constructing a copy of a physical structure does not independently establish that the copy is experiential.',
      'Keep conditional interpretation explicit; an empirical or philosophical defense is separate from the mathematical consequences.')
issue('F153-18','OPEN','Historical bridge compatibility is target-dependent',
      ['TA16:RRH_HISTORY','TA18:PRD','TA18:PAIR_SEPARATION','TA18:ISO_BRIDGE'],
      'Historical gates/participation sufficiency cannot be imported as complete-experience axioms without common-domain compatibility checks.',
      'Identify complete versus selected target, compare actual complete-type fibers, and either discharge compatibility, narrow the target, or retain an explicit conflict.')

proof_sections={
 'P01':['a01','a02','a03','a37'], 'P02':['a14'],
 'P03':['a04','a19','a20','a21','a22','a23a','a23b'],
 'P04':['c01','c02','c03','c04','c19','r149_ta15_fiber','r149_r149_compatibility','r149_r149_null_target'],
 'P05':['r146_self_target'],
 'P06':['a34','r126_2','n128_1','n128_2','n128_3','n128_4','n128_5'],
 'P07':['r132_closure','r137_local','r137_loop','r137_approx','r137_observation','r137_seed'],
 'P08':['c08','c09','c10','c11'],
 'P09':['c12','c20','c21','c22','c24','r127_2','r127_3a'],
 'P10':['a17','a18','r146_centered','r149_ta19_local','r149_ta19_monodromy'],
 'P11':['r147_routing','r147_memory','r147_type','r149_r149_self_application'],
 'P12':['r149_ta15_composition','r149_ta15_error','r149_ta18_germ_nonfactor','r149_ta18_phen_nonfactor','r149_ta18_idle','r149_ta18_factor']}
proof_for={id:k for k,ids in proof_sections.items() for id in ids}
assert set(proof_for)<=set(R)
for r in g['rules']:
    if r['statement'] != N[r['conclusion']]['statement']:
        changes.append({'rule':r['id'],'field':'statement','before':r['statement'],
                        'after':N[r['conclusion']]['statement'],'reason':'Synchronize rule conclusion with its explicitly amended node contract.'})
        r['statement']=N[r['conclusion']]['statement']
    extra={
      'r126_4':'Start from ker(o) with o=(p,r), not r alone. Each strict split adds a block; a stable refinement of ker(o) refines every stage by induction.',
      'r127_1b':'With o=(p,r), future-word equivalence includes the empty word and therefore refines ker(o). Prefixing a letter preserves equivalence; induction shows every stable refinement of ker(o) preserves all future o values.',
      'r134_probe':'For fixed q optimize each decision independently to obtain max(q*a_y,(1-q)*b_y). Finite convex minimax gives the dual. This convex piecewise-affine function attains a minimum at an endpoint or a breakpoint with a_y+b_y>0; zero-zero rows vanish.',
      'c10':'Use the shared positive-mean reproductive reweighting, allowing specified descendant means Cprime. Add and subtract E[W*C]/E[W]. Faithful copying is the Cprime=C specialization, not a premise of the general transmission term.'}
    if r['id'] in extra:
        changes.append({'rule':r['id'],'field':'proof_sketch','before':r['proof_sketch'],'after':extra[r['id']],'reason':'R153 source/domain repair.'})
        r['proof_sketch']=extra[r['id']]
    effective=r['kind']
    if r['id'] in ['a29','a30']: effective='ASSUMPTION_PACKAGE_CONSTRUCTION'
    if r['id'] in ['a06','a35']: effective='META_DEPENDENCY_AUDIT'
    if r['id'] in ['a37','r127_4']: effective='DEFINITION_APPLICATION'
    r['formal_contract_R153']={
       'relation_type':effective,'premise_connective':'AND','alternative_routes':'Separate rule IDs are OR alternatives; never flatten their assumptions into one compulsory set.',
       'quantification':'For each common instantiation satisfying ALL listed premise contracts, conclude the stated conclusion at that same instantiation. Internal exists/forall, limits and countermodel quantifiers remain as written; no automatic exchange.',
       'bindings_required':['same target object/bearer where shared','same time/horizon/grain','same signature and admissible symmetries','same probability law/model and policy class','same operations/enabledness/observations','same epistemic target and interpretation'],
       'root_premise_routes':[sorted(x) for x in routes(r['conclusion'])] if len(incoming[r['conclusion']])==1 else [sorted(set().union(*xs)) for xs in __import__('itertools').product(*(routes(p) for p in r['all_of']))],
       'proof_location':REL+'/FORMAL_FOUNDATION.md section '+proof_for[r['id']] if r['id'] in proof_for else 'Pinned source named by the rule; inherited proof_sketch is reproduced in RULE_LEDGER.',
       'review_status':'R153_EXPANDED_ARGUMENT_AND_BOUNDARY_REVIEW' if r['id'] in proof_for else 'INHERITED_ARGUMENT_WITH_R153_DEPENDENCY_AND_CONTRACT_CHECK',
       'machine_proof':False,'source_edition':source_files[r['conclusion'].split(':')[0]]}

cards=[]
for n in g['nodes']:
    id=n['id']; family=id.split(':')[0]
    leaves=[sorted(t) for t in routes(id)]
    if not n.get('scope'):
        amend(id,'scope',n.get('domain') or domain[family],
              'R153 explicit inline scope; exact conjunctive premises and context bindings remain separately recorded, not silently discharged.')
    src=source_files[family]
    ob=[x['id'] for x in gap if x['state']=='OPEN' and id in x['potentially_affected_nodes']]
    n['formal_contract_R153']={
       'object_domain':domain[family],
       'quantifier_convention':'The displayed statement and each separate premise route are read together. Model parameters are fixed throughout one instance; universal state/action clauses apply only to that instance. Existential witnesses and alternative routes are not universally asserted.',
       'source_anchor':{'path':src,'sha256':digest(ROOT/src),'original_locator':n['source']},
       'premise_routes':[{'rule':r['id'],'all_of':r['all_of']} for r in incoming[id]],
       'root_premise_routes':leaves,
       'proof_or_evidence':([{'rule':r['id'],'argument':r['proof_sketch'],'review':r['formal_contract_R153']['review_status']} for r in incoming[id]] or
                           [{'role':'ROOT_DECLARATION_OR_RECORDED_EVIDENCE','status':n['status'],'note':'No graph derivation. Definition/assumption/model/evidence status is retained; a terminal dependency is not automatically a proven truth.'}]),
       'open_obligations':ob,
       'finite_boundary':domain[family],
       'purpose':'Trace this precise target and its dependencies without promoting mathematical representation to actual constitution or experience measurement.',
       'machine_formalized':False}
    cards.append(n)

# Pin the already published TA25 text without changing release files.
published=Path('/workspace/scratch/ab49378ea8b4/release/research/experience-intelligence-self/published')
if published.exists():
    target=HERE/'sources';target.mkdir(exist_ok=True)
    src=published/'experience-intelligence-self-v1.0.md'
    sums=(published/'SHA256SUMS.txt').read_text()
    assert digest(src) in sums
    (target/src.name).write_bytes(src.read_bytes())
    g['source_versions'].append({'paper':'TA25','version':'1.0','doi':'10.5281/zenodo.23206492','snapshot_workspace_path':(target/src.name).relative_to(ROOT).as_posix(),'sha256':digest(src),'bytes':src.stat().st_size,'integration_status':'Published synthesis; 13 R151 claim cards crosswalk existing nodes. No new theorem count or modification of published bytes.'})
crosswalk=json.loads((ROOT/'records/R151_Foundational_Manuscript_20261007/MANUSCRIPT_CLAIMS.json').read_text())
dump(HERE/'TA25_CROSSWALK.json',{'doi':'10.5281/zenodo.23206492','claims':crosswalk,'role':'Inherited claim-to-map crosswalk; source text hash pinned separately.'})
source_checks=[]
for s in g['source_versions']:
    p=ROOT/s['snapshot_workspace_path'];actual=digest(p)
    assert actual==s['sha256'],s['paper']
    source_checks.append({'paper':s['paper'],'path':s['snapshot_workspace_path'],'sha256':actual,'bytes':p.stat().st_size,'hash_pass':True})
dump(HERE/'SOURCE_CHECKS.json',source_checks)
dump(HERE/'GAP_LEDGER.json',gap)
dump(HERE/'AMENDMENTS.json',changes)
dump(HERE/'NODE_CONTRACTS.json',cards)
dump(HERE/'RULE_CONTRACTS.json',g['rules'])

g['revision']='R153-v1.0'
g['formalization_R153']={'date':'2026-10-07','baseline_sha256':digest(BASE),'baseline_revision':old['revision'],'nodes':len(N),'rules':len(R),'scope':'Exhaustive contract/dependency coverage of inherited map, not complete proof-assistant or global semantic certification.','foundation':REL+'/FORMAL_FOUNDATION.md','nodes_file':REL+'/NODE_CONTRACTS.json','rules_file':REL+'/RULE_CONTRACTS.json','gaps':REL+'/GAP_LEDGER.json','amendments':REL+'/AMENDMENTS.json','source_files':source_files,'historical_fields':'Unmodified fields retain original status; effective contract classifications and open obligations override any reading of blanket proof completeness.'}
dump(ROOT/'UCT_FORMAL_GRAPH.json',g)

lines=['# R153 — Every node, statement, scope and premise route','',
       '391 inherited nodes; no silently deleted IDs. All formulas are ordinary mathematical text. Open obligations are not closed by this export. Source originals and baseline are preserved.','']
for n in cards:
    c=n['formal_contract_R153'];lines += ['## '+n['id']+' — '+n['label'],'',n['statement'],'',
       '**Status:** '+n['status']+' (inherited; not a machine proof).','',
       '**Scope:** '+n['scope'],'','**Typed domain:** '+c['object_domain'],'',
       '**Source:** ['+n['source']+'](../../'+c['source_anchor']['path']+'); SHA256 `'+c['source_anchor']['sha256']+'`.','']
    if c['premise_routes']:
        for route in c['premise_routes']:lines+=['- Route `'+route['rule']+'`: **all of** '+', '.join('`'+x+'`' for x in route['all_of'])+'.']
        lines+=['','**Expanded terminal premises** (each line is one alternative conjunction; terminals are not all proven):','']
        for route in c['root_premise_routes']:lines+=['- '+', '.join('`'+x+'`' for x in route)]
    else:lines+=['**Root role:** supplied definition, assumption, model, or source evidence; no derivation is asserted.']
    lines+=['','**Open obligations:** '+', '.join(c['open_obligations']), '']
    for ev in c['proof_or_evidence']:
        if 'argument' in ev:lines+=['**Argument '+ev['rule']+':** '+ev['argument'],'']
(HERE/'NODE_LEDGER.md').write_text('\n'.join(lines)+'\n')
lines=['# R153 — Every inference rule','',
       'Each all_of is conjunction; separate routes are alternatives. Shared-variable substitution is required, not machine certified.','']
for r in g['rules']:
    c=r['formal_contract_R153'];lines += ['## '+r['id']+' → '+r['conclusion'],'',
       '**Relation:** '+c['relation_type']+'. **Review:** '+c['review_status']+'.','',
       '**All simultaneous premises:** '+', '.join('`'+x+'`' for x in r['all_of'])+'.','',
       '**Conclusion:** '+r['statement'],'','**Inherited argument:** '+r['proof_sketch'],'',
       '**Source:** '+r['source']+'; '+c['source_edition'], '',
       '**Detailed argument:** '+c['proof_location'],'',
       '**Instantiation checks:** '+ '; '.join(c['bindings_required'])+'.','']
(HERE/'RULE_LEDGER.md').write_text('\n'.join(lines)+'\n')
summary={'baseline_nodes':len(old['nodes']),'baseline_rules':len(old['rules']),'nodes':len(N),'rules':len(R),
 'missing_statements_before':sum(not n.get('statement') for n in old['nodes']),
 'missing_scopes_before':sum(not n.get('scope') for n in old['nodes']),
 'missing_statements_after':sum(not n.get('statement') for n in cards),
 'missing_scopes_after':sum(not n.get('scope') for n in cards),
 'detailed_proof_review_rules':len(proof_for),
 'inherited_argument_contract_review_rules':len(R)-len(proof_for),
 'gap_states':dict(Counter(x['state'] for x in gap)),
 'source_hashes_passed':len(source_checks),
 'machine_proof_certification':False,'global_semantic_consistency_certification':False}
dump(HERE/'BUILD_SUMMARY.json',summary)
print(json.dumps(summary,ensure_ascii=False,indent=2))
