"""Radial binary monitor calibration; physical model, not a consciousness assay."""
from __future__ import annotations
import numpy as np

def body_variance(p,D,N,M,a=.2,b=2.,k=1.):
    return D/(a+b)+b/(a+b)*(D+k*k*(N*p*p+M))/(a+k*p)

def body_derivative(p,D,N,M,a=.2,b=2.,k=1.):
    return b*k/(a+b)*(N-(D+k*k*M+a*a*N)/(a+k*p)**2)

def optimum(D,N,M,a=.2,k=1.):
    return 1. if N==0 else min(1.,max(0.,(np.sqrt(a*a+(D+k*k*M)/N)-a)/k))

def exact_probabilities(Sigma,r,s,c=1.):
    """No-alarm probabilities: zero, reference energy c, body at gains r, 2r."""
    if r<=0 or not 0<s<=1 or c<=0: raise ValueError('Invalid calibration parameters')
    sig=np.asarray(Sigma,float)
    return np.array([s,s*np.exp(-r*c),s/np.sqrt(np.linalg.det(np.eye(2)+2*r*sig)),
                     s/np.sqrt(np.linalg.det(np.eye(2)+4*r*sig))])

def recover(q,c=1.):
    q0,qc,q1,q2=np.asarray(q,float)
    if min(q0,qc,q1,q2)<=0 or qc>=q0: return (float('nan'),)*3
    r=np.log(q0/qc)/c
    f1=(q0/q1)**2;f2=(q0/q2)**2
    tr=(4*f1-f2-3)/(4*r)
    det=(f2-2*f1+1)/(8*r*r)
    return r,tr,det

def score_interval(bounds,c=1.):
    """Conservative deterministic enclosure, conditional on four probability intervals.
    No IID claim is made here. Returns NaNs if the gain cannot be separated from zero.
    """
    lo,hi=np.asarray(bounds,float).T
    if np.min(lo)<=0 or lo[0]<=hi[1]:return (float('nan'),float('nan'))
    rlo=np.log(lo[0]/hi[1])/c;rhi=np.log(hi[0]/lo[1])/c
    f1lo=(lo[0]/hi[2])**2; f1hi=(hi[0]/lo[2])**2
    f2lo=(lo[0]/hi[3])**2; f2hi=(hi[0]/lo[3])**2
    nlo=4*f1lo-f2hi-3; nhi=4*f1hi-f2lo-3
    ends=[n/(4*r) for n in (nlo,nhi) for r in (rlo,rhi)]
    if max(ends)<0:
        return (float('nan'),float('nan'))  # inconsistent with a nonnegative body trace
    return max(0.,min(ends)), max(ends)

def joint_alarm_covariance(Sigma,Cross,r,s):
    # Different times with fresh independent monitor randomization.
    n=len(Sigma)
    joint=np.block([[Sigma,Cross],[Cross.T,Sigma]])
    p2=s*s/np.sqrt(np.linalg.det(np.eye(2*n)+2*r*joint))
    p1=s/np.sqrt(np.linalg.det(np.eye(n)+2*r*Sigma))
    return p2-p1*p1

def bounded_moment_interval(bounds,second_energy_moment,c=1.):
    """Only [zero,reference,body] intervals required; no Gaussian hypothesis.
    Assumes finite known upper bound E[energy^2] <= second_energy_moment.
    """
    lo,hi=np.asarray(bounds,float).T
    if np.min(lo)<=0 or lo[0]<=hi[1] or second_energy_moment<0:
        return (float('nan'),float('nan'))
    rlo=np.log(lo[0]/hi[1])/c;rhi=np.log(hi[0]/lo[1])/c
    ulo=max(0.,1-hi[2]/lo[0]);uhi=max(0.,1-lo[2]/hi[0])
    return ulo/rhi, uhi/rlo + rhi*second_energy_moment/2
