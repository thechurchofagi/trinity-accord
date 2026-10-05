#!/usr/bin/env python3
"""Fixed R93 software interventions; no training and no model API calls."""
from pathlib import Path
import json,hashlib
import numpy as np
P=Path(__file__).resolve().parent
data=json.loads((P/'R93_Inputs.json').read_text())
X=np.array(data['test']); c=float(np.mean(X[:,0]**2));den=float(np.mean(np.sum(X*X,axis=1)))
sigma=.01
pulses=np.concatenate([np.sqrt(2)*sigma*np.eye(2),-np.sqrt(2)*sigma*np.eye(2)])

def run(p,noise):
 h=X@p['E'].T
 h=h@p['A'].T
 h=h[:,None,:]+noise[None,:,:]
 h=h@p['A'].T;h=h@p['A'].T
 return h@p['B'].T

rows=[];raw=[];checks=[]
for rr in data['runs']:
 for cp in rr['checkpoints']:
  p={k:np.array(v) for k,v in cp['parameters'].items()}
  M=p['A']@p['E'];D=p['B']@p['A']@p['A'];F=D@M
  C=c*M@M.T;power=np.trace(C)
  clean=run(p,np.zeros((1,2)))[:,0,:]
  base=run(p,pulses)
  baseN=np.mean(np.sum((base-X[:,None,:])**2,axis=2))/den
  N=np.mean(np.sum((clean-X)**2,axis=1))/den
  for r in [.25,1.,4.]:
   shape=np.diag([r,1.]);T=shape*np.sqrt(power/np.trace(shape@C@shape.T));Ti=np.linalg.inv(T)
   q={'E':T@p['E'],'A':T@p['A']@Ti,'B':p['B']@Ti}
   Dq=q['B']@q['A']@q['A']
   y0=run(q,np.zeros((1,2)))[:,0,:];yf=run(q,pulses);yt=run(q,pulses@T.T)
   fixedN=float(np.mean(np.sum((yf-X[:,None,:])**2,axis=2))/den)
   transportedN=float(np.mean(np.sum((yt-X[:,None,:])**2,axis=2))/den)
   pred=float(N+sigma*sigma*np.sum(Dq**2)/den)
   power2=float(np.mean(np.sum((X@q['E'].T@q['A'].T)**2,axis=1)))
   row={'run':rr['run'],'step':cp['step'],'shape':r,'clean_N':float(N),'fixed_noise_N':fixedN,'transported_noise_N':transportedN,'baseline_noise_N':float(baseN),'noise_excess':float(sigma*sigma*np.sum(Dq**2)/den),'gain_norm':float(np.linalg.norm(Dq,2)),'state_power':power2,'clean_discrepancy':float(np.max(np.abs(y0-clean))),'transport_discrepancy':float(np.max(np.abs(yt-base))),'formula_discrepancy':float(abs(pred-fixedN)),'power_discrepancy':float(abs(power-power2))}
   checks.append(row['clean_discrepancy']<1e-10 and row['transport_discrepancy']<1e-10 and row['formula_discrepancy']<1e-10*max(1,pred) and row['power_discrepancy']<1e-10*max(1,power))
   rows.append(row);raw.append({'run':rr['run'],'step':cp['step'],'shape':r,'T':T.tolist(),'parameters':{k:v.tolist() for k,v in q.items()},'clean':y0.tolist(),'fixed_pulse_outputs':yf.tolist(),'transported_pulse_outputs':yt.tolist()})

witness=[]
for eps in [1.,.1]:
 M=np.diag([eps,np.sqrt(2-eps*eps)]);D=np.linalg.inv(M)
 p={'E':M,'A':np.eye(2),'B':D}
 y=run(p,pulses);N=float(np.mean(np.sum((y-X[:,None,:])**2,axis=2))/den)
 witness.append({'epsilon':eps,'state_power':float(c*np.sum(M*M)),'noise_N':N,'analytic_N':float(sigma*sigma*np.sum(D*D)/den),'gain_norm':float(np.linalg.norm(D,2)),'M':M.tolist(),'D':D.tolist(),'clean_F':(D@M).tolist(),'all_pulse_outputs':y.tolist()})
out={'input_sha256':hashlib.sha256((P/'R93_Inputs.json').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((P/'R93_Protocol_20261006.md').read_bytes()).hexdigest(),'numpy':np.__version__,'sigma':sigma,'input_covariance_diagonal':c,'pulses':pulses.tolist(),'rows':rows,'witness':witness,'all_48_checks_pass':all(checks),'scope':'software intervention replay of existing learned checkpoints; constructed witness pair; no training, hardware or subjective measurement'}
(P/'R93_Results.json').write_text(json.dumps(out,indent=2)+'\n')
(P/'R93_All_Pulse_Outputs.json').write_text(json.dumps(raw,separators=(',',':'))+'\n')
print('Checks',sum(checks),'/',len(checks))
print('Constructed matched-power pair:',[{k:v for k,v in w.items() if k not in ['all_pulse_outputs','M','D','clean_F']} for w in witness])
print('Noise error ratio:',witness[1]['noise_N']/witness[0]['noise_N'])
for rr in data['runs']:
 s=[r for r in rows if r['run']==rr['run'] and r['step']==3000]
 print(rr['run'],'cleanN',s[0]['clean_N'],'fixed noise N',[r['fixed_noise_N'] for r in s])
print('Maximum discrepancies:',{k:max(r[k] for r in rows) for k in ['clean_discrepancy','transport_discrepancy','formula_discrepancy','power_discrepancy']})
assert all(checks)
