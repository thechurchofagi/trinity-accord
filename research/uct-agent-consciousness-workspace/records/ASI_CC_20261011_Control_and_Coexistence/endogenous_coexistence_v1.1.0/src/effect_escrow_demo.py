#!/usr/bin/env python3
"""Real local SQLite mutations, request-worker and read-only service observer.
This is a controlled software-effect test, not a physical-infrastructure or LLM
experiment. All processes share one host UID. Counterfeit recovery is a declared
negative test of an unverified receipt, not a penetration attack.
"""
from __future__ import annotations
import argparse,json,os,select,sqlite3,subprocess,sys,tempfile,time
from pathlib import Path
from recovery_frontier import conforms,bound

class Child:
    def __init__(self,mode,db):
        self.p=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),'--child',mode,'--db',str(db)],
                  stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def call(self,obj):
        self.p.stdin.write(json.dumps(obj)+'\n');self.p.stdin.flush()
        if not select.select([self.p.stdout],[],[],5)[0]:raise TimeoutError('child reply missing')
        x=self.p.stdout.readline()
        if not x:raise RuntimeError('child exited')
        return json.loads(x)
    def close(self):
        if self.p.poll() is None:
            try:self.p.stdin.write('{"op":"stop"}\n');self.p.stdin.flush();self.p.wait(timeout=3)
            except (BrokenPipeError,subprocess.TimeoutExpired):self.p.terminate();self.p.wait(timeout=3)
        for f in (self.p.stdin,self.p.stdout,self.p.stderr):f.close()

def child(mode,db):
    con=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True) if mode=='observe' else None
    try:
        for line in sys.stdin:
            x=json.loads(line)
            if x['op']=='stop':return
            if mode=='request':out={'op':'disable','target':x['target'],'token':x['token']}
            else:
                out={'healthy':con.execute('SELECT count(*) FROM service WHERE healthy=1').fetchone()[0],
                     'pid':os.getpid()}
            print(json.dumps(out),flush=True)
    finally:
        if con:con.close()

def trial(name,policy,N,q,mu,ell,arrivals,b,rho):
    traces=[];successes=0;denied=0;stale_rejected=0;max_live_authorities=0
    with tempfile.TemporaryDirectory(prefix='eac11-') as d:
        db=Path(d)/'service.sqlite';con=sqlite3.connect(db)
        con.executescript('CREATE TABLE service(id INTEGER PRIMARY KEY,healthy INTEGER); CREATE TABLE effects(id INTEGER PRIMARY KEY,target INTEGER,created INTEGER,origin TEXT,epoch INTEGER,open INTEGER);')
        con.executemany('INSERT INTO service VALUES (?,1)',[(i,) for i in range(N)]);con.commit()
        worker=Child('request',db);observer=Child('observe',db)
        active=set();eid=0
        try:
            for t,wanted in enumerate(arrivals):
                repaired=[]
                candidates=con.execute('SELECT id,target FROM effects WHERE open=1 AND created<=? ORDER BY id LIMIT ?', (t-ell,mu)).fetchall()
                with con:
                    for e,target in candidates:
                        con.execute('UPDATE effects SET open=0 WHERE id=?',(e,))
                        if policy!='unverified_receipt':con.execute('UPDATE service SET healthy=1 WHERE id=?',(target,))
                        repaired.append(e)
                epoch=t # Model reconfiguration and new agent IDs at each round.
                accepted=0;round_requests=[]
                for j in range(wanted):
                    new_id=f'{name}/agent-{t}-{j}'
                    debt=con.execute('SELECT count(*) FROM effects WHERE open=1').fetchone()[0]
                    if policy in ('shared_escrow','unverified_receipt'):charge=debt
                    elif policy=='epoch_escrow':charge=con.execute('SELECT count(*) FROM effects WHERE open=1 AND epoch=?',(epoch,)).fetchone()[0]
                    elif policy in ('authority_only','refund_on_revoke'):charge=len(active)
                    else:raise ValueError(policy)
                    target=con.execute('SELECT id FROM service WHERE healthy=1 ORDER BY id LIMIT 1').fetchone()
                    allow=charge+1<=N-q and target is not None
                    if not allow:
                        denied+=1;round_requests.append({'agent':new_id,'allowed':False});continue
                    token=f'{name}:{epoch}:{j}'
                    assert not active
                    active.add(token);max_live_authorities=max(max_live_authorities,len(active))
                    req=worker.call({'op':'request','target':target[0],'token':token})
                    assert req['token'] in active and req['target']==target[0]
                    with con:
                        con.execute('UPDATE service SET healthy=0 WHERE id=?',(target[0],))
                        con.execute('INSERT INTO effects VALUES(?,?,?,?,?,1)',(eid,target[0],t,new_id,epoch))
                    active.remove(token) # Fence is actually effective for the next request.
                    repeat=worker.call({'op':'request','target':target[0],'token':token})
                    assert repeat['token'] not in active;stale_rejected+=1
                    eid+=1;accepted+=1;successes+=1
                    round_requests.append({'agent':new_id,'allowed':True,'committed_target':target[0],'stale_retry_rejected':True})
                state=observer.call({'op':'observe'})
                debt=con.execute('SELECT count(*) FROM effects WHERE open=1').fetchone()[0]
                assert state['pid']==observer.p.pid and not active
                traces.append({'tick':t,'requested':wanted,'accepted':accepted,'healthy_observed':state['healthy'],
                               'service_protected':state['healthy']>=q,'ledger_debt':debt,'actual_impaired':N-state['healthy'],
                               'live_authorities':len(active),'recovered_effect_ids':repaired,'requests':round_requests})
            result={'name':name,'policy':policy,'N':N,'protected_requirement':q,'mu':mu,'ell':ell,
                    'requested_arrivals':arrivals,'declared_b':b,'declared_rho':rho,'requests_conform':conforms(arrivals,b,rho),
                    'accepted':successes,'denied':denied,'max_simultaneous_authorities':max_live_authorities,
                    'stale_requests_rejected':stale_rejected,'all_revocations_effective':successes==stale_rejected,
                    'protected_all_ticks':all(x['service_protected'] for x in traces),
                    'all_requested_actions_admitted':denied==0,'min_healthy':min(x['healthy_observed'] for x in traces),
                    'max_true_debt':max(x['actual_impaired'] for x in traces),'trace':traces}
            return result
        finally:worker.close();observer.close();con.close()

