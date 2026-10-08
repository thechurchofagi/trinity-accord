"""TO20261008: exact small-model checks, not neural data or a C1 test."""
from fractions import Fraction as F
from pathlib import Path
import json

def reference(history, eta=F(1,4), initial=F(0)):
    beta=initial
    for d in history:
        beta=(1-eta)*beta+eta*d
    return beta

def device(delta,beta,s,a,b,er=F(0),eu=F(0)):
    q=delta-a*beta
    return {'q':q,'R':int(q-b*beta+er>0),'U':q/s+eu}

def cycle_sum(beta, cycle):
    return sum(beta[i,j] for i,j in zip(cycle,cycle[1:]))

def serial(x):
    if isinstance(x,F): return {'exact':str(x),'decimal':float(x)}
    if isinstance(x,dict): return {str(k):serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [serial(v) for v in x]
    return x

def run():
    checks=[]
    def check(name,truth,scope):
        assert truth,name
        checks.append({'name':name,'pass':True,'scope':scope})
    beta=reference([F(100)]*8)
    S=device(F(20),beta,F(100),1,0)
    C=device(F(20),beta,F(100),0,1)
    check('closed_form_and_crossing',beta==100*(1-F(3,4)**8) and S['q']<0<C['q'], 'Exact illustrative 8-trial model; P1 is general algebra.')
    reports_equal=True
    for delta in map(F,[-50,0,20,100,150]):
        for bval in map(F,[-30,0,50,100]):
            for er in map(F,[-10,0,10]):
                reports_equal &= device(delta,bval,F(100),1,0,er)['R']==device(delta,bval,F(100),0,1,er)['R']
    check('report_route_equivalence_examples',reports_equal,'Boundary and signed examples only; P2 proves pointwise equivalence for all inputs/noise.')
    check('nonreport_separation',S['R']==C['R'] and S['U']-C['U']==-beta/100,'Fixed ports and common actuator noise; does not measure experience.')
    S_off=device(F(20),beta,F(100),0,0)
    C_off=device(F(20),beta,F(100),0,0)
    check('route_knockout_contrast',S_off['R']!=S['R'] and S_off['U']!=S['U'] and C_off['R']!=C['R'] and C_off['U']==C['U'],'Two distinct stipulated knockouts, not one shared physical intervention.')
    alpha=F(1000000)
    rescaled=device(alpha*20,reference([alpha*100]*8),alpha*100,1,0)
    check('full_retiming_vs_unilateral_latency',rescaled['R']==S['R'] and rescaled['U']==S['U'] and device(F(120),beta,F(100),1,0)['q']>0,'All relevant model time parameters scale; added latency alone breaks sign preservation.')
    r={'A':F(0),'B':F(20),'C':F(40)}
    betas={('A','B'):F(30),('B','C'):F(30),('A','C'):F(0)}
    betas.update({(j,i):-v for (i,j),v in list(betas.items())})
    q={(i,j):r[j]-r[i]-v for (i,j),v in betas.items()}
    check('cyclic_encoding_obstruction',cycle_sum(betas,['A','B','C','A'])==60 and q['A','B']<0 and q['B','C']<0 and q['A','C']>0,'Pairwise comparator countermodel; no experienced-cycle claim.')
    offsets={'A':F(0),'B':F(30),'C':F(60)}
    compatible={(i,j):offsets[j]-offsets[i] for i,j in betas}
    u={i:r[i]-offsets[i] for i in r}
    check('compatible_potential_reconstruction',cycle_sum(compatible,['A','B','C','A'])==0 and all(r[j]-r[i]-v==u[j]-u[i] for (i,j),v in compatible.items()),'One exact compatible instance; general proof is path independence in P4.')
    noncyclic={('A','B'):F(0),('B','C'):F(0),('A','C'):F(1)}
    noncyclic.update({(j,i):-v for (i,j),v in list(noncyclic.items())})
    check('nonzero_cycle_sum_need_not_reverse_signs',cycle_sum(noncyclic,['A','B','C','A'])!=0 and all(r[j]-r[i]-noncyclic[i,j]>0 for i,j in [('A','B'),('B','C'),('A','C')]),'Rejects overclaim that nonadditive offsets always produce a sign cycle.')
    return serial({'status':'EXACT_TOY_MODEL_ONLY','checks':checks,'example':{'beta':beta,'S':S,'C':C,'S_route_off':S_off,'C_threshold_off':C_off},'three_event_q':q,'limits':['No human data or quantitative fit','No actual neural/hardware realization certified','No C1/B_order validation','No global map semantic proof']})

if __name__=='__main__':
    result=run()
    target=Path(__file__).with_name('MODEL_RESULTS.json')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'checks_passed':len(result['checks']),'example':result['example']},ensure_ascii=False))
