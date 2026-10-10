#!/usr/bin/env python3
"""Exact topology figure; no simulated measurements or generated imagery."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent / 'figures'
OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'svg.fonttype': 'none'})
fig, axes = plt.subplots(1, 2, figsize=(9.1, 4.6))
ink, route, fill, accent = '#1a3046', '#2d7f83', '#f1f6f8', '#aa4b25'

def box(ax, x, y, label, width=0.36, height=0.115, color=ink):
    ax.add_patch(FancyBboxPatch((x-width/2,y-height/2),width,height,
                 boxstyle='round,pad=0.008,rounding_size=0.012',
                 edgecolor=color,facecolor=fill,linewidth=1.2))
    ax.text(x,y,label,ha='center',va='center',color=ink,fontsize=10)

def arrow(ax, start, end):
    ax.annotate('',xy=end,xytext=start,
                arrowprops={'arrowstyle':'-|>','color':route,'lw':1.5})

for ax in axes:
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    box(ax,.5,.81,'Root source s₀',.48)
    box(ax,.24,.38,'Actuator',.34)
    box(ax,.76,.38,'Predictor',.34)

axes[0].text(.5,.965,'A  Shared relay occurrence',ha='center',weight='bold',color=ink)
box(axes[0],.5,.61,'Relay r',.36,color=accent)
arrow(axes[0],(.5,.747),(.5,.675))
arrow(axes[0],(.43,.55),(.24,.445))
arrow(axes[0],(.57,.55),(.76,.445))
axes[0].text(.5,.22,'Write 1 to r before both reads',ha='center',color=accent)
axes[0].text(.5,.155,'Actuation = 1   ·   Prediction = 1',ha='center',color=ink)

axes[1].text(.5,.965,'B  Separate relay occurrences',ha='center',weight='bold',color=ink)
box(axes[1],.24,.61,'Relay rA',.34)
box(axes[1],.76,.61,'Relay rP',.34,color=accent)
arrow(axes[1],(.43,.748),(.24,.675))
arrow(axes[1],(.57,.748),(.76,.675))
arrow(axes[1],(.24,.55),(.24,.445))
arrow(axes[1],(.76,.55),(.76,.445))
axes[1].text(.5,.22,'Write 1 only to rP before its read',ha='center',color=accent)
axes[1].text(.5,.155,'Actuation = 0   ·   Prediction = 1',ha='center',color=ink)

fig.text(.5,.055,'Both installations agree under every root-source assignment.\n'
         'Shown carrier-write controls start with s₀ = 0; no later overwrite or compensation.',
         ha='center',va='center',fontsize=10,color=ink,linespacing=1.5)
fig.subplots_adjust(left=.025,right=.975,top=.96,bottom=.13,wspace=.17)
fig.savefig(OUT/'source_resolution.png',dpi=300,facecolor='white')
fig.savefig(OUT/'source_resolution.svg',facecolor='white')
plt.close(fig)
