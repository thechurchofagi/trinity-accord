#!/usr/bin/env python3
"""Exact finite pressure for the prescribed coherent secondary refinement.
No uniform lower bound is inferred from this finite family.
"""
import json
from pathlib import Path
from verify_gray_reflection_graph import order_and_scores,counts,gray,graph,optimize
rows=[]
for k in (2,3):
    for n in (6,8,10,12,14,16,18):
        a=list(range(1,n+1)) if k==2 else [1,2]+[3*j-2 for j in range(2,n)]
        w=[(1<<n)*v+(1<<j) for j,v in enumerate(a)]
        p=order_and_scores(w)[0]
        R,C,_=counts(tuple(map(gray,p)))
        g=graph(p,n)
        E,phi=optimize(g,n)
        minimum=((1<<n)+g['D']-E)//2
        assert min(range(n),key=w.__getitem__)==0
        rows.append({'k':k,'n':n,'positive_R':R,'positive_C':C,
                     'minimum_over_all_sign_reflections_R_and_C':minimum,
                     'D':g['D'],'W':g['W'],'E':E,'frustration':phi,
                     'signed_minimum_density':minimum/(1<<n)})
        print(json.dumps(rows[-1]),flush=True)
Path(__file__).with_name('coherent_bucket_refinement_receipt.json').write_text(
    json.dumps({'status':'PASS','rows':rows,'scope':'Fourteen specified vectors; no chamber coverage or asymptotic theorem claimed.'},indent=2)+'\n')
