"""Exploratory post-training geometric certificates; no additional training."""
import json
import numpy as np
from pathlib import Path
s=json.loads(Path('r78_results/R78_Summary.json').read_text())
out=[]
for r in s['runs']:
 if r['condition']!='full': continue
 z=r['final'];h=np.array(z['hidden']);v=np.array(z['weights'][6:8])
 dist,i,j=min((float(np.linalg.norm(h[i]-h[j])),i,j) for i in range(4) for j in range(i))
 radius=z['min_margin']/float(np.linalg.norm(v))
 upper=min(radius,r['initial']['hidden_min_pair_distance']/2)
 out.append({'seed':r['seed'],'nearest_pair_indices':[i,j],
 'nearest_pair_targets':[s['targets'][i],s['targets'][j]],'v_norm':float(np.linalg.norm(v)),
 'old_input_reconstruction_radius':r['initial']['hidden_min_pair_distance']/2,
 'new_input_obstruction_radius':dist/2,'new_target_margin_radius':radius,
 'coexistence_epsilon_interval':[dist/2,upper] if dist/2<upper else None})
d={'status':'exploratory analytic follow-up chosen after the frozen training experiment; no rerun or new training',
 'noise_model':'additive Euclidean perturbation of the two recorded tanh activations, bounded by epsilon; no physical or phenomenal calibration claimed','cases':out}
Path('r78_results/R78_Exploratory_Robustness_Certificate.json').write_text(json.dumps(d,indent=2)+'\n')
