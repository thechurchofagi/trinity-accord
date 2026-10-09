#!/usr/bin/env python3
"""Exact finite organization model. It does not simulate or measure H."""
from fractions import Fraction as Q
from itertools import permutations, product
from pathlib import Path
import json,csv

def inv(p):
 out=[0]*len(p)
 for i,v in enumerate(p):out[v]=i
 return tuple(out)
def compose(f,g):return tuple(f[g[i]] for i in range(len(g)))
def replace(f,a,y):return tuple(y if i==a else v for i,v in enumerate(f))
def update(f,a,y,u):return replace(f,a,y) if u else f

def run():
 total=0;probes=0;relabel_checks=0;mixing_checks=0;axes=set();examples={};rows=[]
 for n in (2,3,4):
  ps=list(permutations(range(n)))
  for p,f,c,u in product(ps,ps,ps,(0,1)):
   total+=1
   success=compose(p,c)==tuple(range(n));aligned=f==p
   axes.add((int(success),int(aligned),u))
   if (int(success),int(aligned),u) not in examples:examples[(int(success),int(aligned),u)]=dict(n=n,plant=p,predictor=f,controller=c,use=u)
   for a in range(n):
    after=update(f,a,p[a],u);probes+=1
    changed=after!=f
    assert changed==bool(u and f[a]!=p[a])
    assert after[a]==(p[a] if u else f[a])
    # A deliberate discrepancy tests consumer use even at perfect alignment.
    z=(f[a]+1)%n;perturbed=update(f,a,z,u)
    assert (perturbed!=f)==bool(u)
    # A complete copied state has identical updates, independently of biography tags.
    assert update(tuple(f),a,p[a],u)==after
   if n==2:
    rows.append(dict(n=n,plant=str(p),predictor=str(f),controller=str(c),use=u,success=int(success),alignment=int(aligned)))
  # Relabeling the grounded action/output ports transports every map, not predictor alone.
  for p,f,alpha,beta in product(ps,ps,ps,ps):
   ai=inv(alpha);pp=compose(beta,compose(p,ai));ff=compose(beta,compose(f,ai))
   assert sum(x!=y for x,y in zip(p,f))==sum(x!=y for x,y in zip(pp,ff))
   assert (p==f)==(pp==ff);relabel_checks+=1
  # Stochastic predictor F_lambda=(1-lambda)F + lambda P.
  for p,f in product(ps,ps):
   err0=Q(sum(f[a]!=p[a] for a in range(n)),n)
   for li in range(11):
    lam=Q(li,10);error=Q(0)
    for a in range(n):
     # TV distance from deterministic actual row is 1 - probability at actual consequence.
     prob=(1-lam)*int(f[a]==p[a])+lam
     error+=1-prob
    error/=n
    assert error==(1-lam)*err0;mixing_checks+=1
 assert len(axes)==8
 # Error-gated versus unconditional reflex write: same register transition, different write events.
 comparator_pairs=0;write_event_differences=0
 for n in (2,3,4):
  for f in permutations(range(n)):
   for a,y,u in product(range(n),range(n),(0,1)):
    comparator_event=bool(u and f[a]!=y)
    reflex_event=bool(u)
    compared=replace(f,a,y) if comparator_event else f
    reflex=replace(f,a,y) if reflex_event else f
    assert compared==reflex
    comparator_pairs+=1
    if comparator_event!=reflex_event:write_event_differences+=1
 # Explicit two-target successful-output matched quartet.
 p=(0,1);c=(0,1)
 quartet=[]
 for f,u in product(((0,1),(1,0)),(0,1)):
  quartet.append(dict(plant=p,controller=c,predictor=f,use=u,task_outputs=compose(p,c),prediction_mismatch=Q(sum(f[a]!=p[a] for a in range(2)),2).__str__(),prediction_after_real_feedback=update(f,0,p[0],u),prediction_after_forced_feedback=update(f,0,1-f[0],u)))
 out=dict(result_id='R204-SAU-v0.2.0',comparator_reflex_pairs=comparator_pairs,write_event_differences=write_event_differences,model_instances=total,real_feedback_probe_checks=probes,port_relabel_checks=relabel_checks,exact_continuous_mixture_checks=mixing_checks,all_eight_combinations=[list(x) for x in sorted(axes)],axis_witnesses=[dict(axes=list(k),**v) for k,v in sorted(examples.items())],successful_output_matched_quartet=quartet,violations=0,h_labels_generated=False,scope='Finite sensorimotor organization and update law only',status='PASS')
 here=Path(__file__).resolve().parent
 (here/'EXACT_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
 with (here/'BINARY_MODEL_ROWS.csv').open('w') as stream:
  w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print(json.dumps({k:out[k] for k in ['status','model_instances','real_feedback_probe_checks','port_relabel_checks','exact_continuous_mixture_checks','violations']}))
if __name__=='__main__':run()
