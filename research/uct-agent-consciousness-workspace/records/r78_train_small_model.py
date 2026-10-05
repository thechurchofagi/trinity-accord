"""R78: tiny trained model; finite-domain mechanism evidence, not phenomenology."""
import numpy as np
import json, hashlib, time, platform
from pathlib import Path

X=np.array([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])
S=X[:,0]*X[:,1]
Y=(S+1)/2
SAVE={0,1,10,100,500,1000,3000}

def unpack(p): return p[:4].reshape(2,2),p[4:6],p[6:8],p[8]
def forward(p):
 W,b,v,c=unpack(p)
 H=np.tanh(X@W.T+b)
 L=H@v+c
 return H,L
def loss_grad(p):
 H,L=forward(p)
 loss=np.logaddexp(0,-S*L).mean()
 prob=1/(1+np.exp(-L))
 dl=(prob-Y)/4
 W,b,v,c=unpack(p)
 da=dl[:,None]*v[None,:]*(1-H*H)
 grad=np.concatenate([(da.T@X).ravel(),da.sum(0),H.T@dl,np.array([dl.sum()])])
 return float(loss),grad
def measure(p):
 H,L=forward(p);W,b,v,c=unpack(p)
 dh=(S[:,None]*H).mean(0); d=float(np.mean(S*L))
 md=min(float(np.linalg.norm(H[i]-H[j])) for i in range(4) for j in range(i))
 loss=float(np.logaddexp(0,-S*L).mean())
 return {'loss':loss,'accuracy':float(np.mean((L>=0)==Y)),'min_margin':float(np.min(S*L)),
 'logit_interaction':d,'hidden_interactions':dh.tolist(),'weighted_hidden_interactions':(v*dh).tolist(),
 'decomposition_error':float(abs(d-v@dh)),
 'lower_bound':float(-np.log(np.expm1(loss))),'jensen_gap':float(loss-np.logaddexp(0,-d)),
 'hidden_min_pair_distance':md,'input1_effects_by_input2':(H[2:]-H[:2]).tolist(),
 'input2_effects_by_input1':(H[[1,3]]-H[[0,2]]).tolist(),
 'weights':p.tolist(),'hidden':H.tolist(),'logits':L.tolist()}
def initial(seed):
 rng=np.random.default_rng(seed)
 W=np.diag(rng.uniform(.5,1.5,2))
 return np.concatenate([W.ravel(),rng.uniform(-.5,.5,2),rng.normal(0,.2,2),[0.]])

start=time.time()
root=Path('r78_results');root.mkdir(exist_ok=True)
p=initial(0);_,g=loss_grad(p);eps=1e-6
num=[]
for i in range(9):
 e=np.eye(9)[i]*eps
 num.append((loss_grad(p+e)[0]-loss_grad(p-e)[0])/(2*eps))
ge=float(np.max(np.abs(g-num)))
assert ge<1e-7, ge
all_runs=[]
for seed in range(8):
 for condition in ['full','readout_only']:
  p=initial(seed);m=np.zeros(9);v2=np.zeros(9)
  mask=np.ones(9) if condition=='full' else np.array([0]*6+[1]*3)
  snapshots={'0':measure(p)};progress=[];prev=None;increases=0
  for step in range(3001):
   loss,grad=loss_grad(p)
   if prev is not None and loss>prev+1e-12: increases+=1
   prev=loss
   if step%100==0:
    z=measure(p);progress.append({'step':step,**{k:z[k] for k in ['loss','accuracy','logit_interaction','min_margin']}})
   if step in SAVE: snapshots[str(step)]=measure(p)
   if step==3000: break
   grad*=mask;m=.9*m+.1*grad;v2=.999*v2+.001*grad*grad
   p-=.03*(m/(1-.9**(step+1)))/(np.sqrt(v2/(1-.999**(step+1)))+1e-8)
  original=p.copy();cut=p.copy();cut[1]=cut[2]=0
  intervention={'uncut':measure(original),'cross_input_cut':measure(cut),'restored':measure(original.copy())}
  for z in snapshots.values():
   assert z['jensen_gap']>=-1e-12
   assert z['decomposition_error']<1e-12
  assert abs(intervention['cross_input_cut']['logit_interaction'])<1e-12
  assert intervention['restored']==intervention['uncut']
  if condition=='readout_only':
   assert all(z['loss']>=np.log(2)-1e-12 and abs(z['logit_interaction'])<1e-12 for z in snapshots.values())
  run={'seed':seed,'condition':condition,'checkpoints':snapshots,'progress':progress,
       'loss_increase_steps':increases,'interventions':intervention}
  fn=f'seed_{seed}_{condition}.json';(root/fn).write_text(json.dumps(run,indent=2)+'\n')
  z=snapshots['3000'];cutz=intervention['cross_input_cut']
  all_runs.append({'seed':seed,'condition':condition,'initial':snapshots['0'],
    'final':z,'cut':cutz,'loss_increase_steps':increases,'file':fn})

summary={'scope':'actual NumPy training of a tiny synthetic neural network; no language model or phenomenal data',
 'protocol_sha256':hashlib.sha256(Path('R78_Protocol_Frozen_20261005.md').read_bytes()).hexdigest(),
 'python':platform.python_version(),'numpy':np.__version__,'gradient_max_error':ge,
 'input_domain':X.tolist(),'targets':Y.tolist(),'train_evaluate_same_complete_domain':True,
 'parameter_count':9,'steps':3000,'runs':all_runs,'elapsed_seconds':time.time()-start}
(root/'R78_Summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'gradient_error':ge,'elapsed_seconds':summary['elapsed_seconds'],
 'runs':[{k:r[k] for k in ['seed','condition','loss_increase_steps']}|{'initial_accuracy':r['initial']['accuracy'],'loss':r['final']['loss'],'accuracy':r['final']['accuracy'],'d':r['final']['logit_interaction'],'cut_loss':r['cut']['loss'],'cut_accuracy':r['cut']['accuracy'],'min_hidden_distance':r['final']['hidden_min_pair_distance']} for r in all_runs]},indent=2))
