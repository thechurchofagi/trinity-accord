#!/usr/bin/env python3
"""Fixed-n association/sensitivity calculator; warrants are asserted, not certified."""
import argparse,json,math
from pathlib import Path
REQUIRED=('signed_endpoint','residual_budget','ignorable_complete_audit','same_actual_instance_use')
def analyze(counts,kappa,alpha=0.05,warrants=None):
    if len(counts)!=4 or any(type(x)!=int or x<0 for x in counts) or sum(counts)<=0:raise ValueError('Four nonnegative integer counts required')
    if not 0<alpha<1 or not 0<=kappa<=0.25:raise ValueError('Invalid alpha or residual budget')
    n=sum(counts);m=(counts[2]+counts[3])/n;j=(counts[1]+counts[3])/n;r=counts[3]/n
    h=math.sqrt(math.log(6/alpha)/(2*n));lo=r-h-min(1,m+h)*min(1,j+h);hi=min(1,r+h)-max(0,m-h)*max(0,j-h)
    lo=max(0,r-h)-min(1,m+h)*min(1,j+h)
    asserted=all((warrants or {}).get(x,{}).get('asserted') is True and (warrants or {}).get(x,{}).get('evidence') for x in REQUIRED)
    direction='POSITIVE_CONDITIONAL_IN_V' if lo>kappa else 'NEGATIVE_CONDITIONAL_IN_V' if hi<-kappa else 'ABSTAIN'
    return dict(n=n,alpha=alpha,m=m,j=j,r=r,covariance=r-m*j,covariance_interval=[lo,hi],kappa=kappa,
       positive_budget_capacity=max(0,lo),hypothetical_direction=direction,
       status=direction if asserted else 'OBSERVABLE_ASSOCIATION_ONLY',external_warrants_asserted=asserted,
       conditional_positive_delta_lower_bound=4*(lo-kappa) if asserted and lo>kappa else None,
       scope='Fixed reporting V; no H endpoint validation, actual-use proof or V-to-T inference by this script')
def main():
    p=argparse.ArgumentParser();p.add_argument('--counts',type=int,nargs=4,required=True);p.add_argument('--n',type=int);p.add_argument('--kappa',type=float,required=True);p.add_argument('--alpha',type=float,default=.05);p.add_argument('--warrants',type=Path)
    a=p.parse_args()
    if a.n is not None and a.n!=sum(a.counts):p.error('n differs from counts total')
    print(json.dumps(analyze(a.counts,a.kappa,a.alpha,json.loads(a.warrants.read_text()) if a.warrants else None),indent=2))
if __name__=='__main__':main()