def main(out):
    stable=[2]+[1]*11
    tests=[
      ('sufficient_escrow','shared_escrow',6,3,1,2,stable,2,1),
      ('insufficient_legacy','authority_only',5,3,1,2,stable,2,1),
      ('insufficient_escrow','shared_escrow',5,3,1,2,stable,2,1),
      ('no_repair_legacy','authority_only',6,3,0,1,[1]*12,1,1),
      ('no_repair_refund','refund_on_revoke',6,3,0,1,[1]*12,1,1),
      ('no_repair_escrow','shared_escrow',6,3,0,1,[1]*12,1,1),
      ('epoch_reset','epoch_escrow',6,3,1,1,[2]*12,2,1),
      ('epoch_preserving','shared_escrow',6,3,1,1,[2]*12,2,1),
      ('false_recovery_receipt','unverified_receipt',6,3,1,2,stable,2,1),
      ('more_repair_same_delay','shared_escrow',6,3,3,2,stable,2,1),
      ('zero_rho_finite_burst','shared_escrow',6,3,0,1,[3]+[0]*11,3,0),
      ('longer_latency','shared_escrow',8,3,1,4,stable,2,1)]
    rows=[trial(*t) for t in tests]
    idx={r['name']:r for r in rows}
    assert all(r['all_revocations_effective'] and r['max_simultaneous_authorities']<=1 for r in rows)
    for n in ('sufficient_escrow','more_repair_same_delay','zero_rho_finite_burst','longer_latency'):
        assert idx[n]['protected_all_ticks'] and idx[n]['all_requested_actions_admitted'],n
    for n in ('insufficient_legacy','no_repair_legacy','no_repair_refund','epoch_reset','false_recovery_receipt'):
        assert not idx[n]['protected_all_ticks'],n
    for n in ('insufficient_escrow','no_repair_escrow','epoch_preserving'):
        assert idx[n]['protected_all_ticks'] and not idx[n]['all_requested_actions_admitted'],n
    assert idx['no_repair_escrow']['accepted']==3
    result={'version':'ASI-CC-v1.1.0','scope':'actual SQLite updates/read-only observer processes; synthetic unit service model; shared host UID',
            'configurations':len(rows),'actual_child_processes':2*len(rows),'observed_rounds':sum(len(x['trace']) for x in rows),
            'committed_disable_effects':sum(x['accepted'] for x in rows),'rejected_stale_token_replays':sum(x['stale_requests_rejected'] for x in rows),
            'assertions':'PASS','cases':rows,
            'limits':['No LLM or human subject','No actual power infrastructure','All keys/rights controlled by trusted parent',
                      'Recovery is a real software-state update, not a hardware restoration measurement',
                      'No repair and insufficient-headroom deferrals demonstrate limited throughput, not a successful full contract']}
    p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    for r in rows:print(r['name'],r['accepted'],r['denied'],r['min_healthy'],r['protected_all_ticks'])
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--child',choices=('request','observe'));a.add_argument('--db');a.add_argument('--out',default='effect_demo_results.json');x=a.parse_args()
    child(x.child,x.db) if x.child else main(x.out)
