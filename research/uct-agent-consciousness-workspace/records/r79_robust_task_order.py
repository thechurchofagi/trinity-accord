"""Reanalyse archived R78 checkpoints; no optimization or new model calls."""
from decimal import Decimal, getcontext
from itertools import product
from pathlib import Path
import hashlib, json

getcontext().prec=200
src=Path('r78_results/R78_Summary.json')
data=json.loads(src.read_text())
LABELS=list(product([0,1],repeat=4))
TARGET=(1,0,0,1)
X1=(0,0,1,1);X2=(0,1,0,1)

def pair_distances(H):
 h=[[Decimal.from_float(x) for x in row] for row in H]
 return {(i,j):sum((h[i][k]-h[j][k])**2 for k in range(2)) for i in range(4) for j in range(i)}
def graph_partition(ds, threshold_sq):
 p=list(range(4))
 def root(i):
  while p[i]!=i:i=p[i]
  return i
 edges=[]
 for (i,j),d in ds.items():
  if d<=threshold_sq:
   edges.append([i,j]);p[root(i)]=root(j)
 comps=sorted([tuple(j for j in range(4) if root(j)==i) for i in set(root(j) for j in range(4))])
 tasks=[f for f in LABELS if all(len({f[j] for j in c})==1 for c in comps)]
 edge_tasks=[f for f in LABELS if all(f[i]==f[j] for i,j in edges)]
 assert tasks==edge_tasks
 assert len(tasks)==2**len(comps)
 return {'components':comps,'edges':edges,'tasks':tasks,'task_count':len(tasks),
         'target_available':TARGET in tasks,'x1_available':X1 in tasks,'x2_available':X2 in tasks}
def compare(a,b):
 sa=set(a['tasks']);sb=set(b['tasks'])
 status='equal' if sa==sb else 'new_strictly_contains_old' if sa<sb else 'old_strictly_contains_new' if sb<sa else 'incomparable'
 # Pairwise refinement must agree with binary-task inclusion.
 def relation(part):return {(i,j) for c in part for i in c for j in c}
 assert (sa<=sb)==(relation(b['components'])<=relation(a['components']))
 return {'order':status,'gained_tasks':sorted(sb-sa),'lost_tasks':sorted(sa-sb)}

out=[]
grid=[Decimal(s) for s in ['0','0.001','0.01','0.1','0.5','0.65','0.7','0.8','1','2']]
for run in data['runs']:
 a=pair_distances(run['initial']['hidden']);b=pair_distances(run['final']['hidden'])
 rows=[]
 for e in grid:
  pa=graph_partition(a,(2*e)**2);pb=graph_partition(b,(2*e)**2)
  rows.append({'epsilon':str(e),'old':pa,'new':pb,**compare(pa,pb)})
 # Every regime is covered by its lower boundary. At a boundary, closed balls touch.
 breaks=sorted(set([Decimal(0),*a.values(),*b.values()]))
 regimes=[]
 for i,t in enumerate(breaks):
  pa=graph_partition(a,t);pb=graph_partition(b,t)
  upper=breaks[i+1].sqrt()/2 if i+1<len(breaks) else None
  lower=t.sqrt()/2
  regimes.append({'epsilon_lower_inclusive':str(lower),'epsilon_upper_exclusive':str(upper) if upper is not None else None,
   'squared_threshold_exact':str(t),'old':pa,'new':pb,**compare(pa,pb),
   'narrow_numeric_interval':upper is not None and upper-lower<Decimal('1e-12')})
 # Fixed local affine chart change with correctly transported sets is exactly invertible;
 # pair differences recover under inverse scaling. Reusing isotropic balls is a different channel.
 H=run['final']['hidden'];D=[[Decimal.from_float(v) for v in row] for row in H]
 transformed=[[2*z[0]+1,z[1]/3-2] for z in D]
 recovered=[[(z[0]-1)/2,(z[1]+2)*3] for z in transformed]
 err=max(abs(recovered[i][k]-D[i][k]) for i in range(4) for k in range(2))
 assert err<Decimal('1e-190')
 out.append({'seed':run['seed'],'condition':run['condition'],'grid':rows,'all_regimes':regimes,
   'old_squared_distances':{str(k):str(v) for k,v in a.items()},'new_squared_distances':{str(k):str(v) for k,v in b.items()},
   'transport_inverse_max_error':str(err)})

result={'status':'secondary deterministic analysis of archived R78 checkpoints; no training; no phenomenal measurement',
 'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'noise_model':'closed Euclidean balls on hidden activations; all four input states must remain allowed',
 'binary_task_order':'all 16 deterministic binary labels; arbitrary decoder; no cost guarantee',
 'arithmetic':'200-digit Decimal applied to exact binary64 archived center values; graph decisions use squared distances',
 'input_indices':data['input_domain'],'runs':out}
Path('R79_Robust_Task_Order_Results.json').write_text(json.dumps(result,indent=2)+'\n')
summary=[]
for r in out:
 for row in r['grid']:
  summary.append({'seed':r['seed'],'condition':r['condition'],'epsilon':row['epsilon'],'order':row['order'],
    'old_task_count':row['old']['task_count'],'new_task_count':row['new']['task_count'],
    'old_target':row['old']['target_available'],'new_target':row['new']['target_available'],
    'gained':len(row['gained_tasks']),'lost':len(row['lost_tasks'])})
import csv
with Path('R79_Robust_Task_Order_Table.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
print(json.dumps({'run_count':len(out),'regime_count':sum(len(x['all_regimes']) for x in out),
 'seed3_selected':[row for row in out[6]['grid'] if row['epsilon'] in ['0','0.01','0.5','0.65','1']],
 'readout_controls_equal':all(row['order']=='equal' for r in out if r['condition']=='readout_only' for row in r['grid'])},indent=2))
