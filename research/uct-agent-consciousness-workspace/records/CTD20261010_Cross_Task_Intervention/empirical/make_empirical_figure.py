from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parent
OUT=BASE/'results'
d=pd.read_csv(OUT/'published_tbw_individual_diagnostics.csv')
dist=pd.read_csv(OUT/'individual_clock_and_monotone_distances.csv')
summary=json.loads((OUT/'count_model_summary.json').read_text())
boot=np.load(OUT/'count_model_bootstrap.npz')['lrt']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.titlesize':11,'axes.titleweight':'bold',
                     'pdf.fonttype':42,'svg.fonttype':'none'})
fig,axes=plt.subplots(1,3,figsize=(12.6,4.1),gridspec_kw={'width_ratios':[1,1.1,1]})
ax=axes[0]
x=d.log_gain_simultaneity_8v13.to_numpy();y=d.log_gain_ownership_8v13.to_numpy()
lo=min(x.min(),y.min())-.08;hi=max(x.max(),y.max())+.08
ax.plot([lo,hi],[lo,hi],color='#718096',lw=1.1,ls='--',label='Equal proportional gain')
ax.scatter(x,y,s=31,color='#176C87',edgecolor='white',lw=.5,zorder=3)
ax.set(xlim=(lo,hi),ylim=(lo,hi),xlabel='Simultaneity: log(W8 / W13)',ylabel='Ownership: log(W8 / W13)')
ax.set_aspect('equal',adjustable='box');ax.set_title('A  Released participant estimates',loc='left')
ax.legend(frameon=False,fontsize=8,loc='lower right')
ax.grid(alpha=.15)
ax=axes[1]
o=np.argsort(dist.epsilon_clock_log.to_numpy())
xx=np.arange(1,31)
ax.plot(xx,dist.clock_upward_tolerance_percent.to_numpy()[o],'-o',ms=3.4,lw=1.1,color='#754A9A',label='Proportional model')
ax.plot(xx,dist.monotone_upward_tolerance_percent.to_numpy()[o],'-s',ms=3.4,lw=.9,color='#07847C',label='Common monotone order')
ax.set(xlabel='Participant rank by proportional distance',ylabel='Minimum upward tolerance (%)',ylim=(-.35,14))
ax.set_title('B  Exact distances of point estimates',loc='left')
ax.legend(frameon=False,fontsize=8,loc='upper left');ax.grid(axis='y',alpha=.15)
ax=axes[2]
ax.hist(boot,bins=18,color='#BEDCE4',edgecolor='white')
stat=summary['test_statistic']
ax.axvline(stat,color='#AD4C2B',lw=1.8,label=f'Observed LR = {stat:.2f}')
ax.set(xlabel='Likelihood-ratio statistic',ylabel='Bootstrap replicates')
ax.set_title('C  Independent count-model bootstrap',loc='left')
ax.legend(frameon=False,fontsize=8,loc='upper left')
ax.text(.98,.87,f"p = {summary['parametric_bootstrap']['p_plus_one']:.3f}\n199 model-based replicates",ha='right',va='top',transform=ax.transAxes,fontsize=9)
fig.text(.01,.01,"Secondary analysis of author-released human data: D'Angelo et al. (2026), DOI 10.1038/s41467-025-67657-w.",fontsize=8,color='#52616B')
fig.tight_layout(rect=(0,.06,1,1),w_pad=2.1)
for ext in ['png','pdf','svg']:fig.savefig(OUT/f'empirical_shared_scale.{ext}',dpi=200,bbox_inches='tight')
print('Saved empirical_shared_scale in PNG, PDF, SVG formats.')
