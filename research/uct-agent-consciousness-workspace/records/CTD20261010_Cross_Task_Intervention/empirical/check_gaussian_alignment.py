from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit, linear_sum_assignment

BASE=Path(__file__).resolve().parent
raw=pd.read_excel(BASE/'Experiment_3.xlsx',header=None)
counts=raw.iloc[3:,1:43].to_numpy(dtype=float).reshape(30,2,3,7)
published=raw.iloc[3:,63:69].to_numpy(dtype=float).reshape(30,2,3)
x=np.array([-400,-200,-100,0,100,200,400],dtype=float)
def gauss(x,a,mu,sd):
    return a*np.exp(-.5*((x-mu)/sd)**2)
fitted=np.zeros((30,2,3))
for i in range(30):
    for t in range(2):
        for f in range(3):
            p,_=curve_fit(gauss,x,counts[i,t,f]/10,p0=[1,0,200],bounds=([0,-500,1],[2,500,2000]),maxfev=4000)
            fitted[i,t,f]=p[2]
print('Published means',published.mean(axis=0))
print('Reconstructed means',fitted.mean(axis=0))
print('Same row Pearson correlations',np.array([np.corrcoef(fitted[:,t,f],published[:,t,f])[0,1] for t in range(2) for f in range(3)]))
print('First participant published',published[0].tolist(),'reconstructed',fitted[0].tolist())
# Diagnostic matching only. Never use this assignment to repair participant identity.
dist=((fitted[:,None]-published[None,:])**2).sum(axis=(2,3))
r,c=linear_sum_assignment(dist)
print('Diagnostic assignment',list(zip(r.tolist(),c.tolist())), 'RMSE',np.sqrt(dist[r,c].sum()/180))
np.savez(BASE/'alignment_diagnostic.npz',counts=counts,published=published,reconstructed=fitted,x=x)
