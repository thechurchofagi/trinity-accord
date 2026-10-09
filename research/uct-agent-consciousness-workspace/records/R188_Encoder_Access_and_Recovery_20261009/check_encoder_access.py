#!/usr/bin/env python3
"""Exact finite checks for R188. Standard-library only; no experience measurement."""
from __future__ import annotations
import argparse, hashlib, itertools, json, platform, random, time
from fractions import Fraction as F
from pathlib import Path

GRAPHS = {
    'bipartite': [(a,b) for a in range(3) for b in range(3,6)],
    'prism': [(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(0,3),(1,4),(2,5)]
}

def law_uniform(edges):
    return [(e, F(1,2*len(edges)), F(1,2*len(edges))) for e in edges]

def posterior_score(law, responses, selector):
    # Directly construct observed (context, feedback, reply) cells.
    cells = {}
    for i, ((a,b), pa,pb) in enumerate(law):
        j = selector[i]
        for t, mass in ((a,pa),(b,pb)):
            key=(i,j,responses[j][t])
            cell=cells.setdefault(key,{})
            cell[t]=cell.get(t,F(0))+mass
    return sum((max(cell.values()) for cell in cells.values()),F(0))

def direct_protocol_optimum(law, n, K, L):
    # Enumerate every source reply table AND every feedback selector.
    # Decoder optimization is direct posterior maximization, not graph cuts.
    best=F(-1); count=0
    selectors=list(itertools.product(range(L),repeat=len(law)))
    source_tables=list(itertools.product(range(K),repeat=n))
    for replies in itertools.product(source_tables,repeat=L):
        for selector in selectors:
            count+=1
            s=posterior_score(law,replies,selector)
            if s>best: best=s
    return best,count

def cut_optimum(law, n, C):
    C=min(n,C)
    best=F(-1); winner=None; count=0
    for colors in itertools.product(range(C),repeat=n):
        count+=1
        error=sum((min(pa,pb) for ((a,b),pa,pb) in law if colors[a]==colors[b]),F(0))
        score=1-error
        if score>best: best,winner=score,colors
    return best,winner,count

def digits(v,K,L):
    return tuple((v//(K**i))%K for i in range(L))

def construct(law, colors, K, L):
    vectors=[digits(v,K,L) for v in colors]
    responses=tuple(tuple(v[j] for v in vectors) for j in range(L))
    selector=tuple(next((j for j in range(L) if vectors[a][j]!=vectors[b][j]),0)
                   for ((a,b),_,_) in law)
    return responses,selector

def matrix_marginals(edges):
    neighbors={t:sorted({b if a==t else a for a,b in edges if t in (a,b)}) for t in range(6)}
    target=[F(0)]*6; context={tuple(sorted(e)):F(0) for e in edges}; pairs={}
    for t,j in itertools.product(range(6),range(3)):
        e=tuple(sorted((t,neighbors[t][j])))
        target[t]+=F(1,18); context[e]+=F(1,18)
        pairs[(t,e)]=pairs.get((t,e),F(0))+F(1,18)
    assert set(target)=={F(1,6)}
    assert set(context.values())=={F(1,9)}
    assert all(pairs[t,e]/context[e]==F(1,2) for t,e in pairs)
    return {'targets':[str(x) for x in target], 'contexts':[str(x) for x in context.values()],
            'conditional_endpoint_probability':'1/2','conditional_entropy_bits':1,
            'external_stimuli':18,'neighbor_map':neighbors}

def run(output):
    started=time.perf_counter(); records=[]; table_count=0
    for name,edges in GRAPHS.items():
        law=law_uniform(edges)
        records.append({'check':'common_external_input_law','graph':name,'result':matrix_marginals(edges)})
        for K,L,expected in [(1,1,F(1,2)),(2,1,F(1) if name=='bipartite' else F(8,9)),
                             (2,2,F(1)),(3,1,F(1))]:
            best,colors,count=cut_optimum(law,6,K**L); table_count+=count
            responses,selector=construct(law,colors,K,L)
            actual=posterior_score(law,responses,selector)
            assert best==expected==actual,(name,K,L,best,actual)
            records.append({'check':'exact_optimum_and_constructive_attainment','graph':name,
                            'forward_symbols':K,'feedback_labels':L,'accuracy':str(best),
                            'enumerated_colorings':count,'colors':colors,
                            'responses':responses,'selector':selector})
        # Direct all-policy computation of the no-feedback value on 64 codes.
        direct,count=direct_protocol_optimum(law,6,2,1);table_count+=count
        assert direct==(F(1) if name=='bipartite' else F(8,9))
        records.append({'check':'independent_no_feedback_table_enumeration','graph':name,
                        'accuracy':str(direct),'encoder_selector_tables':count})
    # Independently exhaust the FULL interactive protocol on three-state examples.
    triangle=[(0,1),(1,2),(0,2)]
    rng=random.Random(20261009)
    laws=[law_uniform(triangle)]
    for _ in range(4):
        masses=[rng.randint(1,11) for i in range(6)];total=sum(masses)
        laws.append([(e,F(masses[2*i],total),F(masses[2*i+1],total)) for i,e in enumerate(triangle)])
    for number,law in enumerate(laws):
        for K,L in [(1,2),(2,1),(2,2)]:
            direct,count=direct_protocol_optimum(law,3,K,L);table_count+=count
            theory,colors,ncolor=cut_optimum(law,3,K**L);table_count+=ncolor
            assert direct==theory
            records.append({'check':'weighted_complete_protocol_vs_cut','law':number,
                            'forward_symbols':K,'feedback_labels':L,'accuracy':str(direct),
                            'encoder_selector_tables':count,'colorings':ncolor,
                            'endpoint_masses':[[str(pa),str(pb)] for _,pa,pb in law]})
    # Complete-graph closed form, with exact rational arithmetic.
    for n in range(2,8):
        edges=list(itertools.combinations(range(n),2))
        for C in range(1,min(4,n)+1):
            best,colors,count=cut_optimum(law_uniform(edges),n,C);table_count+=count
            q,r=divmod(n,C)
            closed=1-F(r*(q+1)*q+(C-r)*q*(q-1),2*n*(n-1))
            assert best==closed
            records.append({'check':'complete_graph_balanced_formula','n':n,'effective_colors':C,
                            'accuracy':str(best),'colorings':count})
    # Access control is logically indispensable: a source granted the full pair
    # sends the endpoint index and beats the blind prism optimum.
    leak_correct=0
    for e in GRAPHS['prism']:
        for t in e:
            reply=e.index(t)  # illegitimate X access under blind protocol
            leak_correct+=int(e[reply]==t)
    assert leak_correct==18
    records.append({'check':'deliberate_context_access_countercontrol','accuracy':'1',
                    'status':'OUTSIDE_BLIND_CONTRACT','reason':'encoder receives context'})
    # Classical matrix block-code countercontrol: a one-use obstruction need not
    # survive altered batching and deadline rules.
    def mat(b):return (b[1],b[0]^b[1])
    def xor(a,b):return tuple(x^y for x,y in zip(a,b))
    vals=list(itertools.product((0,1),repeat=2));examples=[]
    for a,b in itertools.product(vals,repeat=2):
        w=xor(a,mat(b))
        for role,side in [('A',a),('B',b),('AxorB',xor(a,b))]:
            matches=[(aa,bb) for aa,bb in itertools.product(vals,repeat=2)
                     if xor(aa,mat(bb))==w and {'A':aa,'B':bb,'AxorB':xor(aa,bb)}[role]==side]
            assert matches==[(a,b)]
            examples.append((a,b,role))
    records.append({'check':'block_coding_countercontrol','decoded_cases':len(examples),
                    'status':'DIFFERENT_PROTOCOL_NOT_REFUTATION',
                    'common_side_information_role_across_coordinates':True,
                    'note':'a two-coordinate block with one common reader role; not iid varying roles'})
    # A mixed side-information role is a different block law and this code fails.
    aa0,bb0=(0,0),(0,0)
    aa1,bb1=(0,1),(1,0)
    assert (aa0,bb0)!=(aa1,bb1)
    assert xor(aa0,mat(bb0))==xor(aa1,mat(bb1))==(0,0)
    assert (aa0[0],bb0[1])==(aa1[0],bb1[1])==(0,0)
    records.append({'check':'mixed_block_role_counterexample',
                    'sources':[[aa0,bb0],[aa1,bb1]],'same_side_info':[0,0],
                    'same_message':[0,0],'status':'COMMON_ROLE_PREMISE_NECESSARY_FOR_THIS_CODE'})
    result={'research_id':'R188-CER-20261009','version':'CER-RESULT-v0.1.0',
            'status':'ALL_CHECKS_PASSED','scope':'exact finite probability and admissible classical protocol models',
            'not_evidence_of':'human/AI experience or physical causal closure',
            'record_count':len(records),'enumerated_candidate_tables':table_count,
            'python':platform.python_version(),'elapsed_seconds':round(time.perf_counter()-started,3),
            'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'records':records}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=Path(__file__).with_name('EXACT_RESULTS.json'))
    run(ap.parse_args().output)
