"""Exact toy regressions and additive map checks, not empirical or theorem-prover validation.
Run python CHECKS.py [workspace_root] [base_graph_json].
"""
import itertools,json,sys,hashlib
from pathlib import Path
here=Path(__file__).resolve().parent
p=Path(sys.argv[1]) if len(sys.argv)>1 else here.parents[1]
base_path=Path(sys.argv[2]) if len(sys.argv)>2 else None
ext=json.loads((here/'MAP_EXTENSION.json').read_text());g=json.loads((p/'UCT_FORMAL_GRAPH.json').read_text())
results=[]
def check(name,condition,detail):
 results.append({'name':name,'pass':bool(condition),'scope':detail})
 if not condition:raise AssertionError(name)
rows=[(x,m) for x in [0,1] for m in [0,1]]
a={(x,0) for x,m in rows};b={(x,x^m) for x,m in rows}
check('fixed_storage_one_wire_witness',len(rows)==4 and len(a)==2 and len(b)==4,'Exact four-row repertoire; both mechanisms retain two bits. No physical realization claimed.')
check('current_channel_retained',all((x,0) in a for x,c in b),'Projection pi(x,c)=(x,0).')
check('matched_current_temporal_contrast',(1,1^0)!=(1,1^1),'Same current x=1; comparator distinguishes m=0 from m=1.')
check('matched_baseline_not_role_identity',(0,0^0)==(0,0),'An equal baseline output does not identify the stored-past operand path.')
count=0
for mask in range(1,16):
 R=[r for i,r in enumerate(rows) if mask>>i&1];A={a for a,b in R}
 for vals in itertools.product([0,1],repeat=4):
  c=dict(zip(rows,vals));out={(a,c[a,b]) for a,b in R};ra={a:len({c[x,y] for x,y in R if x==a}) for a in A}
  assert len(out)==sum(ra.values())
  assert (len(out)>len(A))==any(v>1 for v in ra.values())
  assert {(a,0) for a,z in out}=={(a,0) for a in A}
  count+=1
check('all_boolean_joint_supports',count==240,'240 finite support/gate cases regress the general disjoint-fiber proof; not its replacement.')
restricted=[(0,0),(1,1)]
check('restricted_reachability_blocks_strict_gain',len({(x,x^m) for x,m in restricted})==2,'Missing mixed histories prevents strict refinement; gate size alone is insufficient.')
fast=[0]
for _ in range(7):fast.append(1-fast[-1])
delayed=[0,0]
for _ in range(7):delayed.append(1-delayed[-2])
slow=delayed[1:]
check('unscaled_delay_countermodel',fast==[0,1,0,1,0,1,0,1] and slow==[0,1,1,0,0,1,1,0],'Declared-step feedback mismatch; not a subjective-time measurement.')
# An exact polynomial instance of the general delay retiming, using rational arithmetic.
from fractions import Fraction as F
for alpha in [F(1,2),F(1),F(3)]:
 for t in [F(0),F(2),F(5)]:
  for d in [F(1),F(2)]:
   y=lambda z:(z/alpha)**2
   assert y(t-alpha*d)==(t/alpha-d)**2
check('retiming_delay_identity',True,'Exact rational samples of y(t-alpha*d)=x(t/alpha-d); general argument is the chain rule in the manuscript.')
# Reducts agree but an omitted unary predicate has different cardinality.
check('selected_equal_full_different',len(set())!=len({0}),'Two abstract equal-carrier reducts; unary extra K predicate separates full structures.')
ids=[n['id'] for n in g['nodes']];ri=[r['id'] for r in g['rules']]
check('unique_node_rule_ids',len(ids)==len(set(ids)) and len(ri)==len(set(ri)),'Graph syntax only.')
s=set(ids)
check('all_rule_endpoints',all(set(r['all_of'])<=s and r['conclusion'] in s for r in g['rules']),'References only, not logical validity.')
check('all_context_endpoints',all(c['from'] in s and c['to'] in s for c in g['context_links']),'Context links are not proof edges.')
for typ in ['nodes','rules','context_links']:
 check('new_'+typ+'_exact',all(x in g[typ] for x in ext[typ]),'Exact extension objects present in aggregate.')
