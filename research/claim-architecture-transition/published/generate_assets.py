#!/usr/bin/env python3
from pathlib import Path
import csv
import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
A = np.logspace(-1, 3, 500)
Z=R=L=K=1.0
beta=0.35
B=0.40
q=0.70
Y = Z*(R**beta)*((L+A*K)**(1-beta))
w = Z*(1-beta)*(R**beta)*((L+A*K)**(-beta))
labor_share = (1-beta)*L/(L+A*K)
coverage = w/B
gap = q*np.maximum(B-w,0.0)
gap_share = gap/Y

with (ROOT/'illustrative_series.csv').open('w', newline='', encoding='utf-8') as f:
    wr=csv.writer(f)
    wr.writerow(['A','Y','w','labor_share','labor_only_claim_coverage','aggregate_gap','gap_share'])
    for row in zip(A,Y,w,labor_share,coverage,gap,gap_share):
        wr.writerow([f'{float(x):.12g}' for x in row])

i1 = int(np.argmin(np.abs(A-1.0)))
fig, ax = plt.subplots(figsize=(8.0,4.7))
ax.loglog(A, Y/Y[i1], label='Output Y (normalized at A=1)')
ax.loglog(A, w/w[i1], label='Human wage w (normalized at A=1)')
ax.set_xlabel('AI productivity A')
ax.set_ylabel('Normalized level')
ax.set_title('Illustrative benchmark: output abundance can coexist with wage decline')
ax.grid(True, which='both', alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(ROOT/'figure1_output_wage.png', dpi=180)
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.0,4.7))
ax.loglog(A, coverage, label='Labor-only basic-claim coverage χ_L = w/B')
ax.loglog(A, np.maximum(gap_share,1e-12), label='Aggregate basic gap / output')
ax.axhline(1.0, linewidth=1.0, linestyle='--', label='Basic-claim threshold')
ax.set_xlabel('AI productivity A')
ax.set_ylabel('Level / share')
ax.set_title('Illustrative benchmark: exclusion and aggregate feasibility can diverge')
ax.grid(True, which='both', alpha=0.25)
ax.legend()
fig.tight_layout()
fig.savefig(ROOT/'figure2_claim_gap.png', dpi=180)
plt.close(fig)
print('generated assets')
