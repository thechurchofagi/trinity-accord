#!/usr/bin/env python3
"""Finite exhaustive controls for R187 / CMA-RESULT-v0.1.0.
All examples are classical automata, not consciousness measurements.
"""
from itertools import product
from fractions import Fraction as F
from math import isclose, sqrt
import json
from pathlib import Path
import sympy as sp

runs=histories=selective=rank_cases=noise_checks=countercontrols=0

def shared_hist(initial,word,width):
    s=initial
    trace=[(s,)*width]
    for c in word:
        s^=c
        trace.append((s,)*width)
    return tuple(trace)

def copies_hist(initial,word,width):
    bits=[initial]*width
    trace=[tuple(bits)]
    for c in word:
        bits=[a^c for a in bits]
        trace.append(tuple(bits))
    return tuple(trace)

# All open-loop common-mode words length<=9 for four distinct n-copy realizations.
# Under proven bisimulation, this also entails adaptive transcript indistinguishability,
# but this executable enumerator is NOT an exhaustive enumeration of policies.
for n in (2,3,4,5):
    for initial in (0,1):
        for ell in range(10):
            for word in product((0,1),repeat=ell):
                histories+=1
                assert shared_hist(initial,word,n)==copies_hist(initial,word,n)
                runs+=1
assert histories==4*2*(2**10-1)

# Physical constituent write while external synchronizer is disabled:
# two copies can take an off-diagonal state; a *restricted* single-bit shared
# source with two faithful readouts cannot. The latter has no matching constituent-
# specific physical intervention, so this is NOT an interface-equivalent test.
for x in (0,1):
    copied=[x,x]
    copied[0]^=1
    assert copied[0]!=copied[1]
    assert not any((t,t)==tuple(copied) for t in (0,1))
    selective+=1
    # Active synchronizer can erase observable divergence prior to sample.
    synced=copied.copy();synced[1]=synced[0]
    assert synced[0]==synced[1]
    countercontrols+=1
    # A shared source with a left-edge readout modifier produces the same immediate
    # output pair, without making two source occurrences. Interface semantics matter.
    edge_readout=(x^1,x)
    assert edge_readout==tuple(copied)
    countercontrols+=1

# Differing rank is about independently writable state coordinates under
# stipulated primitive ports, NOT occurrence count or experiential subjects.
for n in range(2,8):
    common=sp.ones(n,1)
    individually=sp.eye(n)
    assert common.rank()==1 and individually.rank()==n
    # Restrict independent controls to the diagonal control subspace: identical map.
    assert individually*common==common
    rank_cases+=1

# Sharp geometrical distance from differential response to common-mode line.
# squared residual should be delta^2 /2 for an unmeasured common baseline t.
for delta in (F(-4),F(-3,2),F(-1),F(-1,5),F(0),F(1,3),F(1),F(2),F(7,2)):
    for s in (F(-3),F(0),F(3,2)):
        y=sp.Matrix([sp.Rational(s+delta),sp.Rational(s)])
        B=sp.ones(2,1)
        projector=B*(B.T*B).inv()*B.T
        e=(sp.eye(2)-projector)*y
        sq=(e.T*e)[0]
        assert sq==sp.Rational(delta*delta/2)
        assert (B.T*e)[0]==0
        noise_checks+=1
        # Two-sided bounded readout noise gives disjoint closed balls only if gap>2eps.
        for eps in (F(0),F(1,8),F(1,4),F(1,2),F(1)):
            assert bool(sq>4*sp.Rational(eps*eps))==bool(abs(delta)>2*sqrt(2)*float(eps)+1e-12) if delta else sq==0
            noise_checks+=1

# Explicit underidentification: m copies driven only diagonally retain m distinct
# state-locus IDs but the exact same accessible trace as one common-locus source.
# Opposite counterexample: one physical occurrence may carry a 2-bit state with
# two independently writable *internal* coordinates. Rank does not count occurrences.
for a,b in product((0,1),repeat=2):
    one_occurrence_multibit=(a,b)
    after1=(a^1,b);after2=(a,b^1)
    assert after1!=one_occurrence_multibit and after2!=one_occurrence_multibit
    countercontrols+=1

out={"research_id":"R187-20261009","result_version":"CMA-RESULT-v0.1.0",
 "outcome":"PASS","common_protocol_complete_histories":histories,
 "copy_widths":[2,3,4,5],"max_word_length":9,
 "selective_write_witnesses":selective,
 "synchronizer_and_edge_controls":countercontrols,
 "accessibility_rank_cases":rank_cases,
 "exact_noise_geometry_checks":noise_checks,
 "claims_not_tested":["actual physical occurrence identity","C1/U1/P3 truth","phenomenal content","unique self","genuine physical isolation"],
 "scope":"Finite deterministic common-mode automata and exact linear 2-output toy geometry; adaptive-policy impossibility follows the stated mathematical bisimulation lemma, not an exhaustive policy enumeration."}
(Path(__file__).parent/'TEST_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

# Appendix: exact stochastic near-equivalence example.
# Model S reports 0 on every trial, while C independently glitches to 1
# with probability delta. Under equal priors the best test detects C on
# observing >=1 glitch; if none appear, posterior remains ambiguous.
# The exact pairwise TV is 1-(1-delta)^T; binary Bayes error=(1-delta)^T/2.
from math import comb
stochastic=0
for delta in (F(0),F(1,32),F(1,16),F(1,8),F(1,4),F(1,2)):
    for T in range(0,13):
        copy_probs={k:F(comb(T,k))*delta**k*(1-delta)**(T-k) for k in range(T+1)}
        shared_probs={k:F(1) if k==0 else F(0) for k in range(T+1)}
        tv=sum(abs(copy_probs[k]-shared_probs[k]) for k in range(T+1))/2
        assert tv==1-(1-delta)**T
        bayes=(1-tv)/2
        assert bayes==(1-delta)**T/2
        assert tv<=min(F(1),T*delta)
        stochastic+=1
out['stochastic_exact_tv_cases']=stochastic
out['stochastic_bayes_error_T_12_delta_1_8']=str((1-F(1,8))**12/2)
(Path(__file__).parent/'TEST_RESULTS.json').write_text(json.dumps(out,indent=2)+'\n')
print('STOCHASTIC_PASS',stochastic,'example_error',out['stochastic_bayes_error_T_12_delta_1_8'])