if base_path:
 base=json.loads(base_path.read_text())
 for typ in ['nodes','rules','context_links']:
  check('old_'+typ+'_prefix_preserved',g[typ][:len(base[typ])]==base[typ],'All pre-existing entries preserved field-for-field, including historical rules and effective overlays.')
node={n['id']:n for n in g['nodes']}
for r in ext['rules']:
 contract=node[r['conclusion']]['formal_contract_TE20261008']['premise_routes']
 assert {'rule':r['id'],'all_of':r['all_of']} in contract
check('new_all_of_contracts',True,'Exact five rule premise routes; actual/model/axiom premises remain explicit.')
newnote=here/'Organization_Transformations_and_Relational_Increment_v0_1.md'
digest=hashlib.sha256(newnote.read_bytes()).hexdigest()
check('new_source_hashes',all(n['formal_contract_TE20261008']['source_anchor']['sha256']==digest for n in ext['nodes']),'New source bytes match every new node anchor.')
# Only new derivations are checked here; inherited suspended R172 rules are not executed.
suspended={'r172_witnessed_online_action_use','r172_experience_internal_action_coordinate','r172_bio_ai_application_boundary'}
check('new_routes_do_not_execute_suspended_rules',not (suspended & {r['id'] for r in ext['rules']}),'New C1 route uses independently grounded actual role plus R157; R172 only contextual/effective.')
# Kahn check for the aggregate raw dependency graph (syntax only).
adj={n:set() for n in ids};deg={n:0 for n in ids}
for r in g['rules']:
 for n in r['all_of']:
  if r['conclusion'] not in adj[n]:adj[n].add(r['conclusion']);deg[r['conclusion']]+=1
stack=[n for n in ids if deg[n]==0];seen=[]
while stack:
 n=stack.pop();seen.append(n)
 for z in adj[n]:
  deg[z]-=1
  if deg[z]==0:stack.append(z)
check('aggregate_acyclic_syntax',len(seen)==len(ids),'Acyclicity is not semantic consistency or proof verification.')
def reach(vertices, edges, a, b):
 seen={a}; todo=[a]
 while todo:
  u=todo.pop()
  for x,y in edges:
   if x==u and y not in seen:seen.add(y);todo.append(y)
 return b in seen
edge_universe=[(i,j) for i in range(4) for j in range(i+1,4)]
relay_cases=0
for mask in range(1<<len(edge_universe)):
 E={e for k,e in enumerate(edge_universe) if mask>>k&1}
 for u,v in E:
  F=(E-{(u,v)})|{(u,4),(4,5),(5,v)}
  assert all(reach(range(4),E,a,b)==reach(range(6),F,a,b) for a in range(4) for b in range(4))
  relay_cases+=1
check('faithful_relay_endpoint_regression',relay_cases==192,'192 DAG/edge substitutions check endpoint reachability; general proof is path expansion/contraction, not enumeration.')
check('migration_vs_fresh_initialization',reach(range(3),{(0,1),(1,2)},0,2) and not reach(range(3),{(1,2)},0,2),'Equal final values stipulated; only the actual migration graph has the source-to-consumer path. No unique lineage inferred.')
out={'scope':'Exact toy regression and additive graph/source checks. Manual general proofs are in the note. No empirical experiment, full-map semantic proof or C1 validation.','checks':results,'passed':len(results),'graph_counts':{k:len(g[k]) for k in ['nodes','rules','context_links']},'toy_support_gate_cases':count,'source_sha256':digest}
(here/'CHECK_RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':len(results),'counts':out['graph_counts'],'toy_cases':count}))
