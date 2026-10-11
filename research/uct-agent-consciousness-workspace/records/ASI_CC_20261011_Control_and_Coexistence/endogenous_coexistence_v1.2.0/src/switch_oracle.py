#!/usr/bin/env python3
"""Independent exhaustive finite-arrival oracle; no import of switch_frontier.
Every admissible sequence in a finite horizon is enumerated, not only an assumed
maximizer. The proof establishes why the global peak occurs by ell-1 or initially.
"""
import argparse,itertools,json
from pathlib import Path


def main(out):
    profiles=0;streams=0;fail=[]
    for q in range(4):
      for old in itertools.combinations_with_replacement(range(4),q):
       for b in (1,2):
        for rho in range(b+1):
         for mu in range(rho,3):
          for ell in range(1,4):
           max_debt=q;witness=None
           for a in itertools.product(range(b+1),repeat=4):
            if any(sum(a[i:j])>b+rho*(j-i-1) for i in range(4) for j in range(i+1,5)):continue
            jobs=list(old);peak=q
            for t,arrivals in enumerate(a):
             for _ in range(mu):
              eligible=[(v,i) for i,v in enumerate(jobs) if v<=t]
              if not eligible:break
              _,i=min(eligible);jobs.pop(i)
             jobs.extend([t+ell]*arrivals)
             peak=max(peak,len(jobs))
            if peak>max_debt:max_debt=peak;witness=a
            streams+=1
           L=[sum(v<=t for v in old) for t in range(ell)]
           prediction=max(q,q+b-mu,*[q-L[t]+b+rho*t for t in range(ell)])
           assert max_debt==prediction,(old,b,rho,mu,ell,max_debt,prediction,witness)
           profiles+=1
    r={'version':'ASI-CC-v1.2.0','method':'all conforming length4 streams; explicit per-job eligibility and service; no theorem module import','profiles':profiles,'streams':streams,'max_ell':3,'all_maxima_equal_switch_theorem':True,'assertions':'PASS'}
    Path(out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='oracle_results.json');main(p.parse_args().out)
