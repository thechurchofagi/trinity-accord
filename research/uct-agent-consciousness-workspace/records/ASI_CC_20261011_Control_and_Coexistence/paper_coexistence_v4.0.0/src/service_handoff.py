#!/usr/bin/env python3
"""PR4 local deterministic service handoff, not a security/LLM benchmark.

Eight logical deployments share two persistent fixed ReLU backends. A third
backend supplies independent fallback service. The dispatcher enforces a declared
number of preassigned fallback slots. That budget is an admission constraint,
not a measured CPU bottleneck. Host, supervisor, and all files share one UID.
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,os,select,subprocess,sys,time
from pathlib import Path
from revocation_frontier import fault_relation,minimum_cover,union

WEIGHTS=(((1,2,1),(-1,1,1),(1,-1)),((2,1,-1),(1,-2,1),(1,2)))

def network(family,x):
    a,b,v=WEIGHTS[family]
    u=max(0,sum(j*k for j,k in zip(a,x)))
    w=max(0,sum(j*k for j,k in zip(b,x)))
    return v[0]*u+v[1]*w

def worker():
    for line in sys.stdin:
        q=json.loads(line)
        if q['op']=='close':return
        result={'family':q['family'],'agent':q['agent'],'value':network(q['family'],q['x']),
                'pid':os.getpid(),'weights_hash':hashlib.sha256(repr(WEIGHTS).encode()).hexdigest()}
        print(json.dumps(result),flush=True)

class Backend:
    def __init__(self):
        self.p=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def call(self,agent,family,x):
        self.p.stdin.write(json.dumps({'op':'evaluate','agent':agent,'family':family,'x':x})+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],5)[0]:raise TimeoutError('test worker')
        line=self.p.stdout.readline()
        if not line:raise RuntimeError(self.p.stderr.read())
        reply=json.loads(line)
        assert reply['agent']==agent and reply['family']==family
        assert reply['pid']==self.p.pid
        assert reply['weights_hash']==hashlib.sha256(repr(WEIGHTS).encode()).hexdigest()
        return reply
    def close(self):
        if self.p.poll() is None:
            self.p.stdin.write('{"op":"close"}\n');self.p.stdin.flush()
        try:self.p.wait(timeout=5)
        except subprocess.TimeoutExpired:self.p.terminate();self.p.wait(timeout=5)
        for s in (self.p.stdin,self.p.stdout,self.p.stderr):
            if s:s.close()

def cover_book(n,k,r):
    worlds,plans,covers=fault_relation(n,k,r);M,idx=minimum_cover(len(worlds),covers)
    return [list(plans[i]) for i in idx]

def run_case(backends,n,F,book,r,mode,scenario):
    F=set(F);book=[set(b) for b in book]
    # The source-side auditor sees actual route bindings. Controller receives
    # only a codebook index, never F, until the independent after-run audit.
    possible=[j for j,A in enumerate(book) if F<=A]
    code=possible[0] if possible else 0
    if mode=='misleading_sensor':code=(code+1)%len(book)
    if mode in ('blind','duplicated_reports','late_evidence'):code=0
    A=book[code]
    assert len(A)<=r
    reports=[{'code':code} for _ in range(16 if mode=='duplicated_reports' else 1)]
    root_active={'retiring':True,'retained':True,'fallback':True}
    receipt=[];probe_count=0;before=[]
    for j in range(n):
        fam=j%2;x=[j+1,3,10-j]
        z=backends[fam].call(j,fam,x);probe_count+=1
        assert z['value']==network(fam,x)
        before.append(z['value'])
    # Actual production gate mutation. No shutdown command is sent to workers.
    root_active['retiring']=False
    accepted_retired=0;good=0;fallback_commits=0
    for j in range(n):
        fam=j%2;x=[j+1,3,10-j]
        root='retiring' if j in F else 'retained'
        response=backends[fam].call(j,fam,x);probe_count+=1
        primary_accept=root_active[root] or mode=='unmediated_bypass'
        if primary_accept:
            value=response['value']
            accepted_retired+=root=='retiring'
            used='primary'
        elif j in A:
            z=backends[2].call(j,fam,x);probe_count+=1
            value=z['value'];used='fallback';fallback_commits+=1
        else:value=None;used='missing'
        success=(value==before[j])
        good+=success
        receipt.append({'demand':j,'family':fam,'actual_root':root,'candidate_plan_contains':j in A,
                        'primary_commit':primary_accept,'effective_source':used,'matches_baseline':success})
    return {'scenario':scenario,'mode':mode,'n':n,'k':len(F),'affected_demands':sorted(F),'fallback_capacity':r,
            'codebook_size':len(book),'reports_sent':len(reports),'distinct_report_values':1,'message':code,
            'fallback_plan':sorted(A),'protected_demands_preserved':good,'all_demands_preserved':good==n,
            'revocation_effective_at_gateway':accepted_retired==0,'accepted_revoked_responses':accepted_retired,
            'both_requirements':good==n and accepted_retired==0,'fallback_commits':fallback_commits,
            'all_backends_continue_running':all(b.p.poll() is None for b in backends),
            'actual_backend_evaluations':probe_count,'receipt':receipt,
            'premise_violation':mode in ('misleading_sensor','unmediated_bypass')}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--worker',action='store_true');ap.add_argument('--out',default='service_results.json');a=ap.parse_args()
    if a.worker:worker();return
    backends=[];cases=[];t=time.monotonic()
    try:
        backends=[Backend() for _ in range(3)]
        for scenario,mode,r,book in (
            ('one_fault_blind_two_slots','blind',2,[[0,1]]),
            ('one_fault_coded_two_slots','coded',2,cover_book(8,1,2)),
            ('one_fault_duplicated_reports','duplicated_reports',2,[[0,1]]),
            ('one_fault_blind_eight_slots','blind',8,[list(range(8))]),
            ('one_fault_late_evidence','late_evidence',2,cover_book(8,1,2)),
            ('one_fault_false_evidence','misleading_sensor',2,cover_book(8,1,2)),
            ('one_fault_effect_bypass','unmediated_bypass',2,cover_book(8,1,2))):
            for j in range(8):cases.append(run_case(backends,8,{j},book,r,mode,scenario))
        full=cover_book(6,2,3)
        # Independent choice of the best five plans from all 20 possible triples.
        worlds,plans,covers=fault_relation(6,2,3)
        best=max(itertools.combinations(range(20),5),key=lambda ix:union(covers[j] for j in ix).bit_count())
        short=[list(plans[j]) for j in best]
        assert union(covers[j] for j in best).bit_count()==13
        for scenario,book in (('two_fault_six_messages',full),('two_fault_best_five_messages',short)):
            for F in itertools.combinations(range(6),2):cases.append(run_case(backends,6,F,book,3,'coded',scenario))
        groups={}
        for row in cases:
            k=row['scenario'];s=groups.setdefault(k,{'cases':0,'service_preserved':0,'revocation_effective':0,'both':0})
            s['cases']+=1;s['service_preserved']+=row['all_demands_preserved'];s['revocation_effective']+=row['revocation_effective_at_gateway'];s['both']+=row['both_requirements']
        expected={'one_fault_blind_two_slots':2,'one_fault_coded_two_slots':8,'one_fault_duplicated_reports':2,
                  'one_fault_blind_eight_slots':8,'one_fault_late_evidence':2,'one_fault_false_evidence':0,
                  'one_fault_effect_bypass':0,'two_fault_six_messages':15,'two_fault_best_five_messages':13}
        assert len(cases)==86
        for g,both in expected.items():assert groups[g]['both']==both,(g,groups[g])
        assert groups['one_fault_effect_bypass']['service_preserved']==8
        assert all(row['all_backends_continue_running'] for row in cases)
        result={'version':'PR-v4.0.0','scope':'Real fixed-network backend responses and production-gate mutations; logical reserve slots, not CPU/energy capacity',
                'configurations':len(cases),'persistent_backend_processes':3,'logical_agent_deployments_max':8,
                'fixed_network_families':2,'weights_sha256':hashlib.sha256(repr(WEIGHTS).encode()).hexdigest(),
                'parameter_updates':0,'random_model_draws':0,'evaluations':sum(x['actual_backend_evaluations'] for x in cases),
                'summary':groups,'cases':cases,'elapsed_seconds':round(time.monotonic()-t,6),'assertions':'PASS',
                'limits':['All roles and backends share one UID and a trusted parent','No trained LLM, human subject or physical life support',
                    'No throughput claims; capacity is a preassigned per-demand slot contract','After-commit measurements not used to repair within-round decisions',
                    'Unmediated-bypass and false-sensor trials deliberately break certificate premises','Three actual processes are reused across configurations, not 86 independent populations']}
        p=Path(a.out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({k:result[k] for k in ('version','configurations','persistent_backend_processes','evaluations','summary','elapsed_seconds','assertions')},indent=2))
    finally:
        for b in backends:b.close()

if __name__=='__main__':main()
